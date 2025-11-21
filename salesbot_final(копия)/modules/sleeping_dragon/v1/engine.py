"""
Модуль "Спящий Дракон" 🐉 - Работа с неактивными клиентами
Обучает продажников возвращать клиентов через 3 волны сообщений
"""

import json
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from core.state.v1 import StateStore
from core.voice_gateway.v1 import VoicePipeline

# Ситуации для тренировки
SCENARIOS = [
    "after_texts",      # После отправки текстов песни
    "after_demo",       # После демо
    "before_payment",   # До оплаты
    "after_discussion", # После обсуждения акции
    "after_genre",      # После выбора жанра
    "no_response",      # Вообще не ответил
]

# Типы поведения клиента
CLIENT_BEHAVIORS = [
    "busy",            # Занят, но доброжелателен
    "cold",            # Холоден, не интересуется
    "doubtful",        # Сомневается
    "price_sensitive", # Чувствителен к цене
    "emotional",       # Эмоциональный, но нерешительный
    "interested",      # Интересуется, но забыл
]


@dataclass
class SleepingDragonState:
    """Состояние модуля Спящий Дракон"""
    scenario: str           # Ситуация (когда клиент замолчал)
    behavior: str           # Тип поведения клиента
    wave: int               # Текущая волна (1, 2, 3)
    history: List[Dict]     # История диалога
    feedback: List[str]     # Обратная связь по волнам
    meta: Dict[str, Any]    # Метаданные
    
    def to_dict(self):
        return asdict(self)


