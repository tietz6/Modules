#!/usr/bin/env python3
"""
Тест структуры модулей бота.
Проверяет что все модули правильно импортируются.
"""

import sys
import importlib


def test_module_import(module_name):
    """Проверка импорта модуля"""
    try:
        mod = importlib.import_module(f"modules.{module_name}")
        print(f"✅ {module_name}: импорт успешен")
        
        # Проверка наличия register_telegram
        if hasattr(mod, 'register_telegram'):
            print(f"   ✓ register_telegram найдена")
        else:
            print(f"   ⚠️  register_telegram не найдена")
        
        return True
    except Exception as e:
        print(f"❌ {module_name}: ошибка импорта - {e}")
        return False


def test_tietz_prompts():
    """Проверка модуля промптов Tietz"""
    try:
        from modules.tietz_prompts import get_base_prompt, BASE_TIETZ_PERSONA
        prompt = get_base_prompt()
        
        # Проверяем ключевые элементы
        assert "Tietz" in prompt
        assert "На Счастье" in prompt
        assert "персональные песни" in prompt.lower()
        
        print("✅ tietz_prompts: все проверки пройдены")
        return True
    except Exception as e:
        print(f"❌ tietz_prompts: ошибка - {e}")
        return False


def test_sleeping_dragon_engine():
    """Проверка движка Спящего Дракона"""
    try:
        from modules.sleeping_dragon.v1.engine import SleepingDragonEngine, SCENARIOS, CLIENT_BEHAVIORS
        
        # Проверяем что сценарии и поведения определены
        assert len(SCENARIOS) > 0
        assert len(CLIENT_BEHAVIORS) > 0
        
        print(f"✅ sleeping_dragon.engine: {len(SCENARIOS)} сценариев, {len(CLIENT_BEHAVIORS)} типов клиентов")
        return True
    except Exception as e:
        print(f"❌ sleeping_dragon.engine: ошибка - {e}")
        return False


def main():
    """Главная функция тестирования"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ СТРУКТУРЫ МОДУЛЕЙ БОТА")
    print("=" * 60)
    print()
    
    modules_to_test = [
        "main_menu",
        "master_path",
        "objections",
        "upsell",
        "sleeping_dragon",
        "arena",
        "deepseek_persona"
    ]
    
    results = []
    
    print("1. Тестирование импорта модулей:")
    print("-" * 60)
    for module_name in modules_to_test:
        result = test_module_import(module_name)
        results.append(result)
        print()
    
    print("2. Тестирование промптов Tietz:")
    print("-" * 60)
    result = test_tietz_prompts()
    results.append(result)
    print()
    
    print("3. Тестирование движка Спящий Дракон:")
    print("-" * 60)
    result = test_sleeping_dragon_engine()
    results.append(result)
    print()
    
    print("=" * 60)
    print(f"РЕЗУЛЬТАТЫ: {sum(results)}/{len(results)} тестов пройдено")
    print("=" * 60)
    
    if all(results):
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
        return 0
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        return 1


if __name__ == "__main__":
    sys.exit(main())
