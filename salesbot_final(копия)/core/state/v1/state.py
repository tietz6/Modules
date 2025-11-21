
import json
import os
from pathlib import Path

class StateManager:
    def __init__(self, path: str|None=None):
        self.path = Path(path or "state.json")
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def load(self)->dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save(self, data: dict):
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
