
# Glue to enhance sleeping_dragon/v4 with rule-engine
try:
    from modules.sleeping_dragon_rules.v1 import analyze_reply, suggest_fix
except Exception:
    analyze_reply = suggest_fix = None

def dragon_analyze(history, reply, stage=None):
    if not analyze_reply:
        return {"ok": False, "reason": "sleeping_dragon_rules not available"}
    return analyze_reply(history, reply, stage)

def dragon_suggest(history, reply, stage=None):
    if not suggest_fix:
        return {"ok": False, "reason": "sleeping_dragon_rules not available"}
    return suggest_fix(history, reply, stage)
