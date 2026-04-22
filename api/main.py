import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import pokemon, analytics, compare, types
from seed import seed_all

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    yield


app = FastAPI(
    title="PokeAnalytics API",
    description="API for Pokemon analytics",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    max_pokemon: int = 151,
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    background_tasks.add_task(asyncio.run, seed_all(max_pokemon))
    return {
        "message": f"Seeding started for {max_pokemon} pokemon",
        "status": "background_task_started"
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "PokéAnalytics API"}