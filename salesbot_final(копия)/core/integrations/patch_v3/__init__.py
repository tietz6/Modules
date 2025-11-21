
# Backward compatibility shim for legacy imports
from integrations.patch_v4.http_client import http_get, http_post
from integrations.patch_v4.env import get_env
try:
    from integrations.patch_v4.routes import router  # type: ignore
except Exception:
    router = None
