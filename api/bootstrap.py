import asyncio
import logging
import os

from sqlalchemy import func

from database import Base, SessionLocal, engine
from models import Pokemon

logger = logging.getLogger(__name__)

# Set once init has run, so per-worker lifespans skip it (workers forked by
# gunicorn inherit this from the arbiter process where on_starting ran).
INIT_DONE_ENV = "APP_INIT_DONE"


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema ensured")

    if os.getenv("AUTO_SEED", "0") != "1":
        return

    db = SessionLocal()
    try:
        is_empty = db.query(func.count(Pokemon.id)).scalar() == 0
    finally:
        db.close()
    if not is_empty:
        return

    max_pokemon = int(os.getenv("AUTO_SEED_MAX", "151"))
    if os.getenv("AUTO_SEED_SOURCE", "fixture") == "fixture":
        # Hermetic: synchronous, no network — "healthy" implies "data ready".
        from seed_fixture import seed_from_fixture

        count = seed_from_fixture(max_pokemon=max_pokemon)
        logger.info("Auto-seeded %s pokemon from local fixture", count)
    else:
        # Legacy path: live PokeAPI. Runs synchronously here (before serving),
        # so a passing healthcheck still implies the dataset is ready.
        from seed import seed_all

        logger.info("Auto-seeding %s pokemon from PokeAPI...", max_pokemon)
        asyncio.run(seed_all(max_pokemon))
