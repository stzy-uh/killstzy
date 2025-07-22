from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()

# backend/app/services/gossiper.py

def generate_gossip(company_name: str) -> str:
    """
    Stub: generate or fetch some gossip for the given company.
    Replace this with your actual AI call or scraping logic.
    """
    return f"Word on the street is that {company_name} is up to something big…"


