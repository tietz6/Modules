
from typing import Any, Dict, Optional
from .env import get_env

# Prefer requests if available, else simple urllib fallback
try:
    import requests  # type: ignore
except Exception:
    requests = None

def _timeout():
    return get_env("HTTP_TIMEOUT", 15.0, float)

def _retries():
    return get_env("HTTP_RETRIES", 2, int)

def http_get(url: str, params: Optional[Dict[str,Any]]=None, headers: Optional[Dict[str,str]]=None, timeout: Optional[float]=None):
    t = timeout or _timeout()
    if requests is None:
        # minimal urllib fallback
        from urllib.request import urlopen, Request
        import json as _json
        import urllib.parse as _parse
        q = f"{url}?{_parse.urlencode(params or {})}" if params else url
        req = Request(q, headers=headers or {})
        with urlopen(req, timeout=t) as r:
            data = r.read().decode("utf-8")
            try:
                return _json.loads(data)
            except Exception:
                return {"raw": data}
    last_err = None
    for _ in range(max(1, _retries())):
        try:
            resp = requests.get(url, params=params or {}, headers=headers or {}, timeout=t)
            resp.raise_for_status()
            ct = (resp.headers.get("content-type") or "").lower()
            if "application/json" in ct:
                return resp.json()
            return {"raw": resp.text}
        except Exception as e:
            last_err = str(e)
    raise RuntimeError(last_err or "GET failed")

def http_post(url: str, json: Optional[Dict[str,Any]]=None, data: Optional[Dict[str,Any]]=None, headers: Optional[Dict[str,str]]=None, timeout: Optional[float]=None):
    t = timeout or _timeout()
    if requests is None:
        # minimal urllib fallback
        from urllib.request import urlopen, Request
        import json as _json
        import urllib.parse as _parse
        body = _json.dumps(json).encode("utf-8") if json is not None else _parse.urlencode(data or {}).encode("utf-8")
        hdrs = {"Content-Type":"application/json"} if json is not None else {"Content-Type":"application/x-www-form-urlencoded"}
        hdrs.update(headers or {})
        req = Request(url, data=body, headers=hdrs, method="POST")
        with urlopen(req, timeout=t) as r:
            data = r.read().decode("utf-8")
            try:
                return _json.loads(data)
            except Exception:
                return {"raw": data}
    last_err = None
    for _ in range(max(1, _retries())):
        try:
            resp = requests.post(url, json=json, data=data, headers=headers or {}, timeout=t)
            resp.raise_for_status()
            ct = (resp.headers.get("content-type") or "").lower()
            if "application/json" in ct:
                return resp.json()
            return {"raw": resp.text}
        except Exception as e:
            last_err = str(e)
    raise RuntimeError(last_err or "POST failed")
