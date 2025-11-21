
from core.voice_gateway.v1 import VoicePipeline
from .rules import scan

class SleepingDragon:
    def __init__(self):
        try:
            self.llm = VoicePipeline().llm
        except Exception:
            self.llm = None

    def analyze(self, transcript: str)->dict:
        rule_issues = scan(transcript)
        llm_feedback = None

        if self.llm:
            try:
                msg = [
                    {"role":"system","content":"Ты эксперт-методист. Ты анализируешь ошибки менеджера в продажах."},
                    {"role":"user","content":transcript}
                ]
                ans = self.llm.chat(msg)
                llm_feedback = ans
            except Exception:
                pass

        return {
            "ok": True,
            "rule_issues": rule_issues,
            "llm_feedback": llm_feedback
        }
