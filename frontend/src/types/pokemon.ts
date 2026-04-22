export interface PokemonType {
  id: number;
  name: string;
}

export interface PokemonAbility {
  id: number;
  name: string;
  short_effect?: string;
}

export interface PokemonListItem {
  id: number;
  name: string;
  sprite_url?: string;
  types: PokemonType[];
  stat_total: number;
  generation?: number;
  is_legendary: boolean;
  is_mythical: boolean;
  hp: number;
  attack: number;
  defense: number;
  sp_attack: number;
  sp_defense: number;
  speed: number;
}

export interface PokemonDetail extends PokemonListItem {
  height?: number;
  weight?: number;
  base_experience?: number;
  sprite_official?: string;
  is_baby: boolean;
  habitat?: string;
  color?: string;
  shape?: string;
  growth_rate?: string;
  capture_rate?: number;
  base_happiness?: number;
  gender_rate?: number;
  abilities: PokemonAbility[];
  egg_groups: { id: number; name: string }[];
  height_m?: number;
  weight_kg?: number;
}

export interface PaginatedResponse {
  items: PokemonListItem[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface CategoryStat {
  category: string;
  count: number;
  avg_stat_total: number;
  avg_hp: number;
  avg_attack: number;
  avg_defense: number;
  avg_sp_attack: number;
  avg_sp_defense: number;
  avg_speed: number;
  min_stat_total: number;
  max_stat_total: number;
}

export interface TypeDistribution {
  type_name: string;
  count: number;
  percentage: number;
  avg_stat_total: number;
}

export interface GenerationStats {
  generation: number;
  total_pokemon: number;
  avg_stat_total: number;
  legendary_count: number;
  mythical_count: number;
  type_distribution: TypeDistribution[];
}

export interface SimilarPokemon {
  pokemon: PokemonListItem;
  similarity_score: number;
  matching_types: string[];
  stat_difference: number;
}

export interface CompareResponse {
  pokemon: PokemonDetail[];
  stat_comparison: Record<string, {
    values: Record<string, number>;
    max: number;
    min: number;
    leader: string[];
    spread: number;
  }>;
  advantages: Record<string, Record<string, any>>;
}

export interface SearchFilters {
  name?: string;
  types?: string[];
  generation?: number;
  is_legendary?: boolean;
  min_stat_total?: number;
  max_stat_total?: number;
  min_attack?: number;
  min_defense?: number;
  min_speed?: number;
  sort_by?: string;
  sort_order?: string;
}

