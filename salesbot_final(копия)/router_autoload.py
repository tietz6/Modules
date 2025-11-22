from fastapi import FastAPI
import importlib
ROUTE_MODULES = [
    # Публичные API
    "api.public.v1.routes",
    "api.admin.v1.routes",
    "api.voice.v1.routes",

    # Основные модули тренажёра (все работают)
    "modules.master_path.v3.routes",
    "modules.objections.v3.routes",
    "modules.upsell.v3.routes",
    "modules.arena.v4.routes",
    "modules.sleeping_dragon.v1.routes",
]
def include_all(app: FastAPI)->None:
    attached = []
    errors = []
    for m in ROUTE_MODULES:
        try:
            mod = importlib.import_module(m)
            router = getattr(mod, "router", None)
            if router is None:
                continue
            app.include_router(router)
            attached.append(m)
        except Exception as e:
            errors.append((m, str(e)))

    @app.get("/api/public/v1/routes_summary")
    async def routes_summary():
        return {"attached": attached, "errors": errors}
