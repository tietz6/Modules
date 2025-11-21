# Формулы подсчёта (0–100)

**Шаг 1. Rule/LLM суб-баллы (0–10):**
- `rule_score = clamp(10 - sum(penalties), 0, 10)`
- `llm_score ∈ [0..10]` (от DeepSeek-оценки или fallback)

**Шаг 2. Комбинированный суб-балл (0–10):**
- `combined_sub = rule_weight * rule_score + llm_weight * llm_score`

**Шаг 3. По стадиям:**
- `stage_score(stage) = combined_sub * 10 * weight(stage)`

**Шаг 4. Эмоции/сложность (для arena):**
- `stage_score -= emotion_penalty.get(emotion,0)`
- `stage_score += difficulty_bonus.get(difficulty,0)`

**Шаг 5. Сумма по стадиям и бонусы/потолки:**
- `total = clamp(sum(stage_score) + bonuses - penalties_extra, 0, 100)`
