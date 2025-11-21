
# Optional glue to enhance objections/v3 with classifier
try:
    from modules.objections_classifier.v1 import classify, apply_patterns, score_response
except Exception:
    classify = apply_patterns = score_response = None

def enhance_reply(client_utterance: str, history=None):
    if not classify or not apply_patterns or not score_response:
        return None
    cl = classify(client_utterance, history=history or [])
    pat = apply_patterns(cl.get("type","doubts"), history or [], client_utterance)
    sc = score_response(pat.get("coach_reply",""))
    return {"classify": cl, "coach": pat, "score": sc}
