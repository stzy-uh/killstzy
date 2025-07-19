from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_gossip_data(company: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Keep it playful but believable, try to be factual.in 1 sentence. No filler. spicy gossip-style rumors about {company}?" 
             }
        ]
    )
    return {"gossip": response.choices[0].message.content}
