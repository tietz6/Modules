
# Glue to enhance arena/v4 with psychotypes
try:
    from modules.arena_psychotypes.v1 import spawn_persona, step_dialog
except Exception:
    spawn_persona = step_dialog = None

def psy_spawn(difficulty="medium", psy_type=None, context=None):
    if not spawn_persona:
        return {"ok": False, "reason":"arena_psychotypes not available"}
    return spawn_persona(difficulty, psy_type, context)

def psy_step(state, manager_reply):
    if not step_dialog:
        return {"ok": False, "reason":"arena_psychotypes not available"}
    return step_dialog(state, manager_reply)
