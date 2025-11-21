
sleeping_dragon/v4 — real‑time mistake detector
----------------------------------------------
Функции:
  - DeepSeek анализ ошибок менеджера
  - 40 типов ошибок (тон, вопросы, структура, давление, неуверенность)
  - подсказки + рекомендации
  - предупреждения: low, medium, high
  - интеграция с master_path, arena, objections
  - сохранение истории для отчётов

Роуты:
  POST /sleeping_dragon/v4/start/{sid}
  POST /sleeping_dragon/v4/handle/{sid}
  GET  /sleeping_dragon/v4/snapshot/{sid}
