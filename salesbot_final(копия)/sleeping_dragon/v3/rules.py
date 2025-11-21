
RULES = {
    "no_greeting": ["здравствуйте","добрый","приветствую"],
    "no_qualification": ["уточните","подскажите","давайте разберём"],
    "aggressive_tone": ["быстрее","давайте быстрее","вы обязаны","немедленно"]
}

def scan(text: str):
    t = text.lower()
    issues=[]
    if not any(w in t for w in RULES["no_greeting"]):
        issues.append("Отсутствует приветствие")
    if not any(w in t for w in RULES["no_qualification"]):
        issues.append("Нет квалификации клиента")
    if any(w in t for w in RULES["aggressive_tone"]):
        issues.append("Агрессивный тон в речи")
    return issues
