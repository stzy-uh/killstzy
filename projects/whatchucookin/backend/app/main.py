from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# import your companies router (no other routers)
from app.routers.companies import router as companies_router

app = FastAPI(title="WhatchuCookin API", version="0.1.0")

# CORS so your React at 5173 can talk here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount your companies router exactly once under /companies
app.include_router(companies_router, prefix="/companies", tags=["companies"])

@app.get("/")
def root():
    return {"message": "Welcome to WhatchuCookin 👀🔥"}

@app.on_event("startup")
async def print_routes():
    print("---- ROUTES ----")
    for r in app.routes:
        try:
            print(r.methods, r.path)
        except:
            pass
    print("---------------")
