
upsell/v3 — advanced upsell trainer
----------------------------------
Функции:
  - DeepSeek сценарии допродаж
  - Режимы: soft, normal, aggressive
  - Пакеты: Basic, Premium, Gold
  - Авто-оценка аргументации
  - История диалога + персонажи
  - Интеграция с products.bundle

Роуты:
  POST /upsell/v3/start/{sid}
  POST /upsell/v3/handle/{sid}
  GET  /upsell/v3/snapshot/{sid}
