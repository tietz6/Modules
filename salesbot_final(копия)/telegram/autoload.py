from importlib import import_module
import pkgutil
from typing import Optional
from api.core.registry import ModuleRegistry

# Библиотека: aiogram (v2) — используем Dispatcher интерфейс
from aiogram.dispatcher import Dispatcher


def autoload_telegram_handlers(dp: Dispatcher, registry: ModuleRegistry, package_name: str = "modules"):
    """
    Импортирует подмодули из package_name (обычно 'modules') и вызывает
    register_telegram(dp, registry) если функция присутствует.
    Ожидает, что package_name — импортируемый пакет (modules/__init__.py).
    """
    try:
        pkg = import_module(package_name)
    except Exception as e:
        print(f"[tg_autoload] Cannot import package {package_name}: {e}")
        return

    if not hasattr(pkg, "__path__"):
        print(f"[tg_autoload] Package {package_name} has no __path__")
        return

    for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
        full_name = f"{package_name}.{name}"
        try:
            mod = import_module(full_name)
        except Exception as e:
            print(f"[tg_autoload] Failed to import {full_name}: {e}")
            continue

        reg_fn = getattr(mod, "register_telegram", None)
        if callable(reg_fn):
            try:
                reg_fn(dp, registry)
                print(f"[tg_autoload] Registered telegram handlers for {full_name}")
            except Exception as e:
                print(f"[tg_autoload] register_telegram() failed for {full_name}: {e}")
        else:
            print(f"[tg_autoload] No register_telegram in {full_name}; skipping")