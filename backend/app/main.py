from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from . import db, ai
from .auth import current_user
from .config import settings
from .schemas import LocationIn, ProductOffer, ChatIn, ChatOut
from .scraper import scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_pool()
    sched = scheduler.start()      # in production run scrapers as a separate worker/cron instead
    yield
    sched.shutdown(wait=False)
    await db.close_pool()

app = FastAPI(title="Grocery TMA API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[settings.allowed_origin],
                   allow_methods=["*"], allow_headers=["*"])

@app.post("/api/location", status_code=204)
async def submit_location(loc: LocationIn, user: dict = Depends(current_user)):
    await db.pool.execute(
        """INSERT INTO user_locations (telegram_id, geom)
           VALUES ($1, ST_SetSRID(ST_MakePoint($2,$3),4326)::geography)
           ON CONFLICT (telegram_id) DO UPDATE SET geom=EXCLUDED.geom, updated_at=now()""",
        user["id"], loc.lng, loc.lat)

@app.get("/api/products/search", response_model=list[ProductOffer])
async def search_products(q: str = Query(min_length=2), lat: float = Query(ge=-90, le=90),
                          lng: float = Query(ge=-180, le=180),
                          radius_m: int = Query(3000, le=10000),
                          user: dict = Depends(current_user)):
    return await db.search_nearby(lat, lng, q, radius_m)

@app.post("/api/assistant/chat", response_model=ChatOut)
async def chat(body: ChatIn, user: dict = Depends(current_user)):
    if not settings.anthropic_api_key:
        raise HTTPException(503, "AI not configured")
    return await ai.run_assistant(body.message, body.lat, body.lng)

@app.get("/health")
async def health():
    return {"ok": True}
