from fastapi import FastAPI
from pathlib import Path
from api.core.registry import ModuleRegistry
from api.core.module_loader import load_all_modules

app = FastAPI(title="SalesBot CORE", version="0.1" )
registry = ModuleRegistry()

@app.get("/health")
def health():
    return {"ok": True, "msg": "core alive"}

@app.on_event("startup")
def startup_event():
    modules_path = Path(__file__).parent / "modules"
    load_all_modules(registry, modules_path)
    print(f"[core] Loaded modules: {list(registry.all().keys())}")

@app.get("/")
def root():
    return {
        "status": "running",
        "loaded_modules": list(registry.all().keys())
    }
