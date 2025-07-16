import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def get_company_news(company_name: str):
    search_url = f"https://news.google.com/search?q={company_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)

    soup = BeautifulSoup(response.content, "html.parser")
    headlines = []

    for article in soup.select("article h3 a"):
        title = article.text
        link = "https://news.google.com" + article["href"][1:]
        headlines.append(title)

    headlines = headlines[:10]
    summary = summarize_headlines(company_name, headlines)

    return {
        "company": company_name,
        "headlines": headlines,
        "what_they_cookin": summary
    }

def summarize_headlines(company: str, headlines: list):
    prompt = (
        f"In 2 concise bullet points,summarize what {company} is working on or planning. "
        f"be factual, clear and insightful. No buzzwords, no hype - just straight intel\n\n"
        f"Headlines:\n" + "\n".join(f"- {h}" for h in headlines)
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"GPT error: {str(e)}"
