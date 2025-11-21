# Memory Engine (PART J)
- Формат сессии: `memory/schema/session.json`
- Формат сообщения: `memory/schema/message.json`
- Конфиг: `memory/config.json` (kv_prefix, retention_days, max_history)
- Пример: `memory/examples/session_example.json`

### Контракты чтения/записи (без кода)
- write(session) → сохраняется как kv: `sd:mem:{manager_id}:{session_id}`
- read(manager_id, session_id) → возвращает JSON сессии
- list(manager_id, limit=50) → список ключей по префиксу
