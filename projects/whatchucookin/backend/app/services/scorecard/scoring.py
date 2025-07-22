from dataclasses import dataclass
import random

@dataclass
class ScoreResult:
    innovation: float
    product_momentum: float
    brand_clout: float
    financial_quality: float
    market_momentum: float
    talent_demand: float
    ethics_risk: float
    composite: float
    explanation: str

def compute_scores(company: str) -> ScoreResult:
    """
    Stub scoring – deterministic seed so same company gives same scores.
    Replace with real feature extraction later.
    """
    seed = sum(ord(c.lower()) for c in company) % 10000
    random.seed(seed)

    def r(): return round(random.uniform(30, 90), 1)

    innovation = r()
    product = r()
    brand = r()
    financial = r()
    market = r()
    talent = r()
    ethics = r()

    composite = round(
        (innovation*0.2 + product*0.15 + brand*0.15 + financial*0.2 +
         market*0.1 + talent*0.1 + ethics*0.1), 1
    )

    explanation = (
        f"{company} composite {composite}. Innovation {innovation}, product {product}, "
        f"brand {brand}, financial {financial}, market momentum {market}, "
        f"talent demand {talent}, ethics/risk {ethics} (stub model)."
    )

    return ScoreResult(
        innovation, product, brand, financial, market,
        talent, ethics, composite, explanation
    )
