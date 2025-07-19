from fastapi import FastAPI
from app.routers import companies, roast, gossip
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='WhatchuCookin API')

# No prefix here — we want to use "/roast" directly
app.include_router(roast.router)
app.include_router(gossip.router, prefix='/gossip')
app.include_router(companies.router, prefix='/companies')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def root():
    return {'message': 'Welcome to WhatchuCookin 👀🔥'}
