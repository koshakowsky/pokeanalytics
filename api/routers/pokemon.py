from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from schemas import (
    PokemonSearchParams, PaginatedResponse, PokemonDetail, SimilarPokemon
)
from services.pokemon_service import get_pokemon_list, get_pokemon_detail
from services.similarity_service import find_similar_pokemon

router = APIRouter(prefix="/api/pokemon", tags=["Pokemon"])


def search_params(
    name: Optional[str] = None,
    types: Optional[str] = Query(None, description="Comma-separated type names"),
    generation: Optional[int] = None,
    is_legendary: Optional[bool] = None,
    is_mythical: Optional[bool] = None,
    min_stat_total: Optional[int] = None,
    max_stat_total: Optional[int] = None,
    min_hp: Optional[int] = None,
    max_hp: Optional[int] = None,
    min_attack: Optional[int] = None,
    max_attack: Optional[int] = None,
    min_defense: Optional[int] = None,
    max_defense: Optional[int] = None,
    min_speed: Optional[int] = None,
    max_speed: Optional[int] = None,
    habitat: Optional[str] = None,
    color: Optional[str] = None,
    sort_by: str = "stat_total",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PokemonSearchParams:
    """Shared query-parameter parsing for the list/search endpoints."""
    return PokemonSearchParams(
        name=name,
        types=[t.strip() for t in types.split(",") if t.strip()] if types else None,
        generation=generation,
        is_legendary=is_legendary,
        is_mythical=is_mythical,
        min_stat_total=min_stat_total,
        max_stat_total=max_stat_total,
        min_hp=min_hp,
        max_hp=max_hp,
        min_attack=min_attack,
        max_attack=max_attack,
        min_defense=min_defense,
        max_defense=max_defense,
        min_speed=min_speed,
        max_speed=max_speed,
        habitat=habitat,
        color=color,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )


@router.get("/", response_model=PaginatedResponse)
def list_pokemon(
    params: PokemonSearchParams = Depends(search_params),
    db: Session = Depends(get_db),
):
    return get_pokemon_list(db, params)


# Kept as an explicit alias so existing clients hitting /search keep working.
@router.get("/search", response_model=PaginatedResponse)
def search(
    params: PokemonSearchParams = Depends(search_params),
    db: Session = Depends(get_db),
):
    """Search Pokemon by params - full stat."""
    return get_pokemon_list(db, params)


@router.get("/{pokemon_id}", response_model=PokemonDetail)
def detail(pokemon_id: int, db: Session = Depends(get_db)):
    pokemon = get_pokemon_detail(db, pokemon_id)
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    return PokemonDetail.model_validate(pokemon)


@router.get("/{pokemon_id}/similar", response_model=list[SimilarPokemon])
def similar(
    pokemon_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    results = find_similar_pokemon(db, pokemon_id, limit=limit)
    if not results:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    return results
