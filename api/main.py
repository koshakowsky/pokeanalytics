import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from database import Base, engine, SessionLocal
from models import Pokemon
from routers import pokemon, analytics, compare, types
from seed import seed_all
from seed_fixture import seed_from_fixture

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost,http://localhost:3000,http://localhost:8000",
    ).split(",")
    if o.strip()
]

# Optional shared secret protecting the admin seed endpoint. When unset, the
# endpoint is disabled to avoid leaving an unauthenticated reseed trigger open.
SEED_TOKEN = os.getenv("SEED_TOKEN")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    if os.getenv("AUTO_SEED", "0") == "1":
        db = SessionLocal()
        try:
            is_empty = db.query(func.count(Pokemon.id)).scalar() == 0
        finally:
            db.close()
        if is_empty:
            max_pokemon = int(os.getenv("AUTO_SEED_MAX", "151"))
            if os.getenv("AUTO_SEED_SOURCE", "fixture") == "fixture":
                count = seed_from_fixture(max_pokemon=max_pokemon)
                logger.info("Auto-seeded %s pokemon from local fixture", count)
            else:
                logger.info("Empty database detected, auto-seeding %s pokemon from PokeAPI...", max_pokemon)
                asyncio.create_task(seed_all(max_pokemon))

    yield


app = FastAPI(
    title="PokeAnalytics API",
    description="API for Pokemon analytics",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(pokemon.router)
app.include_router(analytics.router)
app.include_router(compare.router)
app.include_router(types.router)


@app.post("/api/admin/seed")
async def seed_database(
    background_tasks: BackgroundTasks,
    max_pokemon: int = Query(151, ge=1, le=1025),
    x_seed_token: str | None = Header(default=None),
):
    if not SEED_TOKEN:
        raise HTTPException(status_code=403, detail="Seeding is disabled")
    if x_seed_token != SEED_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid seed token")

    background_tasks.add_task(asyncio.run, seed_all(max_pokemon))
    return {
        "message": f"Seeding started for {max_pokemon} pokemon",
        "status": "background_task_started"
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "PokéAnalytics API"}
