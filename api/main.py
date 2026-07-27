import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from routers import pokemon, analytics, compare, types
from seed import seed_all
from bootstrap import INIT_DONE_ENV, initialize_database

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
    # Under gunicorn, on_starting() already ran initialize_database() once in
    # the arbiter before forking (INIT_DONE_ENV set), so workers skip it and
    # avoid racing on the SQLite file. Under a bare `uvicorn main:app` (single
    # process) the flag is unset, so we initialize here.
    if os.environ.get(INIT_DONE_ENV) != "1":
        initialize_database()
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
