
import sqlite3
from pathlib import Path

class DB:
    def __init__(self, file: str|None=None):
        self.file = file or "salesbot.db"
        self.path = Path(self.file)
        self._ensure()

    def _ensure(self):
        if not self.path.exists():
            conn = sqlite3.connect(self.file)
            conn.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)")
            conn.commit()
            conn.close()

    def set(self, key: str, value: str):
        conn = sqlite3.connect(self.file)
        conn.execute("REPLACE INTO kv (k,v) VALUES (?,?)",(key,value))
        conn.commit()
        conn.close()

    def get(self, key: str):
        conn = sqlite3.connect(self.file)
        cur = conn.execute("SELECT v FROM kv WHERE k=?",(key,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
