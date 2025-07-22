
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
USE_OPENAI = bool(OPENAI_KEY)

client = None
if USE_OPENAI:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
    except Exception:
        client = None
        USE_OPENAI = False

def chat_complete(prompt: str, temperature: float = 0.7, model: str = "gpt-3.5-turbo"):
    """
    Returns completion text or raises.
    """
    if not USE_OPENAI or client is None:
        raise RuntimeError("openai_unavailable")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()
