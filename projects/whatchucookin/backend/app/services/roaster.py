from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI()

def generate_roast(company: str) -> str:
    prompt = (f"Roast the company '{company}' in 1 sharp, witty line. "
              f"Keep it clean, clever, high-signal. Max ~25 words.")
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            temperature=0.9,
            max_tokens=60
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"(roast unavailable: {e})"
