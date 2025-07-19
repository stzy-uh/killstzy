"""
Score computation module for WhatchuCookin.

Principles:
- Missing data => None (NOT 0). We then reweight composite over available subscores.
- Each subscore normalized to 0–100.
- Composite optionally soft-penalized for low coverage (mild factor, adjustable).
"""

from __future__ import annotations
from typing import Dict, Optional, Tuple, Any

# Base weights (sum = 1.0). Adjust freely.
WEIGHTS: Dict[str, float] = {
    "innovation":        0.18,
    "product_momentum":  0.18,
    "financial_quality": 0.22,
    "brand_clout":       0.12,
    "market_momentum":   0.10,
    "talent_demand":     0.12,
    "ethics_risk":       0.08,
}

# How strong is the coverage penalty. 0 = none, 0.15 = mild.
COVERAGE_PENALTY_WEIGHT = 0.15  # composite * (0.85 + 0.15*coverage)


# ----------------------------- Helpers --------------------------------- #

def clamp(x: float) -> float:
    return max(0.0, min(100.0, x))


def safe_norm(val: Optional[float], max_ref: float) -> Optional[float]:
    """
    Normalize val to 0–100 relative to max_ref. Returns None if val is None.
    """
    if val is None:
        return None
    return clamp((val / max_ref) * 100.0) if max_ref > 0 else None


# ------------------------ Subscore Functions --------------------------- #

def _financial_quality(fin: Dict[str, Any]) -> Optional[float]:
    """
    Blend of revenue growth %, gross margin %, and a shaped P/E scoring.
    All inputs optional. Returns None if nothing available.
    Expected fields:
      - rev_growth_yoy (percent already or fraction—adjust if needed)
      - gross_margin_pct (percent 0–100)
      - pe (price/earnings ratio)
    """
    if not fin:
        return None

    rev_growth = fin.get("rev_growth_yoy")
    gross = fin.get("gross_margin_pct")
    pe = fin.get("pe")

    parts = []

    if rev_growth is not None:
        # If rev_growth arrives as fraction (e.g. 0.15) convert—detect heuristic.
        if abs(rev_growth) <= 1:
            rev_growth = rev_growth * 100
        parts.append(clamp(rev_growth))

    if gross is not None:
        if abs(gross) <= 1:  # fraction to percent
            gross = gross * 100
        parts.append(clamp(gross))

    if pe is not None and pe > 0:
        # Sweet-ish zone 10–30. Below 10 may mean undervalued / risk; above 60 stretched.
        if pe <= 5:
            val = 55
        elif pe <= 10:
            val = 70
        elif pe <= 30:
            # 10 -> 80, 30 -> 60 (gentle decline)
            span = pe - 10
            val = 80 - (span * 1.0)  # 10 =>80, 30=>60
        elif pe <= 60:
            # 30 -> 60 (already 60), 60 -> 35
            span = pe - 30
            val = 60 - (span * (25 / 30))  # linear to 35
        else:
            val = 25
        parts.append(clamp(val))

    if not parts:
        return None

    return sum(parts) / len(parts)


def _brand_clout(news: Optional[Dict[str, Any]], jobs: Optional[Dict[str, Any]]) -> Optional[float]:
    """
    Rough brand clout proxy = mix of recent headline volume + hiring volume.
    """
    if not news and not jobs:
        return None
    scores = []
    if news:
        h = news.get("headline_count_30d")
        if h is not None:
            scores.append(clamp(min(h, 150) / 150 * 100))
    if jobs:
        j = jobs.get("job_count")
        if j is not None:
            scores.append(clamp(min(j, 500) / 500 * 100))
    if not scores:
        return None
    return sum(scores) / len(scores)


def _market_momentum(fin: Optional[Dict[str, Any]]) -> Optional[float]:
    """
    Daily % price change mapped:
      -5% => 0
       0% => 50
      +5% => 100
    Clamped outside that band.
    """
    if not fin:
        return None
    change = fin.get("change_percent")
    if change is None:
        return None
    return clamp((change + 5) / 10 * 100)


def _talent_demand(jobs: Optional[Dict[str, Any]]) -> Optional[float]:
    if not jobs:
        return None
    jc = jobs.get("job_count")
    return safe_norm(jc, 400) if jc is not None else None


def _innovation(github: Optional[Dict[str, Any]]) -> Optional[float]:
    """
    Innovation proxy using commits + stars last 30 days.
    We weight commits heavier; tune as needed.
    """
    if not github:
        return None
    commits = github.get("commits_last30")
    stars = github.get("stars_last30")
    if commits is None and stars is None:
        return None
    c_score = safe_norm(commits, 500) if commits is not None else None
    s_score = safe_norm(stars, 300) if stars is not None else None
    parts = [p for p in (c_score, s_score) if p is not None]
    if not parts:
        return None
    # Slight bias toward commits if both present
    if c_score is not None and s_score is not None:
        return clamp((c_score * 0.6) + (s_score * 0.4))
    return parts[0]


def _product_momentum(news: Optional[Dict[str, Any]]) -> Optional[float]:
    if not news:
        return None
    count = news.get("headline_count_30d")
    return safe_norm(count, 120) if count is not None else None


def _ethics_risk(raw: Dict[str, Any]) -> Optional[float]:
    """
    Placeholder: neutral 60. Replace with:
      - Negative news keyword ratio
      - ESG controversy feed
      - Lawsuit / recall flags
    """
    return 60.0


# -------------------------- Public API -------------------------------- #

def compute_scores(raw: Dict[str, Any]) -> Tuple[Dict[str, Optional[float]], Optional[float], Dict[str, Any]]:
    """
    Compute all subscores + composite + meta.
    raw expects keys: financials, news, jobs, github (all optional dicts).
    Returns:
        subscores: dict[subscore_name -> 0..100 or None]
        composite: float or None
        meta: { coverage: float, missing: {name: bool}, weight_sum: float }
    """

    github = raw.get("github")
    news = raw.get("news")
    jobs = raw.get("jobs")
    fin = raw.get("financials")

    subs = {
        "innovation":        _innovation(github),
        "product_momentum":  _product_momentum(news),
        "financial_quality": _financial_quality(fin),
        "brand_clout":       _brand_clout(news, jobs),
        "market_momentum":   _market_momentum(fin),
        "talent_demand":     _talent_demand(jobs),
        "ethics_risk":       _ethics_risk(raw),
    }

    # Filter available subscores
    available = {k: v for k, v in subs.items() if v is not None}
    if not available:
        composite = None
        weight_sum = 0.0
    else:
        weight_sum = sum(WEIGHTS[k] for k in available)
        composite_raw = 0.0
        for k, v in available.items():
            composite_raw += v * (WEIGHTS[k] / weight_sum)
        coverage = len(available) / len(WEIGHTS)
        composite = composite_raw * (1 - COVERAGE_PENALTY_WEIGHT + COVERAGE_PENALTY_WEIGHT * coverage)
        composite = round(composite, 1)

    coverage = len(available) / len(WEIGHTS) if WEIGHTS else 0.0

    meta = {
        "coverage": coverage,
        "missing": {k: (subs[k] is None) for k in subs},
        "weight_sum_used": weight_sum,
    }

    return subs, composite, meta
