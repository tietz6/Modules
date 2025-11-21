# DeepSeek Persona Module

## Overview
Provides branded AI persona for the "На Счастье" (To Happiness) brand. Ensures all AI-generated responses maintain the brand's warm, professional, and emotional communication style.

## Features
- Brand-specific system prompts
- Role-based response styling (coach, emotional client, rational client)
- Template-based emotional phrases
- Integration with DeepSeek AI via VoicePipeline
- Graceful fallback when API unavailable

## API Endpoints

### GET /deepseek_persona/v1/persona
Get the complete persona configuration.

**Response:**
```json
{
  "brand": "На Счастье",
  "tone": {
    "coach": "тёплый, уверенный, экспертный, но дружелюбный",
    "client": "эмоциональный, живой, реалистичный",
    "system": "стиль бренда — забота, искренность, эмоция, уважительное общение"
  },
  "rules": [...],
  "templates": {...}
}
```

### POST /deepseek_persona/v1/chat
Generate AI response with brand persona.

**Request:**
```json
{
  "prompt": "Как мне ответить клиенту на возражение о цене?",
  "role": "coach"
}
```

**Response:**
```json
{
  "reply": "Хей, давай разберёмся вместе 😊 Переведи разговор к ценности результата..."
}
```

### POST /deepseek_persona/v1/stylize
Apply brand style to existing text.

**Request:**
```json
{
  "text": "Расскажите о вашем бюджете",
  "role": "coach"
}
```

**Response:**
```json
{
  "styled": "Хей, давай разберёмся вместе 😊 Расскажите о вашем бюджете"
}
```

## Roles

### coach
Used for trainer feedback, recommendations, and guidance.

**Style:** Warm, confident, expert but friendly
**Opening templates:**
- "Хей, давай разберёмся вместе 😊"
- "Смотри, сейчас покажу, как можно сделать ещё лучше:"
- "Ты уже молодец, теперь усилим пару моментов…"

### client_emotional
Used for emotional client simulation in training.

**Style:** Expressive, values feelings and relationships
**Opening templates:**
- "Мне важно, чтобы получилось по‑настоящему…"
- "Я видел ваши работы — хочу что‑то тёплое, душевное."
- "Хочу удивить близкого человека."

### client_rational
Used for rational/logical client simulation.

**Style:** Focuses on facts, results, and clear outcomes
**Opening templates:**
- "Мне нужен понятный результат и сроки."
- "Скажи коротко: что я получу?"
- "Мне важно понимать стоимость и этапы."

## Brand Rules

The persona follows these core principles:

1. **Говорить от души, без официоза** - Speak from the heart, no bureaucratic language
2. **Использовать мягкие фразы** - Use soft phrases: "давай посмотрим", "предлагаю такой вариант", "подскажи…"
3. **Подчёркивать ценность эмоций и историй** - Emphasize value of emotions and stories
4. **Не давить. Направлять.** - Don't push. Guide.
5. **Признание ошибок менеджера формулировать мягко, но уверенно** - Acknowledge manager's mistakes gently but confidently

## Configuration

### Environment Variables
- `DEEPSEEK_API_KEY` - API key for DeepSeek service
- `DEEPSEEK_API_URL` - API endpoint (default: https://api.deepseek.com/v1/chat/completions)
- `DEEPSEEK_MODEL` - Model name (default: deepseek-chat)

### Data File

`data/persona.json` contains:
- Brand identity
- Communication tone definitions
- Speaking rules
- Template phrases for each role

## Usage in Code

### Basic Chat
```python
from modules.deepseek_persona.v1.service import persona_chat

response = persona_chat(
    "Клиент говорит, что дорого",
    role="coach"
)
# Returns: "Смотри, сейчас покажу... [advice with brand style]"
```

### Apply Style to Text
```python
from modules.deepseek_persona.v1.service import apply_persona

styled = apply_persona(
    role="client_emotional",
    text="Мне нужна песня для жены"
)
# Returns: "Мне важно, чтобы получилось по‑настоящему… Мне нужна песня для жены"
```

### Load Configuration
```python
from modules.deepseek_persona.v1.service import load_persona

persona = load_persona()
print(persona["brand"])  # "На Счастье"
print(persona["rules"])  # List of communication rules
```

## Integration Points

### With Training Modules
All training modules (Master Path, Arena, Upsell, Objections) use this persona for:
- Coach feedback generation
- Client response simulation
- Recommendation styling

### With Telegram Bot
The telegram_bot integration uses this persona to ensure all bot responses maintain brand voice.

### With Voice Pipeline
VoicePipeline automatically applies persona styling when generating LLM responses.

## Fallback Behavior

If DeepSeek API is unavailable:
1. System uses local template-based responses
2. Maintains brand style through template selection
3. Returns appropriate fallback text for the role
4. Never fails - always returns some response

## Testing

### Test Chat Endpoint
```bash
curl -X POST http://localhost:8080/deepseek_persona/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Как мне начать разговор с клиентом?",
    "role": "coach"
  }'
```

### Test Stylize Endpoint
```bash
curl -X POST http://localhost:8080/deepseek_persona/v1/stylize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Давайте обсудим детали",
    "role": "coach"
  }'
```

### Get Persona Config
```bash
curl http://localhost:8080/deepseek_persona/v1/persona
```

## Customization

To modify the brand persona:

1. Edit `data/persona.json`
2. Update tone definitions, rules, or templates
3. Restart the application
4. No code changes needed

## Best Practices

1. **Use appropriate roles**: Coach for guidance, client roles for simulation
2. **Keep prompts clear**: More specific prompts = better persona-aligned responses
3. **Test fallbacks**: Ensure system works without API access
4. **Monitor tone**: Regularly check that responses maintain brand voice
5. **Update templates**: Refresh template phrases based on real usage patterns

## Related Modules

- `core/voice_gateway/v1/` - VoicePipeline with DeepSeek integration
- `integrations/telegram_bot/v1/` - Uses persona for bot responses
- `modules/trainer_*/` - Training modules that use persona for feedback
- `modules/arena/` - Arena training uses persona for client simulation
