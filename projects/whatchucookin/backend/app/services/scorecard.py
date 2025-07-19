# app/services/scorecard.py
from datetime import datetime

def build_scorecard(raw_company: str) -> dict:
    company = raw_company.strip()
    display = company.upper()
    # Temporary fixed values
    innovation = 72
    ethics = 55
    clout = 81

    return {
        "company": display,
        "scores": {
            "innovation": innovation,
            "ethics": ethics,
            "clout": clout
        },
        "composite": round((innovation*0.45 + ethics*0.2 + clout*0.35), 1),
        "summary": (
            f"{display}: solid innovation momentum, middling transparency, strong brand gravity "
            "(stub – real data pipeline pending)."
        ),
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "sources": []  # will populate later
    }
