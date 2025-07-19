# app/services/jobs.py
def fetch_jobs(company: str) -> dict:
    # Placeholder job listings
    return {
        "company": company,
        "listings": [
            {"title": "Data Analyst", "location": "Remote", "age": "2d"},
            {"title": "Product Manager", "location": "NYC", "age": "5d"},
        ]
    }
