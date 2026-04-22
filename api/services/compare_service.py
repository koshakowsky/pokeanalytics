from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from models import Pokemon, Type, TypeEffectiveness
from schemas import PokemonDetail, CompareResponse


def compare_pokemon(db: Session, pokemon_ids: list[int]) -> CompareResponse:
    pokemon_list = (
        db.query(Pokemon)
        .options(
            joinedload(Pokemon.types),
            joinedload(Pokemon.abilities),
            joinedload(Pokemon.egg_groups),
        )
        .filter(Pokemon.id.in_(pokemon_ids))
        .all()
    )

    seen = set()
    unique = []
    for p in pokemon_list:
        if p.id not in seen:
            seen.add(p.id)
            unique.append(p)
    pokemon_list = unique

    if len(pokemon_list) < 2:
        raise ValueError("Need at least 2 pokemon to compare")

    details = [PokemonDetail.model_validate(p) for p in pokemon_list]

    # --- Stat comparison ---
    stat_names = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "stat_total"]
    stat_comparison = {}

    for stat in stat_names:
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
    # Pre-load all type effectiveness into a dict for fast lookup
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
    Pre-load entire type effectiveness table into a dict.
    Key: (attacking_type_name, defending_type_name) -> multiplier
    """
    from sqlalchemy.orm import aliased

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

    eff_map = {}
    for row in rows:
        eff_map[(row.atk_name, row.def_name)] = row.multiplier

    return eff_map


def _calc_type_advantage(
    eff_map: dict[tuple[str, str], float],
    attacker_types: list[str],
    defender_types: list[str],
) -> dict:
    """Calculate type advantage using pre-loaded effectiveness map."""
    total_multiplier = 1.0
    details = []

    for atk_type in attacker_types:
        best_mult = 0.0  # best multiplier this attack type can achieve
        best_detail = None

        for def_type in defender_types:
            mult = eff_map.get((atk_type, def_type), 1.0)
            details.append({
                "attack_type": atk_type,
                "defend_type": def_type,
                "multiplier": mult,
            })

            # For multi-type defenders, multipliers stack multiplicatively
            # But for picking "best attack type", we track per-type
            if mult > best_mult:
                best_mult = mult

    # Calculate combined multiplier:
    # For each attacker type, multiply against all defender types
    for atk_type in attacker_types:
        atk_mult = 1.0
        for def_type in defender_types:
            atk_mult *= eff_map.get((atk_type, def_type), 1.0)

        # Use the best attacking type's multiplier
        if atk_mult > total_multiplier:
            total_multiplier = atk_mult

    # Recalculate: actually, the attacker picks the BEST type to attack with
    # So we take the max across attacker types
    best_overall = 0.0
    for atk_type in attacker_types:
        atk_mult = 1.0
        for def_type in defender_types:
            atk_mult *= eff_map.get((atk_type, def_type), 1.0)
        if atk_mult > best_overall:
            best_overall = atk_mult

    if best_overall == 0.0:
        best_overall = 1.0  # fallback

    return {
        "best_multiplier": best_overall,
        "details": details,
        "verdict": (
            "super_effective" if best_overall > 1 else
            "not_effective" if best_overall < 1 else
            "neutral"
        )
    }


def _calc_stat_advantage(p1, p2) -> dict:
    """Compare stats between two pokemon."""
    stats = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
    wins = 0
    losses = 0
    details = {}

    for stat in stats:
        v1 = getattr(p1, stat)
        v2 = getattr(p2, stat)
        diff = v1 - v2
        details[stat] = {
            "difference": diff,
            "winner": p1.name if diff > 0 else (p2.name if diff < 0 else "tie")
        }
        if diff > 0:
            wins += 1
        elif diff < 0:
            losses += 1

    return {
        "stats_won": wins,
        "stats_lost": losses,
        "stats_tied": 6 - wins - losses,
        "details": details,
    }