class SleepingDragonEngine:
    """
    Движок модуля Спящий Дракон.
    Симулирует неактивного клиента и даёт обратную связь.
    """
    
    def __init__(self, sid: str):
        self.sid = f"sleeping_dragon:{sid}"
        self.store = StateStore("salesbot.db")
        raw = self.store.get(self.sid)
        
        if raw:
            try:
                d = json.loads(raw)
                self.state = SleepingDragonState(**d)
            except:
                self._reset()
        else:
            self._reset()
        
        # Подключение к DeepSeek (Tietz)
        try:
            self.llm = VoicePipeline().llm
        except:
            self.llm = None
    
    def _reset(self):
        """Создать новую тренировку"""
        self.state = SleepingDragonState(
            scenario=random.choice(SCENARIOS),
            behavior=random.choice(CLIENT_BEHAVIORS),
            wave=1,
            history=[],
            feedback=[],
            meta={"responses": 0}
        )
        self._save()
    
    def reset(self):
        """Публичный метод сброса"""
        self._reset()
        return {"status": "reset", "scenario": self.state.scenario}
    
    def _save(self):
        """Сохранить состояние"""
        self.store.set(self.sid, json.dumps(self.state.to_dict(), ensure_ascii=False))
    
    def snapshot(self):
        """Получить текущее состояние"""
        return self.state.to_dict()
    
    def _get_scenario_description(self) -> str:
        """Получить описание ситуации"""
        scenarios_ru = {
            "after_texts": "Клиент получил тексты песни, но не ответил",
            "after_demo": "Клиент прослушал демо, но замолчал",
            "before_payment": "Клиент обсуждал оплату, но пропал",
            "after_discussion": "Клиент обсуждал акцию 3+1, но не вернулся",
            "after_genre": "Клиент выбирал жанр, но пропал",
            "no_response": "Клиент вообще не ответил на первое сообщение"
        }
        return scenarios_ru.get(self.state.scenario, self.state.scenario)
    
    def _get_client_role_prompt(self) -> str:
        """Системный промпт для Tietz в роли клиента"""
        behavior_prompts = {
            "busy": "Ты занятой клиент. Отвечаешь кратко, но не грубо. Дай понять что интересно, но сейчас нет времени.",
            "cold": "Ты холодный клиент. Не особо интересуешься. Отвечай сухо, без энтузиазма.",
            "doubtful": "Ты сомневающийся клиент. У тебя есть вопросы и сомнения по качеству.",
            "price_sensitive": "Ты чувствителен к цене. Тебя интересует продукт, но смущает стоимость.",
            "emotional": "Ты эмоциональный клиент. Тебе нравится идея, но ты нерешителен.",
            "interested": "Ты заинтересованный клиент, просто забыл/отвлёкся."
        }
        
        behavior_desc = behavior_prompts.get(self.state.behavior, "Веди себя естественно")
        scenario_desc = self._get_scenario_description()
        
        return f"""Ты играешь роль клиента в диалоге с продавцом персональных песен.

Ситуация: {scenario_desc}

Твоё поведение: {behavior_desc}

Важно:
- Отвечай естественно, как реальный клиент
- Не говори сразу "да" или "нет" - будь реалистичным
- Реагируй на тон и подход продавца
- Если видишь эмпатию и ценность - смягчайся
- Если давят или слишком настойчивы - закрывайся

Отвечай кратко (1-3 предложения)."""
    
    def _get_coach_role_prompt(self, seller_message: str, client_response: str) -> str:
        """Системный промпт для Tietz в роли наставника"""
        wave_guidance = {
            1: """Это первая волна. Оцени:
- Есть ли тёплое напоминание?
- Проявлена ли эмпатия?
- Аккуратен ли вопрос/предложение?
- Не слишком ли настойчиво?""",
            
            2: """Это вторая волна. Оцени:
- Добавлена ли ценность?
- Есть ли эмоция или микро-история?
- Предложен ли бонус/демо/идея?
- Сохранён ли тёплый тон?""",
            
            3: """Это третья волна. Оцени:
- Уважаются ли границы клиента?
- Мягкое ли завершение?
- Дверь остаётся открытой?
- Нет ли давления или обиды?"""
        }
        
        guidance = wave_guidance.get(self.state.wave, "Оцени общую эффективность")
        
        return f"""Ты Tietz - наставник по продажам. Анализируешь работу с неактивными клиентами.

Ситуация: {self._get_scenario_description()}
Волна сообщений: {self.state.wave} из 3

Сообщение продавца: "{seller_message}"
Ответ клиента: "{client_response}"

{guidance}

Дай краткий разбор (2-4 предложения):
- Что хорошо
- Что можно улучшить
- Конкретный совет

Тон: тёплый, поддерживающий, экспертный."""
    
    def handle(self, text: str) -> Dict[str, Any]:
        """
        Обработка сообщения продавца.
        Возвращает ответ клиента + обратную связь от наставника.
        """
        # Сохраняем сообщение продавца
        self.state.history.append({
            "role": "seller",
            "content": text,
            "wave": self.state.wave
        })
        self.state.meta["responses"] += 1
        
        # Генерируем ответ клиента через Tietz
        client_response = self._generate_client_response(text)
        
        # Сохраняем ответ клиента
        self.state.history.append({
            "role": "client",
            "content": client_response,
            "wave": self.state.wave
        })
        
        # Генерируем обратную связь от наставника
        coach_feedback = self._generate_coach_feedback(text, client_response)
        self.state.feedback.append(coach_feedback)
        
        # Проверяем, пора ли переходить к следующей волне
        should_advance = self.state.meta["responses"] % 2 == 0  # После каждых 2 ответов
        
        result = {
            "client_response": client_response,
            "coach_feedback": coach_feedback,
            "wave": self.state.wave,
            "scenario": self._get_scenario_description(),
            "behavior": self.state.behavior,
        }
        
        if should_advance and self.state.wave < 3:
            self.state.wave += 1
            result["wave_advanced"] = True
            result["next_wave"] = self.state.wave
            result["wave_message"] = self._get_wave_message(self.state.wave)
        
        self._save()
        return result
    
    def _generate_client_response(self, seller_message: str) -> str:
        """Генерация ответа клиента через DeepSeek"""
        if not self.llm:
            return self._local_client_response()
        
        try:
            messages = [
                {"role": "system", "content": self._get_client_role_prompt()},
                {"role": "user", "content": seller_message}
            ]
            response = self.llm.chat(messages)
            return response
        except Exception as e:
            return self._local_client_response()
    
    def _generate_coach_feedback(self, seller_message: str, client_response: str) -> str:
        """Генерация обратной связи от наставника через DeepSeek"""
        if not self.llm:
            return self._local_coach_feedback()
        
        try:
            messages = [
                {"role": "system", "content": self._get_coach_role_prompt(seller_message, client_response)},
                {"role": "user", "content": f"Проанализируй это сообщение продавца в контексте ответа клиента"}
            ]
            feedback = self.llm.chat(messages)
            return feedback
        except Exception as e:
            return self._local_coach_feedback()
    
    def _local_client_response(self) -> str:
        """Локальный ответ клиента без AI"""
        responses = [
            "Спасибо, подумаю над этим.",
            "Хорошо, посмотрю позже.",
            "Интересно, но мне нужно время.",
        ]
        return random.choice(responses)
    
    def _local_coach_feedback(self) -> str:
        """Локальная обратная связь без AI"""
        return "Хороший подход! Продолжай в том же духе, добавь чуть больше эмпатии."
    
    def _get_wave_message(self, wave: int) -> str:
        """Сообщение о переходе на следующую волну"""
        messages = {
            1: "🌊 <b>Волна 1</b>\n\nТёплое напоминание. Покажи эмпатию и задай аккуратный вопрос.",
            2: "🌊 <b>Волна 2</b>\n\nДобавь ценность! Расскажи микро-историю или предложи бонус.",
            3: "🌊 <b>Волна 3</b>\n\nЗавершающая волна. Уважай границы, но оставь дверь открытой."
        }
        return messages.get(wave, "")
