from sqlalchemy.orm import Session, selectinload, aliased
from models import Pokemon, Type, TypeEffectiveness
from schemas import PokemonDetail, CompareResponse

STAT_NAMES = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "stat_total"]
BATTLE_STATS = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]


def compare_pokemon(db: Session, pokemon_ids: list[int]) -> CompareResponse:
    # Dedupe ids up front so the query (and result ordering) is unambiguous.
    unique_ids = list(dict.fromkeys(pokemon_ids))

    by_id = {
        p.id: p
        for p in (
            db.query(Pokemon)
            .options(
                selectinload(Pokemon.types),
                selectinload(Pokemon.abilities),
                selectinload(Pokemon.egg_groups),
            )
            .filter(Pokemon.id.in_(unique_ids))
            .all()
        )
    }

    # Preserve the order the caller requested; drop ids that don't exist.
    pokemon_list = [by_id[pid] for pid in unique_ids if pid in by_id]

    if len(pokemon_list) < 2:
        raise ValueError("Need at least 2 pokemon to compare")

    details = [PokemonDetail.model_validate(p) for p in pokemon_list]

    # --- Stat comparison ---
    stat_comparison = {}
    for stat in STAT_NAMES:
        values = {p.name: getattr(p, stat) for p in pokemon_list}
        max_val = max(values.values())
        min_val = min(values.values())
        leader = [name for name, val in values.items() if val == max_val]

        stat_comparison[stat] = {
            "values": values,
            "max": max_val,
            "min": min_val,
            "leader": leader,
            "spread": max_val - min_val,
        }

    # --- Type advantages ---
    type_eff_map = _build_type_effectiveness_map(db)

    advantages = {}
    for p in pokemon_list:
        p_types = [t.name for t in p.types]
        p_advantages = {}

        for other in pokemon_list:
            if other.id == p.id:
                continue

            other_types = [t.name for t in other.types]
            p_advantages[other.name] = {
                "type_advantage": _calc_type_advantage(type_eff_map, p_types, other_types),
                "stat_advantage": _calc_stat_advantage(p, other),
            }

        advantages[p.name] = p_advantages

    return CompareResponse(
        pokemon=details,
        stat_comparison=stat_comparison,
        advantages=advantages,
    )


def _build_type_effectiveness_map(db: Session) -> dict[tuple[str, str], float]:
    """
    Pre-load the entire type effectiveness table into a dict.
    Key: (attacking_type_name, defending_type_name) -> multiplier
    """
    AtkType = aliased(Type)
    DefType = aliased(Type)

    rows = (
        db.query(
            AtkType.name.label("atk_name"),
            DefType.name.label("def_name"),
            TypeEffectiveness.multiplier,
        )
        .join(AtkType, TypeEffectiveness.attacking_type_id == AtkType.id)
        .join(DefType, TypeEffectiveness.defending_type_id == DefType.id)
        .all()
    )

    return {(row.atk_name, row.def_name): row.multiplier for row in rows}


def _calc_type_advantage(
    eff_map: dict[tuple[str, str], float],
    attacker_types: list[str],
    defender_types: list[str],
) -> dict:
    """
    Best multiplier the attacker can achieve: for each of the attacker's types,
    its effectiveness against the defender stacks multiplicatively across the
    defender's types; the attacker picks the best of its types.
    """
    details = []
    best_overall = 0.0

    for atk_type in attacker_types:
        atk_mult = 1.0
        for def_type in defender_types:
            mult = eff_map.get((atk_type, def_type), 1.0)
            atk_mult *= mult
            details.append({
                "attack_type": atk_type,
                "defend_type": def_type,
                "multiplier": mult,
            })
        if atk_mult > best_overall:
            best_overall = atk_mult

    if best_overall == 0.0:
        best_overall = 1.0  # fallback when attacker has no types

    return {
        "best_multiplier": best_overall,
        "details": details,
        "verdict": (
            "super_effective" if best_overall > 1 else
            "not_effective" if best_overall < 1 else
            "neutral"
        ),
    }


def _calc_stat_advantage(p1, p2) -> dict:
    """Compare battle stats between two pokemon."""
    wins = 0
    losses = 0
    details = {}

    for stat in BATTLE_STATS:
        v1 = getattr(p1, stat)
        v2 = getattr(p2, stat)
        diff = v1 - v2
        details[stat] = {
            "difference": diff,
            "winner": p1.name if diff > 0 else (p2.name if diff < 0 else "tie"),
        }
        if diff > 0:
            wins += 1
        elif diff < 0:
            losses += 1

    return {
        "stats_won": wins,
        "stats_lost": losses,
        "stats_tied": len(BATTLE_STATS) - wins - losses,
        "details": details,
    }
