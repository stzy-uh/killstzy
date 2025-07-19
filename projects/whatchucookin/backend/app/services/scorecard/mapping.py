# app/services/scorecard/mapping.py
MAPPINGS = {
    "nvidia": {"ticker": "NVDA", "github_org": "NVIDIA", "careers_url": "https://www.nvidia.com/en-us/about-nvidia/careers/"},
    "apple": {"ticker": "AAPL", "github_org": "apple", "careers_url": "https://jobs.apple.com/en-us/search"},
    "microsoft": {"ticker": "MSFT", "github_org": "microsoft", "careers_url": "https://jobs.careers.microsoft.com/global/en"},
    "meta": {"ticker": "META", "github_org": "facebook", "careers_url": "https://www.metacareers.com/jobs"},
    "google": {"ticker": "GOOGL", "github_org": "google", "careers_url": "https://careers.google.com/jobs/results/"}
}

def resolve(company: str) -> dict:
    c = company.strip().lower()
    return MAPPINGS.get(c, {
        "ticker": company.upper(),
        "github_org": None,
        "careers_url": None
    })
