import os
import re
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

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


@app.get("/favicon.ico")
async def favicon() -> Response:
    return template_file("favicon.ico")


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
    path = strip_duplicate_prefix(path, prefix)
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
    headers = build_forward_headers(request, prefix)
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
    response_headers = build_response_headers(upstream_response.headers, prefix, request)
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


def strip_duplicate_prefix(path: str, prefix: str) -> str:
    duplicated_prefix = prefix.strip("/")

    if path == duplicated_prefix:
        return ""

    if path.startswith(f"{duplicated_prefix}/"):
        return path.removeprefix(f"{duplicated_prefix}/")

    return path


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


def build_forward_headers(request: Request, prefix: str) -> dict[str, str]:
    forwarded_host = request.headers.get("x-forwarded-host") or request.headers.get("host", request.url.netloc)
    forwarded_proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    forwarded_port = request.headers.get("x-forwarded-port")

    forwarded_headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() != "host"
    }
    forwarded_headers["x-forwarded-prefix"] = prefix
    forwarded_headers["x-forwarded-host"] = forwarded_host
    forwarded_headers["x-forwarded-proto"] = forwarded_proto

    if forwarded_port:
        forwarded_headers["x-forwarded-port"] = forwarded_port
    elif request.url.port:
        forwarded_headers["x-forwarded-port"] = str(request.url.port)

    return forwarded_headers


def build_response_headers(
    headers: Mapping[str, str],
    prefix: str,
    request: Request,
) -> dict[str, str]:
    response_headers = {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    location = response_headers.get("location")

    if location:
        response_headers["location"] = rewrite_location_header(location, prefix, request)

    return response_headers


def rewrite_location_header(location: str, prefix: str, request: Request) -> str:
    prefix_path = prefix.rstrip("/")

    if location.startswith(prefix_path):
        return location

    if location.startswith("/"):
        return f"{prefix_path}{location}"

    parsed_location = urlsplit(location)

    if not parsed_location.scheme or not parsed_location.netloc:
        return location

    if parsed_location.netloc != request.url.netloc:
        return location

    if parsed_location.path == prefix_path or parsed_location.path.startswith(f"{prefix_path}/"):
        return urlunsplit(("", "", parsed_location.path, parsed_location.query, parsed_location.fragment))

    rewritten_path = f"{prefix_path}{parsed_location.path}"
    return urlunsplit(("", "", rewritten_path, parsed_location.query, parsed_location.fragment))


def rewrite_html_paths(content: bytes, prefix: str) -> bytes:
    html = content.decode("utf-8", errors="ignore")
    prefix_path = prefix.rstrip("/")

    def replace_attribute(match: re.Match[str]) -> str:
        attr, quote, path = match.groups()

        if path == prefix_path or path.startswith(f"{prefix_path}/"):
            return match.group(0)

        return f'{attr}={quote}{prefix_path}{path}{quote}'

    html = re.sub(r'\b(href|src|action)=(["\'])(/[^"\']*)\2', replace_attribute, html)
    html = html.replace(f"{prefix_path}{prefix_path}/", f"{prefix_path}/")
    return html.encode("utf-8")
