
import os, json, time
from typing import List, Dict, Any, Optional

# try to import http client shim
_http = None
try:
    from integrations.patch_v4.http_client import http_post, http_get
    _http = ("v4", http_post, http_get)
except Exception:
    try:
        from integrations.patch_v3.http_client import http_post, http_get  # backward
        _http = ("v3", http_post, http_get)
    except Exception:
        _http = None

# fallback requests
try:
    import requests
except Exception:
    requests = None

def _read_env(name: str, default: Optional[str]=None)->Optional[str]:
    return os.environ.get(name, default)

class _LLMClient:
    """Wrapper для DeepSeek (или любого совместимого сервиса).
    Ожидается JSON API вида:
      POST {api_url}
      headers: Authorization: Bearer <key>, Content-Type: application/json
      body: { messages: [{role, content}, ...] }
      resp: { output: "..." }  или  { choices:[{message:{content:"..."}}] }
    """
    def __init__(self):
        self.api_url = _read_env("DEEPSEEK_API_URL", "https://api.deepseek.example/v1/chat")
        self.api_key = _read_env("DEEPSEEK_API_KEY", None)
        self.timeout = float(_read_env("HTTP_TIMEOUT", "15"))
        self.retries = int(_read_env("HTTP_RETRIES", "2"))

    def chat(self, messages: List[Dict[str, str]])->str:
        # Fallback: если ключа нет — возврат простого коуч-эхо.
        if not self.api_key or (_http is None and requests is None):
            return self._local_echo(messages)

        payload = {"messages": messages}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        last_err = None
        for _ in range(max(1, self.retries)):
            try:
                if _http:
                    _, http_post, _ = _http
                    r = http_post(self.api_url, json=payload, headers=headers, timeout=self.timeout)
                    data = r if isinstance(r, dict) else {}
                else:
                    r = requests.post(self.api_url, json=payload, headers=headers, timeout=self.timeout)
                    data = r.json()
                # normalize
                if isinstance(data, dict):
                    if "output" in data and isinstance(data["output"], str):
                        return data["output"]
                    if "choices" in data and data["choices"]:
                        ch = data["choices"][0]
                        msg = (ch.get("message") or {}).get("content")
                        if isinstance(msg, str):
                            return msg
                # unexpected format
                last_err = f"unexpected response: {str(data)[:200]}"
            except Exception as e:
                last_err = str(e)
                time.sleep(0.25)

        # graceful degrade
        return self._local_echo(messages, error=last_err)

    def _local_echo(self, messages: List[Dict[str,str]], error: Optional[str]=None)->str:
        # простой тренер: даёт мягкий совет по последнему сообщению
        text = ""
        for m in reversed(messages):
            if m.get("role") in ("user","assistant"):
                text = m.get("content","")
                break
        prefix = "Совет коуча: "
        base = "задавай уточняющие вопросы, показывай ценность и веди к следующему шагу."
        if not text:
            return prefix + base
        low = text.lower()
        tips = []
        if any(w in low for w in ["цена","дорого","сколько"]):
            tips.append("переведи разговор к ценности результата и разложи стоимость на шаги/части.")
        if "?" not in text:
            tips.append("добавь 1–2 уточняющих вопроса, чтобы понять контекст.")
        if len(text) < 16:
            tips.append("расширь ответ ещё 1–2 фразами для доверия.")
        if not tips:
            tips.append(base)
        if error:
            tips.append("(локальный режим LLM, причина: " + error[:80] + ")")
        return prefix + " ".join(tips)

class _ASRStub:
    def transcribe(self, audio_bytes: bytes, lang: str="ru")->str:
        return "[asr-stub] распознавание недоступно в офлайн-режиме"

class _TTSStub:
    def synth(self, text: str, voice: str="neutral")->bytes:
        return b"[tts-stub]"

class VoicePipeline:
    """Основной фасад голосового шлюза.
    Содержит:
      - llm: чат-API
      - asr: распознавание (стаб)
      - tts: синтез (стаб)
    """
    def __init__(self):
        self.llm = _LLMClient()
        self.asr = _ASRStub()
        self.tts = _TTSStub()
