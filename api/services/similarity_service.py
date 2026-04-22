import numpy as np
from sqlalchemy.orm import Session, joinedload
from models import Pokemon, Type
from schemas import SimilarPokemon, PokemonListItem


def compute_stat_vector(pokemon: Pokemon) -> np.ndarray:
    return np.array([
        pokemon.hp,
        pokemon.attack,
        pokemon.defense,
        pokemon.sp_attack,
        pokemon.sp_defense,
        pokemon.speed,
    ], dtype=float)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def find_similar_pokemon(
    db: Session,
    pokemon_id: int,
    limit: int = 10,
    same_type_weight: float = 0.3,
    stat_weight: float = 0.5,
    meta_weight: float = 0.2,
) -> list[SimilarPokemon]:
    """
    Search for similar Pokemon based on a combined metric:
    - Cosine similarity by stats (50%)
    - Type matching (30%)
    - Metastat matching: generation, habitat, color (20%)
    """
    target = (
        db.query(Pokemon)
        .options(joinedload(Pokemon.types))
        .filter(Pokemon.id == pokemon_id)
        .first()
    )
    if not target:
        return []
    
    target_types = {t.name for t in target.types}
    target_vec = compute_stat_vector(target)
    
    all_pokemon = (
        db.query(Pokemon)
        .options(joinedload(Pokemon.types))
        .filter(Pokemon.id != pokemon_id)
        .all()
    )
    
    seen = set()
    unique_pokemon = []
    for p in all_pokemon:
        if p.id not in seen:
            seen.add(p.id)
            unique_pokemon.append(p)
    
    scored = []
    for candidate in unique_pokemon:
        candidate_types = {t.name for t in candidate.types}
        candidate_vec = compute_stat_vector(candidate)
        
        stat_sim = cosine_similarity(target_vec, candidate_vec)
        
        stat_diff = float(np.linalg.norm(target_vec - candidate_vec))
        max_possible_diff = float(np.linalg.norm(np.array([255]*6)))
        magnitude_sim = 1.0 - (stat_diff / max_possible_diff)
        
        combined_stat_sim = 0.6 * stat_sim + 0.4 * magnitude_sim
        
        type_intersection = target_types & candidate_types
        type_union = target_types | candidate_types
        type_sim = len(type_intersection) / len(type_union) if type_union else 0
        
        meta_score = 0.0
        meta_checks = 0
        
        if target.generation and candidate.generation:
            meta_score += 1.0 if target.generation == candidate.generation else 0.0
            meta_checks += 1
        if target.habitat and candidate.habitat:
            meta_score += 1.0 if target.habitat == candidate.habitat else 0.0
            meta_checks += 1
        if target.color and candidate.color:
            meta_score += 1.0 if target.color == candidate.color else 0.0
            meta_checks += 1
        if target.is_legendary == candidate.is_legendary:
            meta_score += 1.0
            meta_checks += 1
        
        meta_sim = meta_score / meta_checks if meta_checks > 0 else 0
        
        total_score = (
            stat_weight * combined_stat_sim +
            same_type_weight * type_sim +
            meta_weight * meta_sim
        )
        
        scored.append((candidate, total_score, list(type_intersection), stat_diff))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    
    return [
        SimilarPokemon(
            pokemon=PokemonListItem.model_validate(p),
            similarity_score=round(score * 100, 1),
            matching_types=matching,
            stat_difference=round(diff, 1),
        )
        for p, score, matching, diff in scored[:limit]
    ]