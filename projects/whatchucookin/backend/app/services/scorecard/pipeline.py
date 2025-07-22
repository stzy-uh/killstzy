from datetime import datetime
from .scoring import compute_scores

def get_scorecard(company: str):
    """
    Real pipeline placeholder – calls compute_scores (stub) now.
    """
    scores = compute_scores(company)
    composite = scores.composite
    explanation = scores.explanation
    return {
        "company": company,
        "composite": composite,
        "scores": {
            "innovation": scores.innovation,
            "product_momentum": scores.product_momentum,
            "brand_clout": scores.brand_clout,
            "financial_quality": scores.financial_quality,
            "market_momentum": scores.market_momentum,
            "talent_demand": scores.talent_demand,
            "ethics_risk": scores.ethics_risk,
        },
        "explanation": explanation,
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
