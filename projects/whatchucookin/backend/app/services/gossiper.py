from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_gossip_data(company: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're a Gen Z gossip expert"},
            {"role": "user", "content": f"Give me a short and spicy gossip-style rumors about {company}?" f"Keep it playful but believable, try to be factual. Each one in 1 sentence. No filler."}
        ]
    )
    return {"gossip": response.choices[0].message.content}
