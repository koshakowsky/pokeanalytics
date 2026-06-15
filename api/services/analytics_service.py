from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from models import Pokemon, Type, pokemon_types
from schemas import CategoryStat, TypeDistribution, GenerationStats

# Pokemon columns that may be used as a grouping dimension.
GROUPABLE_COLUMNS = {"color", "generation", "habitat", "shape", "growth_rate"}

_STAT_AGGREGATES = (
    func.count(Pokemon.id).label("count"),
    func.avg(Pokemon.stat_total).label("avg_stat_total"),
    func.avg(Pokemon.hp).label("avg_hp"),
    func.avg(Pokemon.attack).label("avg_attack"),
    func.avg(Pokemon.defense).label("avg_defense"),
    func.avg(Pokemon.sp_attack).label("avg_sp_attack"),
    func.avg(Pokemon.sp_defense).label("avg_sp_defense"),
    func.avg(Pokemon.speed).label("avg_speed"),
    func.min(Pokemon.stat_total).label("min_stat_total"),
    func.max(Pokemon.stat_total).label("max_stat_total"),
)


def get_category_analysis(db: Session, category_field: str = "type") -> list[CategoryStat]:
    """Pokemon analysis grouped by a category (type, color, generation, ...)."""

    if category_field == "type":
        results = (
            db.query(Type.name.label("category"), *_STAT_AGGREGATES)
            .join(pokemon_types, Pokemon.id == pokemon_types.c.pokemon_id)
            .join(Type, Type.id == pokemon_types.c.type_id)
            .group_by(Type.name)
            .order_by(func.count(Pokemon.id).desc())
            .all()
        )
    else:
        if category_field not in GROUPABLE_COLUMNS:
            category_field = "color"
        col = getattr(Pokemon, category_field)
        results = (
            db.query(col.label("category"), *_STAT_AGGREGATES)
            .filter(col.isnot(None))
            .group_by(col)
            .order_by(func.count(Pokemon.id).desc())
            .all()
        )

    return [
        CategoryStat(
            category=str(r.category),
            count=r.count,
            avg_stat_total=round(r.avg_stat_total, 1),
            avg_hp=round(r.avg_hp, 1),
            avg_attack=round(r.avg_attack, 1),
            avg_defense=round(r.avg_defense, 1),
            avg_sp_attack=round(r.avg_sp_attack, 1),
            avg_sp_defense=round(r.avg_sp_defense, 1),
            avg_speed=round(r.avg_speed, 1),
            min_stat_total=r.min_stat_total,
            max_stat_total=r.max_stat_total,
        )
        for r in results
    ]


def get_type_distribution(db: Session) -> list[TypeDistribution]:
    """Distribution of Pokemon by types."""
    total_pokemon = db.query(func.count(Pokemon.id)).scalar()

    results = (
        db.query(
            Type.name,
            func.count(Pokemon.id).label("count"),
            func.avg(Pokemon.stat_total).label("avg_stat_total"),
        )
        .join(pokemon_types, Type.id == pokemon_types.c.type_id)
        .join(Pokemon, Pokemon.id == pokemon_types.c.pokemon_id)
        .group_by(Type.name)
        .order_by(func.count(Pokemon.id).desc())
        .all()
    )

    return [
        TypeDistribution(
            type_name=r[0],
            count=r[1],
            percentage=round(r[1] / total_pokemon * 100, 1) if total_pokemon else 0,
            avg_stat_total=round(r[2], 1),
        )
        for r in results
    ]


def get_stat_ranges(db: Session) -> dict:
    """Ranges of all characteristics for filter sliders."""
    stats = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "stat_total"]
    result = {}

    for stat in stats:
        col = getattr(Pokemon, stat)
        row = db.query(
            func.min(col).label("min"),
            func.max(col).label("max"),
            func.avg(col).label("avg"),
        ).first()
        result[stat] = {
            "min": row.min,
            "max": row.max,
            "avg": round(row.avg, 1) if row.avg else 0,
        }

    return result


def get_generation_stats(db: Session) -> list[GenerationStats]:
    """Stats by generation (computed in two queries, not one-per-generation)."""
    generations = (
        db.query(
            Pokemon.generation,
            func.count(Pokemon.id).label("total"),
            func.avg(Pokemon.stat_total).label("avg_stat_total"),
            func.sum(case((Pokemon.is_legendary == True, 1), else_=0)).label("legendary_count"),
            func.sum(case((Pokemon.is_mythical == True, 1), else_=0)).label("mythical_count"),
        )
        .filter(Pokemon.generation.isnot(None))
        .group_by(Pokemon.generation)
        .order_by(Pokemon.generation)
        .all()
    )

    totals_by_gen = {g.generation: g.total for g in generations}

    # Single query for the per-generation type distribution.
    type_rows = (
        db.query(
            Pokemon.generation,
            Type.name,
            func.count(Pokemon.id).label("count"),
            func.avg(Pokemon.stat_total).label("avg_st"),
        )
        .join(pokemon_types, Type.id == pokemon_types.c.type_id)
        .join(Pokemon, Pokemon.id == pokemon_types.c.pokemon_id)
        .filter(Pokemon.generation.isnot(None))
        .group_by(Pokemon.generation, Type.name)
        .order_by(Pokemon.generation, func.count(Pokemon.id).desc())
        .all()
    )

    dist_by_gen: dict[int, list[TypeDistribution]] = defaultdict(list)
    for row in type_rows:
        gen_total = totals_by_gen.get(row.generation) or 0
        dist_by_gen[row.generation].append(
            TypeDistribution(
                type_name=row.name,
                count=row.count,
                percentage=round(row.count / gen_total * 100, 1) if gen_total else 0,
                avg_stat_total=round(row.avg_st, 1),
            )
        )

    return [
        GenerationStats(
            generation=gen.generation,
            total_pokemon=gen.total,
            avg_stat_total=round(gen.avg_stat_total, 1),
            legendary_count=gen.legendary_count or 0,
            mythical_count=gen.mythical_count or 0,
            type_distribution=dist_by_gen.get(gen.generation, []),
        )
        for gen in generations
    ]
