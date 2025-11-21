import importlib
from pathlib import Path
from .registry import ModuleRegistry

def _iter_versions(module_dir: Path):
    # priority: _current -> latest v*
    current = module_dir / "_current"
    if current.is_dir():
        yield "_current", current
        return
    vers = []
    for d in module_dir.iterdir():
        if d.is_dir() and d.name.startswith("v"):
            try:
                vers.append((int(d.name.lstrip("v")), d))
            except ValueError:
                pass
    vers.sort(key=lambda t: t[0])
    for num, d in vers:
        yield d.name, d

def load_all_modules(registry: ModuleRegistry, modules_base_path: Path):
    """
    Auto-loader:
        - scans api/modules/*
        - prefers _current if exists, else latest v*
        - loads engine.py + routes.py
        - registers module instance
    """
    if not modules_base_path.exists():
        print(f"[loader] Path not found: {modules_base_path}")
        return

    print(f"[loader] Scanning modules in: {modules_base_path}")

    for module_dir in modules_base_path.iterdir():
        if not module_dir.is_dir():
            continue

        module_name = module_dir.name

        versions = list(_iter_versions(module_dir))
        if not versions:
            print(f"[loader] No versions found inside {module_name}")
            continue

        version, version_dir = versions[0]
        print(f"[loader] Loading module: {module_name} (version: {version})")

        try:
            engine_mod = importlib.import_module(
                f"api.modules.{module_name}.{version}.engine"
            )
            routes_mod = importlib.import_module(
                f"api.modules.{module_name}.{version}.routes"
            )

            instance = None
            if hasattr(engine_mod, "Module"):
                instance = engine_mod.Module()
                registry.register(module_name, instance)

            if hasattr(routes_mod, "register_routes"):
                routes_mod.register_routes(instance)

        except Exception as e:
            print(f"[loader] ERROR loading {module_name}: {e}")
