import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from database import SessionLocal
from models import (
    Ability, EggGroup, Pokemon, Type, TypeEffectiveness,
    pokemon_abilities, pokemon_egg_groups, pokemon_types,
)

OUT_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "gen1.json"

POKEMON_COLUMNS = [
    "id", "name", "height", "weight", "base_experience",
    "hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "stat_total",
    "sprite_url", "sprite_official",
    "generation", "is_legendary", "is_mythical", "is_baby",
    "habitat", "color", "shape", "growth_rate",
    "capture_rate", "base_happiness", "gender_rate",
]


def main() -> None:
    db = SessionLocal()
    try:
        pokemon = db.query(Pokemon).order_by(Pokemon.id).all()
        types = db.query(Type).order_by(Type.id).all()
        effectiveness = db.query(TypeEffectiveness).order_by(TypeEffectiveness.id).all()

        type_links = db.execute(select(pokemon_types)).all()
        ability_links = db.execute(select(pokemon_abilities)).all()
        egg_group_links = db.execute(select(pokemon_egg_groups)).all()

        used_ability_ids = {row.ability_id for row in ability_links}
        used_egg_group_ids = {row.egg_group_id for row in egg_group_links}
        abilities = (
            db.query(Ability).filter(Ability.id.in_(used_ability_ids))
            .order_by(Ability.id).all()
        )
        egg_groups = (
            db.query(EggGroup).filter(EggGroup.id.in_(used_egg_group_ids))
            .order_by(EggGroup.id).all()
        )

        types_by_pokemon: dict[int, list[dict]] = {}
        for row in type_links:
            types_by_pokemon.setdefault(row.pokemon_id, []).append(
                {"type_id": row.type_id, "slot": row.slot}
            )
        abilities_by_pokemon: dict[int, list[dict]] = {}
        for row in ability_links:
            abilities_by_pokemon.setdefault(row.pokemon_id, []).append(
                {"ability_id": row.ability_id, "is_hidden": bool(row.is_hidden), "slot": row.slot}
            )
        egg_groups_by_pokemon: dict[int, list[int]] = {}
        for row in egg_group_links:
            egg_groups_by_pokemon.setdefault(row.pokemon_id, []).append(row.egg_group_id)

        data = {
            "meta": {
                "description": "Hermetic seed fixture exported from a PokeAPI-seeded DB",
                "generated_on": date.today().isoformat(),
                "pokemon_count": len(pokemon),
            },
            "types": [{"id": t.id, "name": t.name} for t in types],
            "type_effectiveness": [
                {
                    "id": e.id,
                    "attacking_type_id": e.attacking_type_id,
                    "defending_type_id": e.defending_type_id,
                    "multiplier": e.multiplier,
                }
                for e in effectiveness
            ],
            "abilities": [
                {"id": a.id, "name": a.name, "effect": a.effect, "short_effect": a.short_effect}
                for a in abilities
            ],
            "egg_groups": [{"id": g.id, "name": g.name} for g in egg_groups],
            "pokemon": [
                {
                    **{col: getattr(p, col) for col in POKEMON_COLUMNS},
                    "types": sorted(types_by_pokemon.get(p.id, []), key=lambda x: x["slot"]),
                    "abilities": sorted(abilities_by_pokemon.get(p.id, []), key=lambda x: x["slot"]),
                    "egg_groups": sorted(egg_groups_by_pokemon.get(p.id, [])),
                }
                for p in pokemon
            ],
        }

        OUT_PATH.parent.mkdir(exist_ok=True)
        OUT_PATH.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
        print(
            f"Wrote {OUT_PATH} — pokemon: {len(pokemon)}, types: {len(types)}, "
            f"effectiveness: {len(effectiveness)}, abilities: {len(abilities)}, "
            f"egg_groups: {len(egg_groups)}, size: {OUT_PATH.stat().st_size // 1024} KiB"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
