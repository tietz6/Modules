from typing import Dict, Any

class ModuleRegistry:
    """Global registry of all loaded modules.
    Provides: module name -> module instance
    """
    def __init__(self):
        self.modules: Dict[str, Any] = {}

    def register(self, name: str, module_instance: Any):
        """Register a module instance."""
        self.modules[name] = module_instance
        print(f"[registry] Loaded module: {name}")

    def get(self, name: str):
        """Retrieve module instance by name."""
        return self.modules.get(name)

    def all(self):
        """Return dict of all registered modules."""
        return self.modules
