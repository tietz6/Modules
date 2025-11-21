from fastapi import FastAPI
import importlib
ROUTE_MODULES = [
    # Публичные API
    "api.public.v1.routes",
    "api.admin.v1.routes",
    "api.voice.v1.routes",

    # Основные модули тренажёра
    "modules.master_path.v3.routes",
    "modules.objections.v3.routes",
    "modules.upsell.v3.routes",
    "modules.arena.v4.routes",
    "modules.sleeping_dragon.v4.routes",
    "modules.exam_autocheck.v2.routes",
    "modules.payments.v2.routes",

    # Trainer-пакет (новые модули)
    "modules.trainer_core.v1.routes",
    "modules.trainer_scenarios.v1.routes",
    "modules.trainer_dialog_engine.v1.routes",
    "modules.trainer_arena_pro.v1.routes",
    "modules.trainer_upsell_master.v1.routes",
    "modules.trainer_story_collection.v1.routes",
    "modules.trainer_exam.v1.routes",

    # Доп-модули
    "modules.voice_arena.v1.routes",
    "modules.dialog_memory.v1.routes",
    "modules.edu_lessons.v1.routes",
    "modules.client_cases.v1.routes",
    "modules.sales_commission.v1.routes",
    "modules.errors_manager.v1.routes",

    # Приложения и интеграции
    "apps.mini_webkit.v3.routes",
    "apps.public_miniapp.v1.routes",
    "apps.dashboard_manager.v1.routes",
    "apps.mini_webkit.brand.v1.router",

    "bridges.crm_api_bridge.v4.routes",
    "bridges.crm_sync.v1.routes",
    "bridges.crm_leads_bridge.v2.routes",

    "integrations.patch_v4.routes",
    "integrations.telegram_push.v1.routes",
    "integrations.telegram_bot.v1.routes",
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
