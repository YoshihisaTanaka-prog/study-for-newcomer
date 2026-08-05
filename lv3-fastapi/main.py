import os
from collections.abc import Mapping
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates


LV2_ORIGIN = os.getenv("LV2_ORIGIN", "http://127.0.0.1:3000").rstrip("/")
LV1_DIST_DIR = Path(os.getenv("LV1_DIST_DIR", "/workspaces/lv1-vue/dist"))
TEMPLATES_DIR = Path(__file__).parent / "templates"
GITHUB_BASE_URL = "https://github.com/YoshihisaTanaka-prog/study-for-newcomer/tree/main"
LEVEL_FOLDERS = {
    1: "lv1-vue",
    2: "lv2-rails",
    3: "lv3-fastapi",
}

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}

app = FastAPI(title="Study for Newcomer Lv3 Proxy")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/")
async def root() -> Response:
    return template_file("index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.api_route(
    "/lv-1/example",
    methods=["GET", "HEAD", "OPTIONS"],
)
@app.api_route(
    "/lv-1/example/{path:path}",
    methods=["GET", "HEAD", "OPTIONS"],
)
async def serve_lv1(path: str = "") -> Response:
    return serve_static_file(LV1_DIST_DIR, path)


@app.api_route(
    "/lv-2/example",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
)
@app.api_route(
    "/lv-2/example/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
)
async def proxy_lv2(request: Request, path: str = "") -> Response:
    prefix = request.url.path.removesuffix(path).rstrip("/")
    return await proxy_request(request, LV2_ORIGIN, path, prefix=prefix)


@app.get("/lv-{level:int}")
async def level_contents(request: Request, level: int) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="contents.html",
        context={
            "article_url": f"/lv-{level}/article",
            "example_url": f"/lv-{level}/example",
            "github_url": build_github_url(level),
        },
    )


@app.get("/lv-{level:int}/article")
async def level_article(level: int) -> Response:
    return template_file(f"article/lv{level}.html")


async def proxy_request(request: Request, origin: str, path: str, prefix: str) -> Response:
    upstream_url = build_upstream_url(origin, path, request.url.query)
    headers = build_forward_headers(request.headers, prefix)
    body = await request.body()

    try:
        async with httpx.AsyncClient(http2=True, follow_redirects=False, timeout=30.0) as client:
            upstream_response = await client.request(
                request.method,
                upstream_url,
                content=body,
                headers=headers,
            )
    except httpx.HTTPError as error:
        return JSONResponse(
            status_code=502,
            content={
                "error": "upstream_unavailable",
                "detail": str(error),
                "upstream": origin,
            },
        )

    response_content = upstream_response.content
    response_headers = build_response_headers(upstream_response.headers, prefix)
    content_type = upstream_response.headers.get("content-type", "")

    if content_type.startswith("text/html"):
        response_content = rewrite_html_paths(response_content, prefix)
        response_headers.pop("content-length", None)

    return Response(
        content=response_content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=content_type,
    )


def build_upstream_url(origin: str, path: str, query: str) -> str:
    normalized_path = f"/{path}" if path else "/"
    url = f"{origin}{normalized_path}"

    if query:
        return f"{url}?{query}"

    return url


def serve_static_file(root_dir: Path, path: str) -> Response:
    if not root_dir.exists():
        return JSONResponse(
            status_code=503,
            content={
                "error": "lv1_dist_not_found",
                "detail": f"Build Lv1 first. Missing directory: {root_dir}",
            },
        )

    requested_path = (root_dir / path).resolve()
    root_path = root_dir.resolve()

    if not is_relative_to(requested_path, root_path):
        return JSONResponse(status_code=404, content={"error": "not_found"})

    if requested_path.is_dir():
        requested_path = requested_path / "index.html"

    if requested_path.is_file():
        return FileResponse(requested_path)

    fallback_path = root_path / "index.html"

    if fallback_path.is_file():
        return FileResponse(fallback_path)

    return JSONResponse(status_code=404, content={"error": "not_found"})


def template_file(path: str) -> Response:
    requested_path = (TEMPLATES_DIR / path).resolve()

    if not is_relative_to(requested_path, TEMPLATES_DIR.resolve()):
        return JSONResponse(status_code=404, content={"error": "not_found"})

    if requested_path.is_file():
        return FileResponse(requested_path)

    return JSONResponse(status_code=404, content={"error": "not_found"})


def build_github_url(level: int) -> str:
    folder_name = LEVEL_FOLDERS.get(level, f"lv{level}")
    return f"{GITHUB_BASE_URL}/{folder_name}"


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def build_forward_headers(headers: Mapping[str, str], prefix: str) -> dict[str, str]:
    forwarded_headers = {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() != "host"
    }
    forwarded_headers["x-forwarded-prefix"] = prefix
    return forwarded_headers


def build_response_headers(headers: Mapping[str, str], prefix: str) -> dict[str, str]:
    response_headers = {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    location = response_headers.get("location")

    if location and location.startswith("/") and not location.startswith(prefix):
        response_headers["location"] = f"{prefix}{location}"

    return response_headers


def rewrite_html_paths(content: bytes, prefix: str) -> bytes:
    html = content.decode("utf-8", errors="ignore")
    html = html.replace('href="/', f'href="{prefix}/')
    html = html.replace('src="/', f'src="{prefix}/')
    html = html.replace('action="/', f'action="{prefix}/')
    return html.encode("utf-8")
