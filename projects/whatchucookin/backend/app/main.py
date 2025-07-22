from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import companies  # only companies now

app = FastAPI(title="WhatchuCookin API", version="0.1.0")

# CORS so React @5173 can talk here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount only the companies router
app.include_router(companies.router, prefix="/companies", tags=["companies"])

@app.get("/")
def root():
    return {"message": "Welcome to WhatchuCookin 👀🔥"}

# Optional: show routes on startup
@app.on_event("startup")
async def print_routes():
    print("---- ROUTES ----")
    for r in app.routes:
        try:
            print(r.methods, r.path)
        except:
            pass
    print("---------------")
