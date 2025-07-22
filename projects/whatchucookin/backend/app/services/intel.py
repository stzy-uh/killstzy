import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def get_company_intel(company_name: str) -> dict:
    """
    Fetches latest headlines (stubbed) and then uses OpenAI to summarize
    into Gen Z–style bullet points. Returns exactly the keys:
      - company
      - headlines: List[str]
      - what_they_cookin: str
    """
    # (Optionally replace this stub with real scraping.)
    # headlines = scrape_headlines(company_name)
    search_url = f"https://news.google.com/search?q={company_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(resp.content, "html.parser")
    headlines = [a.text for a in soup.select("article h3 a")][:5]

    prompt = (
        f"In 2 concise bullet points, summarize what {company_name} is currently working on or planning. "
        "Be factual, clear, and insightful. No buzzwords, no hype — just straight intel.\n\n"
        "Headlines:\n" + "\n".join(f"- {h}" for h in headlines)
    )

    try:
        ai = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        summary = ai.choices[0].message.content.strip()
    except Exception as e:
        summary = f"GPT error: {e}"

    return {
        "company": company_name,
        "headlines": headlines,
        "what_they_cookin": summary
    }
