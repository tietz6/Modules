
# patch_v4 public interface
from .http_client import http_get, http_post
from .env import get_env
try:
    from .routes import router  # optional, if present
except Exception:
    router = None
