import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def generate_roast(company_name: str) -> str:
    prompt = (
        f"Roast the company '{company_name}' in just 1-2 sentences. "
    f"Be sharp, sarcastic, and witty — like you're on Twitter, not writing a novel."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Roast error: {str(e)}"

# ✅ Add this function so it can be imported
def roast_company(company_name: str) -> dict:
    return {
        "company": company_name,
        "roast": generate_roast(company_name)
    }
