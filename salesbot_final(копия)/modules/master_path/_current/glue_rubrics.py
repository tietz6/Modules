
# Optional glue for master_path/v3
try:
    from modules.master_path_rubrics.v1 import score_dialog
except Exception:
    score_dialog = None

def compute_master_score(history):
    if not score_dialog:
        return {"ok": False, "reason": "rubrics not available"}
    res = score_dialog(history or [])
    return {"ok": True, "result": res}
