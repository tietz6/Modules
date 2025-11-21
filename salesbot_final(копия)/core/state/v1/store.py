
import sqlite3, time, threading
from typing import List, Tuple, Optional

_SCHEMA = '''
CREATE TABLE IF NOT EXISTS kv (
  key TEXT PRIMARY KEY,
  value TEXT,
  ts REAL
);
CREATE INDEX IF NOT EXISTS kv_ts_idx ON kv(ts);
'''

class StateStore:
    def __init__(self, path: str = "salesbot.db"):
        self.path = path
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._init_db()

    def _init_db(self):
        with self._lock:
            cur = self._conn.cursor()
            for stmt in _SCHEMA.strip().split(';'):
                s = stmt.strip()
                if s:
                    cur.execute(s)
            cur.close()

    def _exec(self, sql: str, args: tuple=()):
        # simple retry for SQLITE_BUSY
        backoff = 0.01
        for _ in range(5):
            try:
                with self._lock:
                    cur = self._conn.cursor()
                    cur.execute(sql, args)
                    self._conn.commit()
                    return cur
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower():
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                raise
        raise RuntimeError("SQLite busy, retries exceeded")

    def get(self, key: str) -> Optional[str]:
        cur = self._exec("SELECT value FROM kv WHERE key = ?", (key,))
        row = cur.fetchone()
        cur.close()
        return row[0] if row else None

    def set(self, key: str, value: str) -> None:
        ts = time.time()
        self._exec("REPLACE INTO kv(key, value, ts) VALUES(?,?,?)", (key, value, ts))

    def delete(self, key: str) -> int:
        cur = self._exec("DELETE FROM kv WHERE key = ?", (key,))
        n = cur.rowcount or 0
        cur.close()
        return n

    def scan(self, prefix: str, limit: int = 100) -> List[Tuple[str,str]]:
        cur = self._exec("SELECT key, value FROM kv WHERE key LIKE ? ORDER BY key LIMIT ?", (prefix + "%", limit))
        rows = cur.fetchall()
        cur.close()
        return [(k,v) for k,v in rows]

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass
