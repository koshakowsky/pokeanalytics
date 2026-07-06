import numpy as np
from sqlalchemy.orm import Session, selectinload
from models import Pokemon
from schemas import SimilarPokemon, PokemonListItem

# Theoretical maximum L2 distance between two 6-dim stat vectors capped at 255.
_MAX_STAT_DIFF = float(np.linalg.norm(np.full(6, 255.0)))


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
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


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
    - Cosine + magnitude similarity by stats (50%)
    - Type matching (30%)
    - Meta matching: generation, habitat, color, legendary flag (20%)

    Stat similarity is computed in a single vectorized pass over all candidates.
    """
    target = (
        db.query(Pokemon)
        .options(selectinload(Pokemon.types))
        .filter(Pokemon.id == pokemon_id)
        .first()
    )
    if not target:
        return []

    target_types = {t.name for t in target.types}
    target_vec = compute_stat_vector(target)

    candidates = (
        db.query(Pokemon)
        .options(selectinload(Pokemon.types))
        .filter(Pokemon.id != pokemon_id)
        .all()
    )
    if not candidates:
        return []

    # --- Vectorized stat similarity ---
    cand_matrix = np.array([compute_stat_vector(c) for c in candidates])  # (N, 6)
    target_norm = np.linalg.norm(target_vec)
    cand_norms = np.linalg.norm(cand_matrix, axis=1)

    dots = cand_matrix @ target_vec
    denom = cand_norms * target_norm
    cosine = np.divide(dots, denom, out=np.zeros_like(dots), where=denom != 0)

    stat_diffs = np.linalg.norm(cand_matrix - target_vec, axis=1)
    magnitude_sim = 1.0 - (stat_diffs / _MAX_STAT_DIFF)
    combined_stat_sim = 0.6 * cosine + 0.4 * magnitude_sim

    scored = []
    for i, candidate in enumerate(candidates):
        candidate_types = {t.name for t in candidate.types}

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
            stat_weight * float(combined_stat_sim[i]) +
            same_type_weight * type_sim +
            meta_weight * meta_sim
        )

        scored.append(
            (candidate, total_score, list(type_intersection), float(stat_diffs[i]))
        )

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
