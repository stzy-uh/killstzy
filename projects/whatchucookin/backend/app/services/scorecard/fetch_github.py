# app/services/scorecard/fetch_github.py
import httpx
from datetime import datetime, timedelta

GITHUB_API = "https://api.github.com"

async def fetch_github_metrics(org: str) -> dict:
    if not org:
        return {"commits_last30": 0, "stars_last30": 0}
    async with httpx.AsyncClient(timeout=10) as client:
        repos = await client.get(f"{GITHUB_API}/orgs/{org}/repos?per_page=50&type=public&sort=updated")
        if repos.status_code != 200:
            return {"commits_last30": 0, "stars_last30": 0}
        data = repos.json()
    now = datetime.utcnow()
    cutoff = now - timedelta(days=30)
    commits_count = 0
    stars_new = 0  # GitHub API doesn't give stars in last 30 directly; we approximate via updated_at
    for r in data[:25]:
        pushed_at = r.get("pushed_at")
        stargazers = r.get("stargazers_count", 0)
        if pushed_at:
            try:
                dt = datetime.fromisoformat(pushed_at.replace("Z",""))
                if dt >= cutoff:
                    commits_count += 1  # proxy: treat active repos as "1"
                    stars_new += int(stargazers * 0.02)  # crude heuristic
            except:
                pass
    return {"commits_last30": commits_count, "stars_last30": stars_new}
