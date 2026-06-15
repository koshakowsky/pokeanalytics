from sqlalchemy.orm import Session, selectinload
from sqlalchemy import asc, desc, func
from models import Pokemon, Type
from schemas import PokemonSearchParams, PaginatedResponse, PokemonListItem

# Columns that are safe to sort by (prevents arbitrary attribute access / 500s).
SORTABLE_COLUMNS = {
    "id", "name", "stat_total", "hp", "attack", "defense",
    "sp_attack", "sp_defense", "speed", "generation",
}


def get_pokemon_list(db: Session, params: PokemonSearchParams) -> PaginatedResponse:
    # selectinload (not joinedload) loads the many-to-many `types` in a separate
    # query, so the main query rows are NOT multiplied. This keeps LIMIT/OFFSET
    # correct and removes the need for manual de-duplication.
    query = db.query(Pokemon).options(selectinload(Pokemon.types))

    # --- Filters ---
    if params.name:
        query = query.filter(Pokemon.name.ilike(f"%{params.name}%"))

    if params.types:
        for type_name in params.types:
            query = query.filter(
                Pokemon.types.any(Type.name == type_name)
            )

    if params.generation is not None:
        query = query.filter(Pokemon.generation == params.generation)

    if params.is_legendary is not None:
        query = query.filter(Pokemon.is_legendary == params.is_legendary)

    if params.is_mythical is not None:
        query = query.filter(Pokemon.is_mythical == params.is_mythical)

    if params.habitat:
        query = query.filter(Pokemon.habitat == params.habitat)

    if params.color:
        query = query.filter(Pokemon.color == params.color)

    stat_filters = [
        ("stat_total", params.min_stat_total, params.max_stat_total),
        ("hp", params.min_hp, params.max_hp),
        ("attack", params.min_attack, params.max_attack),
        ("defense", params.min_defense, params.max_defense),
        ("speed", params.min_speed, params.max_speed),
    ]

    for attr_name, min_val, max_val in stat_filters:
        col = getattr(Pokemon, attr_name)
        if min_val is not None:
            query = query.filter(col >= min_val)
        if max_val is not None:
            query = query.filter(col <= max_val)

    # --- Total calculation ---
    total = query.with_entities(func.count(Pokemon.id)).scalar()

    # --- Sorting (allowlisted to avoid arbitrary attribute access) ---
    sort_by = params.sort_by if params.sort_by in SORTABLE_COLUMNS else "id"
    sort_column = getattr(Pokemon, sort_by)
    order_func = desc if params.sort_order == "desc" else asc
    query = query.order_by(order_func(sort_column))

    # --- Pagination ---
    items = query.offset(params.offset).limit(params.limit).all()

    return PaginatedResponse(
        items=[PokemonListItem.model_validate(p) for p in items],
        total=total,
        limit=params.limit,
        offset=params.offset,
        has_more=(params.offset + params.limit) < total,
    )


def get_pokemon_detail(db: Session, pokemon_id: int) -> Pokemon | None:
    return (
        db.query(Pokemon)
        .options(
            selectinload(Pokemon.types),
            selectinload(Pokemon.abilities),
            selectinload(Pokemon.egg_groups),
        )
        .filter(Pokemon.id == pokemon_id)
        .first()
    )
