# Sleeping Dragon — LAUNCH KIT v1

Этот пакет завершает сборку и готовит проект к запуску.

## Что внутри
- .env.example — переменные окружения
- manifests/parts_required.json — обязательные модули перед стартом
- scripts/run_local.sh — локальный запуск (uvicorn)
- scripts/smoke.sh — базовые проверки curl
- tools/autobuilder_instructions.md — как прогнать автосборщик
- checks/checklist.md — финальная чек‑листа перед стартом
- api/postman_collection.json — коллекция для быстрой проверки API
- data/seed/* — минимальные данные (персоны, рубрики, пресеты)
- README_ROUTES.md — куда стучаться после старта

## Шаги запуска
1) Скопируй содержимое в корень проекта.
2) Заполни .env на основе .env.example.
3) Убедись, что все модули из manifests/parts_required.json установлены.
4) Прогони автосборщик (см. tools/autobuilder_instructions.md).
5) Запусти `scripts/run_local.sh`.
6) Выполни `scripts/smoke.sh` — все запросы должны вернуть 200.
7) Открой /mini/brand/hub — визуальная проверка.
