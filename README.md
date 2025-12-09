# Authentication Proxy (FastAPI)

Simple FastAPI service that proxies requests from your React app to a backend while adding an `X-Security-Key` header. CORS is fully open to allow local development.

## Quick start

1) Install deps
```bash
pip install -r requirements.txt
```

2) Configure environment
```bash
export BACKEND_URL="https://your-backend-service.com"
export SECURITY_HEADER_VALUE="your-secret-key"
```

3) Run the proxy
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4) Point your React app at the proxy (e.g., `http://localhost:8000/api/...`). Every request is forwarded to `BACKEND_URL` with the same path/query/body and with `X-Security-Key` injected.

## Notes
- All CORS origins/methods/headers are allowed.
- Supported HTTP methods: GET, POST, PUT, PATCH, DELETE, OPTIONS.
- Hop-by-hop headers are stripped when forwarding.