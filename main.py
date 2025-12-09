import os
import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Configure via environment variables so the same code can be used across envs.
BACKEND_URL = os.getenv("BACKEND_URL", "dfdf")
SECURITY_HEADER_VALUE = os.getenv("SECURITY_HEADER_VALUE", "change-me")

app = FastAPI(title="Authentication Proxy")

# Allow all origins/methods/headers so the React app can call this proxy freely.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(full_path: str, request: Request) -> Response:
    """Proxy every request to the configured backend, adding a security header."""
    target_url = f"{BACKEND_URL.rstrip('/')}/{full_path}"

    try:
        body = await request.body()
    except Exception as exc:  # pragma: no cover - FastAPI handles body parsing
        raise HTTPException(status_code=400, detail="Failed to read request body") from exc

    # Copy incoming headers while dropping hop-by-hop ones.
    hop_by_hop = {"host", "content-length", "content-encoding", "connection", "transfer-encoding"}
    headers = {k: v for k, v in request.headers.items() if k.lower() not in hop_by_hop}

    # Add required security header expected by the upstream service.
    headers["X-Security-Key"] = SECURITY_HEADER_VALUE

    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        try:
            upstream_response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body or None,
                params=request.query_params,
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error contacting backend: {exc}") from exc

    # Filter hop-by-hop response headers that should not be forwarded.
    excluded = {"content-encoding", "transfer-encoding", "connection", "keep-alive"}
    response_headers = {k: v for k, v in upstream_response.headers.items() if k.lower() not in excluded}

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
    )

