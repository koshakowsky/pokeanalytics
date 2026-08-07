import { api } from './client';
import type {
  PaginatedResponse, PokemonDetail, CategoryStat,
  TypeDistribution, GenerationStats, SimilarPokemon,
  CompareResponse, PokemonType, SearchFilters,
} from '../types/pokemon';

export const fetchPokemonList = async (
  filters: SearchFilters & { limit?: number; offset?: number }
): Promise<PaginatedResponse> => {
  const params: Record<string, any> = { ...filters };
  if (filters.types && filters.types.length > 0) {
    params.types = filters.types.join(',');
  }
  const { data } = await api.get('/pokemon/', { params });
  return data;
};

export const fetchPokemonSearch = async (
  filters: SearchFilters & { limit?: number; offset?: number }
): Promise<PaginatedResponse> => {
  const params: Record<string, any> = { ...filters };
  if (filters.types && filters.types.length > 0) {
    params.types = filters.types.join(',');
  }
  const { data } = await api.get('/pokemon/search', { params });
  return data;
};

export const fetchPokemonDetail = async (id: number): Promise<PokemonDetail> => {
  const { data } = await api.get(`/pokemon/${id}`);
  return data;
};

export const fetchSimilarPokemon = async (
  id: number, limit: number = 10
): Promise<SimilarPokemon[]> => {
  const { data } = await api.get(`/pokemon/${id}/similar`, { params: { limit } });
  return data;
};

export const fetchCategories = async (groupBy: string = 'type'): Promise<CategoryStat[]> => {
  const { data } = await api.get('/analytics/categories', { params: { group_by: groupBy } });
  return data;
};

export const fetchTypeDistribution = async (): Promise<TypeDistribution[]> => {
  const { data } = await api.get('/analytics/type-distribution');
  return data;
};

export const fetchStatRanges = async (): Promise<Record<string, any>> => {
  const { data } = await api.get('/analytics/stat-ranges');
  return data;
};

export const fetchGenerationStats = async (): Promise<GenerationStats[]> => {
  const { data } = await api.get('/analytics/generation-stats');
  return data;
};

export const comparePokemon = async (pokemonIds: number[]): Promise<CompareResponse> => {
  const { data } = await api.post('/compare/', { pokemon_ids: pokemonIds });
  return data;
};

export const fetchTypes = async (): Promise<PokemonType[]> => {
  const { data } = await api.get('/types/');
  return data;
};
