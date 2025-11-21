SalesBot CORE API (minimum skeleton)
====================================

What is this?
-------------
This is a minimal FastAPI core for your project. It discovers modules under:
  api/modules/<module_name>/<version>/routes.py

Two integration options per module:
  1) Provide `router = APIRouter()` in routes.py (recommended)
     -> auto-mounted to /api/<module>/<version>
  2) Provide `def register(app: FastAPI, prefix: str): ...` to add routes manually

How to run (from project root with Python 3.10+):
  uvicorn api.main:app --host 127.0.0.1 --port 8080 --reload

Health:
  http://127.0.0.1:8080/api/public/v1/health

Example module endpoint:
  http://127.0.0.1:8080/api/example/v1/ping
