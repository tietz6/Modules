
objections/v3 — advanced objection simulator
--------------------------------------------
10 типов возражений:
  - price, trust, hurry, think, ask_spouse,
    scam_fear, too_expensive, not_needed,
    later, competitor

Функции:
  - DeepSeek моделирование клиента
  - тип возражения определяется автоматически
  - state + история диалога
  - scoring (качество ответа)
  - персонажи (stranger, calm, aggressive, funny)

Routes:
  POST /objections/v3/start/{sid}
  POST /objections/v3/handle/{sid}
  GET  /objections/v3/snapshot/{sid}
