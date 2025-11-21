
arena/v4 — advanced client arena
--------------------------------
Функции:
  - 20 типов клиентов
  - 5 эмоций и эмоциональные переходы
  - уровни сложности (L1 / L2 / L3)
  - персональные цели (client goals)
  - DeepSeek реакция клиента
  - динамическая сложность: клиент "учится"
  - сохранение истории и контекста

Routes:
  POST /arena/v4/start/{sid}
  POST /arena/v4/handle/{sid}
  GET  /arena/v4/snapshot/{sid}
