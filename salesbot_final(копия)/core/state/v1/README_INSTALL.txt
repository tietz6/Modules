
core/state/v1 — SQLite KV storage (StateStore)
----------------------------------------------
Возможности:
  - Автосоздание БД (salesbot.db по умолчанию)
  - Методы: get(key), set(key, value), delete(key), scan(prefix, limit)
  - Потокобезопасность (check_same_thread=False)
  - Простые TTL (опционально) — через метку ts (пока без автоочистки)
  - Транзакции с автоматическим повтором при busy

Использование:
  from core.state.v1 import StateStore
  kv = StateStore("salesbot.db")
  kv.set("user:1", "{...}")
  s = kv.get("user:1")
  kv.delete("user:1")
  items = kv.scan("user:", limit=100)
