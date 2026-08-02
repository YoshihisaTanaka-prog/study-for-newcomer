# Lv3 FastAPI Proxy

Lv1 と Lv2 を同じ入口から扱うための FastAPI プロキシです。

## 起動

```bash
cd /workspaces/lv3-fastapi
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

別ターミナルで Lv1 / Lv2 も起動してください。

```bash
cd /workspaces/lv1-vue
npm run build
```

```bash
cd /workspaces/lv2-rails
bin/rails s -b 0.0.0.0
```

## ルーティング

| Lv3 URL | 転送先 |
|---|---|
| `/lv-1/example/*` | `/workspaces/lv1-vue/dist` の静的ファイル |
| `/lv-2/example/*` | `http://127.0.0.1:3000/*` |

例:

```text
/lv-1/example/
  -> /workspaces/lv1-vue/dist/index.html

/lv-1/example/no-daily
  -> /workspaces/lv1-vue/dist/no-daily/index.html

/lv-2/example/restaurants.json
  -> http://127.0.0.1:3000/restaurants.json
```

## 転送先を変える場合

環境変数で変更できます。

```bash
LV1_DIST_DIR=/workspaces/lv1-vue/dist
LV2_ORIGIN=http://127.0.0.1:3000
```
