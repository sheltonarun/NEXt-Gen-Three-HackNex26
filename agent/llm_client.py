import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash")
FALLBACK = os.getenv("LLM_FALLBACK_MODEL", "gemini-3.1-flash-lite")
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _call(model: str, system: str, user: str) -> str:
    resp = _client.models.generate_content(
        model=model,
        contents=user,
        config=types.GenerateContentConfig(system_instruction=system),
    )
    return resp.text


def ask_llm(system: str, user: str, retries: int = 4) -> str:
    for model in (MODEL, FALLBACK):
        for attempt in range(retries):
            try:
                return _call(model, system, user)
            except errors.APIError as e:
                if e.code in (429, 500, 503):      # busy or rate-limited: wait, retry
                    time.sleep(2 ** attempt)       # 1s, 2s, 4s, 8s
                    continue
                raise                              # real error (bad key, bad model name)
    raise RuntimeError("LLM unavailable after retries on both models")