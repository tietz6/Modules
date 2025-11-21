# Автосборка
1) Проверь, что все ZIP‑пакеты распакованы по своим путям (см. manifests/parts_required.json).
2) Запусти: POST /autobuilder/run  (или python -m autobuilder.apply_all, если доступно).
3) После автосборки появится core/router/registry.json с актуальными маршрутами.
4) Перезапусти приложение — роуты подключатся автоматически.
