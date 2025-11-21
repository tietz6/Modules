
import os

def get_env(key: str, default=None, cast=str):
    val = os.environ.get(key, None)
    if val is None:
        return default
    try:
        if cast is bool:
            return val.lower() in ("1","true","yes","on")
        if cast is int:
            return int(val)
        if cast is float:
            return float(val)
        return cast(val)
    except Exception:
        return default
