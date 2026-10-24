import os
from app.main import app as _fastapi_app

# Ensure Vercel environment flag is present
os.environ.setdefault("VERCEL", "1")

class VercelPathFixMiddleware:
    """Fix ASGI scope path when Vercel rewrites route to /api/index.py.
    Vercel sends the client's originally requested URL in headers such as
    x-matched-path or x-forwarded-uri or x-real-ip.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            orig = (
                headers.get(b"x-matched-path") or
                headers.get(b"x-forwarded-uri") or
                headers.get(b"x-original-uri")
            )
            current_path = scope.get("path", "")
            if orig and current_path in ("/api/index.py", "/api/index", "/api/index/"):
                orig_str = orig.decode("utf-8")
                # Remove query string if present in matched header
                scope["path"] = orig_str.split("?")[0]
        await self.app(scope, receive, send)

app = VercelPathFixMiddleware(_fastapi_app)
