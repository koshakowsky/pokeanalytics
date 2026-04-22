from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc, desc, func, or_
from models import Pokemon, Type
from schemas import PokemonSearchParams, PaginatedResponse, PokemonListItem


def get_pokemon_list(db: Session, params: PokemonSearchParams) -> PaginatedResponse:
    query = db.query(Pokemon).options(joinedload(Pokemon.types))
    
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
    
    # --- Sorting ---
    sort_column = getattr(Pokemon, params.sort_by, Pokemon.id)
    order_func = desc if params.sort_order == "desc" else asc
    query = query.order_by(order_func(sort_column))
    
    # --- Pagination ---
    items = query.offset(params.offset).limit(params.limit).all()
    
    seen = set()
    unique_items = []
    for item in items:
        if item.id not in seen:
            seen.add(item.id)
            unique_items.append(item)
    
    return PaginatedResponse(
        items=[PokemonListItem.model_validate(p) for p in unique_items],
        total=total,
        limit=params.limit,
        offset=params.offset,
        has_more=(params.offset + params.limit) < total
    )


def get_pokemon_detail(db: Session, pokemon_id: int) -> Pokemon | None:
    return (
        db.query(Pokemon)
        .options(
            joinedload(Pokemon.types),
            joinedload(Pokemon.abilities),
            joinedload(Pokemon.egg_groups),
        )
        .filter(Pokemon.id == pokemon_id)
        .first()
    )


def search_pokemon(db: Session, params: PokemonSearchParams) -> PaginatedResponse:
    return get_pokemon_list(db, params)