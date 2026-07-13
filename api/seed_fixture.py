import json
import logging
from pathlib import Path

from database import Base, SessionLocal, engine
from models import (
    Ability, EggGroup, Pokemon, Type, TypeEffectiveness,
    pokemon_abilities, pokemon_egg_groups, pokemon_types,
)

logger = logging.getLogger(__name__)

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "gen1.json"


def seed_from_fixture(path: Path = FIXTURE_PATH, max_pokemon: int | None = None) -> int:
    """Seed the database from the fixture; returns the number of pokemon."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for row in data["types"]:
            db.merge(Type(**row))
        for row in data["abilities"]:
            db.merge(Ability(**row))
        for row in data["egg_groups"]:
            db.merge(EggGroup(**row))
        for row in data["type_effectiveness"]:
            db.merge(TypeEffectiveness(**row))
        db.commit()

        records = data["pokemon"]
        if max_pokemon is not None:
            records = records[:max_pokemon]

        for entry in records:
            entry = dict(entry)
            type_links = entry.pop("types")
            ability_links = entry.pop("abilities")
            egg_group_ids = entry.pop("egg_groups")

            db.merge(Pokemon(**entry))
            db.flush()

            for link in type_links:
                db.execute(
                    pokemon_types.insert().prefix_with("OR IGNORE")
                    .values(pokemon_id=entry["id"], **link)
                )
            for link in ability_links:
                db.execute(
                    pokemon_abilities.insert().prefix_with("OR IGNORE")
                    .values(pokemon_id=entry["id"], **link)
                )
            for egg_group_id in egg_group_ids:
                db.execute(
                    pokemon_egg_groups.insert().prefix_with("OR IGNORE")
                    .values(pokemon_id=entry["id"], egg_group_id=egg_group_id)
                )
        db.commit()

        logger.info("Seeded %s pokemon from fixture %s", len(records), Path(path).name)
        return len(records)
    finally:
        db.close()
