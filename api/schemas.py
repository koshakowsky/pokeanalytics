from pydantic import BaseModel, computed_field
from typing import Optional


# --- Base ---

class TypeSchema(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True


class AbilitySchema(BaseModel):
    id: int
    name: str
    short_effect: Optional[str] = None
    
    class Config:
        from_attributes = True


class EggGroupSchema(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True


class MoveSchema(BaseModel):
    id: int
    name: str
    power: Optional[int] = None
    accuracy: Optional[int] = None
    pp: Optional[int] = None
    damage_class: Optional[str] = None
    type: Optional[TypeSchema] = None
    
    class Config:
        from_attributes = True


# --- Pokemon ---

class PokemonListItem(BaseModel):
    id: int
    name: str
    sprite_url: Optional[str] = None
    types: list[TypeSchema] = []
    stat_total: int
    generation: Optional[int] = None
    is_legendary: bool = False
    is_mythical: bool = False
    hp: int = 0
    attack: int = 0
    defense: int = 0
    sp_attack: int = 0
    sp_defense: int = 0
    speed: int = 0
    
    class Config:
        from_attributes = True


class PokemonDetail(BaseModel):
    id: int
    name: str
    height: Optional[int] = None
    weight: Optional[int] = None
    base_experience: Optional[int] = None
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int
    stat_total: int
    sprite_url: Optional[str] = None
    sprite_official: Optional[str] = None
    generation: Optional[int] = None
    is_legendary: bool
    is_mythical: bool
    is_baby: bool
    habitat: Optional[str] = None
    color: Optional[str] = None
    shape: Optional[str] = None
    growth_rate: Optional[str] = None
    capture_rate: Optional[int] = None
    base_happiness: Optional[int] = None
    gender_rate: Optional[int] = None
    types: list[TypeSchema] = []
    abilities: list[AbilitySchema] = []
    egg_groups: list[EggGroupSchema] = []
    
    @computed_field
    @property
    def height_m(self) -> Optional[float]:
        return round(self.height / 10, 1) if self.height else None
    
    @computed_field
    @property
    def weight_kg(self) -> Optional[float]:
        return round(self.weight / 10, 1) if self.weight else None
    
    class Config:
        from_attributes = True


# --- Filters and queries ---

class PokemonSearchParams(BaseModel):
    name: Optional[str] = None
    types: Optional[list[str]] = None
    generation: Optional[int] = None
    is_legendary: Optional[bool] = None
    is_mythical: Optional[bool] = None
    min_stat_total: Optional[int] = None
    max_stat_total: Optional[int] = None
    min_hp: Optional[int] = None
    max_hp: Optional[int] = None
    min_attack: Optional[int] = None
    max_attack: Optional[int] = None
    min_defense: Optional[int] = None
    max_defense: Optional[int] = None
    min_speed: Optional[int] = None
    max_speed: Optional[int] = None
    habitat: Optional[str] = None
    color: Optional[str] = None
    sort_by: str = "id"
    sort_order: str = "asc"
    limit: int = 50
    offset: int = 0


class CompareRequest(BaseModel):
    pokemon_ids: list[int]


# --- Analytics ---

class CategoryStat(BaseModel):
    category: str
    count: int
    avg_stat_total: float
    avg_hp: float
    avg_attack: float
    avg_defense: float
    avg_sp_attack: float
    avg_sp_defense: float
    avg_speed: float
    min_stat_total: int
    max_stat_total: int


class TypeDistribution(BaseModel):
    type_name: str
    count: int
    percentage: float
    avg_stat_total: float


class GenerationStats(BaseModel):
    generation: int
    total_pokemon: int
    avg_stat_total: float
    legendary_count: int
    mythical_count: int
    type_distribution: list[TypeDistribution]


class SimilarPokemon(BaseModel):
    pokemon: PokemonListItem
    similarity_score: float
    matching_types: list[str]
    stat_difference: float


# --- Paginated response ---

class PaginatedResponse(BaseModel):
    items: list[PokemonListItem]
    total: int
    limit: int
    offset: int
    has_more: bool


class CompareResponse(BaseModel):
    pokemon: list[PokemonDetail]
    stat_comparison: dict
    advantages: dict


class TypeEffectivenessSchema(BaseModel):
    attacking_type: str
    defending_type: str
    multiplier: float
    
    class Config:
        from_attributes = True