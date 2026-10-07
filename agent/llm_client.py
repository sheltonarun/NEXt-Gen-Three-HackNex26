import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash")
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_llm(system: str, user: str) -> str:
    resp = _client.models.generate_content(
        model=MODEL,
        contents=user,
        config=types.GenerateContentConfig(system_instruction=system),
    )
    return resp.text