import React, { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { gridTheme } from '../setupGrid';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Radar, Legend, Tooltip, ResponsiveContainer,
} from 'recharts';
import { fetchPokemonList, fetchPokemonDetail, fetchSimilarPokemon } from '../api/pokemonApi';
import type { PokemonListItem, PokemonDetail, SimilarPokemon, PokemonType } from '../types/pokemon';
import TypeBadge from '../components/shared/TypeBadge';
import StatBar from '../components/shared/StatBar';
import { colors, typography, spacing, radius, transitions, CHART_COLORS } from '../styles/tokens';
import {
  card, searchInputStyle, dropdownPanel, dropdownRow,
  pageTitle, pageSubtitle, errorBanner,
} from '../styles/ui';

const SimilarPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [hints, setHints] = useState<PokemonListItem[]>([]);
  const [target, setTarget] = useState<PokemonDetail | null>(null);
  const [similar, setSimilar] = useState<SimilarPokemon[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (query.length < 1) { setHints([]); return; }
    const t = setTimeout(async () => {
      try { const d = await fetchPokemonList({ name: query, limit: 8, offset: 0 }); setHints(d.items); }
      catch (e) { console.error(e); }
    }, 300);
    return () => clearTimeout(t);
  }, [query]);

  const pick = async (p: PokemonListItem) => {
    setQuery(''); setHints([]); setBusy(true); setError(null);
    try {
      const [det, sim] = await Promise.all([fetchPokemonDetail(p.id), fetchSimilarPokemon(p.id, 12)]);
      setTarget(det); setSimilar(sim);
    } catch (e) { console.error(e); setError('Failed to load similar Pokemon.'); }
    setBusy(false);
  };

  const colDefs: ColDef<SimilarPokemon>[] = [
    { headerName: '', width: 48, sortable: false, cellRenderer: (p: any) => p.data?.pokemon?.sprite_url ? <img src={p.data.pokemon.sprite_url} alt="" style={{ width: 32, height: 32, borderRadius: 4 }} /> : null },
    { headerName: '#', width: 48, valueGetter: (p: any) => p.data?.pokemon?.id, sortable: true, cellStyle: { color: colors.gray400, fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'Name', width: 120, valueGetter: (p: any) => p.data?.pokemon?.name, cellStyle: { fontWeight: typography.fontWeight.semibold, textTransform: 'capitalize', color: colors.gray900 }, sortable: true },
    { headerName: 'Types', width: 150, sortable: false, cellRenderer: (p: any) => (<span>{p.data?.pokemon?.types?.map((t: PokemonType) => <TypeBadge key={t.id} typeName={t.name} size="sm" />)}</span>) },
    {
      headerName: 'Match', field: 'similarity_score', width: 110, sortable: true,
      cellRenderer: (p: any) => {
        const s = p.value; const c = s >= 80 ? colors.success : s >= 60 ? colors.warning : colors.error;
        return (<span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          <span style={{ display: 'inline-block', width: Math.min(s, 100) * 0.5, height: 6, background: c, borderRadius: 3, transition: transitions.slow }} />
          <b style={{ color: c, fontSize: typography.fontSize.sm, fontVariantNumeric: 'tabular-nums' }}>{s}%</b>
        </span>);
      },
    },
    { headerName: 'Shared', field: 'matching_types', width: 110, cellRenderer: (p: any) => (<span>{p.value?.length ? p.value.map((t: string) => <TypeBadge key={t} typeName={t} size="sm" />) : <span style={{ color: colors.gray300, fontSize: typography.fontSize.xs }}>—</span>}</span>) },
    { headerName: 'Total', width: 60, valueGetter: (p: any) => p.data?.pokemon?.stat_total, sortable: true, cellStyle: { fontWeight: typography.fontWeight.bold, fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'Δ', field: 'stat_difference', width: 56, sortable: true, cellStyle: { color: colors.gray400, fontVariantNumeric: 'tabular-nums' } },
  ];

  const radar = target && similar.length > 0
    ? ['HP','ATK','DEF','SpA','SpD','SPD'].map((l, i) => { const k = ['hp','attack','defense','sp_attack','sp_defense','speed'] as const; const r: any = { stat: l, [target.name]: (target as any)[k[i]] }; similar.slice(0, 3).forEach(s => { r[s.pokemon.name] = (s.pokemon as any)[k[i]]; }); return r; })
    : [];

  return (
    <div>
      <div style={{ marginBottom: spacing.xl }}>
        <h1 style={pageTitle}>Find a similar Pokemon</h1>
        <p style={pageSubtitle}>Find Pokemon with similar stats, types, and profiles</p>
      </div>

      {error && <div style={errorBanner}>{error}</div>}

      {/* Search */}
      <div style={{ position: 'relative', maxWidth: 420, marginBottom: spacing.xl }}>
        <input type="text" placeholder="Start typing the Pokemon's name..." value={query} onChange={e => setQuery(e.target.value)}
          data-testid="similar-search" style={searchInputStyle} />
        {hints.length > 0 && (
          <div style={dropdownPanel}>
            {hints.map(p => (
              <div key={p.id} data-testid="similar-suggestion" onClick={() => pick(p)}
                style={dropdownRow}
                onMouseEnter={e => (e.currentTarget.style.background = colors.gray50)} onMouseLeave={e => (e.currentTarget.style.background = colors.white)}>
                {p.sprite_url && <img src={p.sprite_url} alt="" style={{ width: 32, height: 32, marginRight: spacing.sm, borderRadius: 4 }} />}
                <span style={{ textTransform: 'capitalize', fontWeight: typography.fontWeight.medium, color: colors.gray800 }}>#{p.id} {p.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {busy && <p style={{ color: colors.gray500 }}>⏳ Loading...</p>}

      {/* Target card */}
      {target && (
        <div data-testid="target-card" style={card({
          display: 'flex', gap: spacing.xl, padding: spacing.xl,
          marginBottom: spacing.xl, borderLeft: `4px solid ${colors.primary500}`,
        })}>
          <div style={{ textAlign: 'center' }}>
            {target.sprite_official && (
              <div style={{ width: 140, height: 140, borderRadius: radius.xl, background: colors.gray50, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <img src={target.sprite_official} alt="" style={{ width: 120, height: 120 }} />
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'baseline', gap: spacing.xs, justifyContent: 'center', marginTop: spacing.sm }}>
              <span style={{ fontSize: typography.fontSize.sm, color: colors.gray400, fontWeight: typography.fontWeight.semibold }}>#{String(target.id).padStart(3, '0')}</span>
              <h3 style={{ fontSize: typography.fontSize.xl, fontWeight: typography.fontWeight.bold, textTransform: 'capitalize', color: colors.gray900 }}>{target.name}</h3>
            </div>
            <div style={{ marginTop: spacing.xs }}>{target.types.map(t => <TypeBadge key={t.id} typeName={t.name} />)}</div>
          </div>
          <div style={{ flex: 1, maxWidth: 360 }}>
            <h4 style={{ fontSize: typography.fontSize.sm, fontWeight: typography.fontWeight.semibold, color: colors.gray400, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: spacing.sm }}>Base stats</h4>
            {(['hp','attack','defense','sp_attack','sp_defense','speed'] as const).map(s => <StatBar key={s} label={s} value={target[s]} />)}
            <div style={{ marginTop: spacing.md, fontSize: typography.fontSize.sm, color: colors.gray500, display: 'flex', gap: spacing.base, flexWrap: 'wrap' }}>
              <span>📏 {target.height_m}m</span>
              <span>⚖️ {target.weight_kg}kg</span>
              <span>🌍 {target.habitat || '—'}</span>
              <span>📅 Gen {target.generation}</span>
              <span>🎯 Rate: {target.capture_rate}</span>
            </div>
          </div>
        </div>
      )}

      {/* Similar table */}
      {similar.length > 0 && (
        <>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: spacing.sm, marginBottom: spacing.md }}>
            <h2 style={{ fontSize: typography.fontSize['2xl'], fontWeight: typography.fontWeight.bold, color: colors.gray900 }}>Similar Pokemon</h2>
            <span style={{ fontSize: typography.fontSize.md, color: colors.gray400 }}>({similar.length})</span>
          </div>
          <div data-testid="similar-grid" style={card({ overflow: 'hidden', height: 480, marginBottom: spacing.xl })}>
            <AgGridReact<SimilarPokemon> theme={gridTheme} rowData={similar} columnDefs={colDefs} defaultColDef={{ resizable: true }} rowHeight={44} animateRows />
          </div>

          {radar.length > 0 && target && (
            <div data-testid="similar-radar" style={card({ maxWidth: 640, margin: '0 auto', padding: spacing.xl })}>
              <h3 style={{ textAlign: 'center', fontSize: typography.fontSize.lg, fontWeight: typography.fontWeight.bold, color: colors.gray900, marginBottom: spacing.base }}>
                <span style={{ textTransform: 'capitalize' }}>{target.name}</span> vs Top-3 similar
              </h3>
              <ResponsiveContainer width="100%" height={380}>
                <RadarChart data={radar}>
                  <PolarGrid stroke={colors.gray200} />
                  <PolarAngleAxis dataKey="stat" tick={{ fill: colors.gray600, fontSize: 12, fontWeight: 600 }} />
                  <PolarRadiusAxis tick={{ fill: colors.gray400, fontSize: 10 }} />
                  <Radar name={target.name} dataKey={target.name} stroke={CHART_COLORS[0]} fill={CHART_COLORS[0]} fillOpacity={0.15} strokeWidth={3} />
                  {similar.slice(0, 3).map((s, i) => (
                    <Radar key={s.pokemon.id} name={s.pokemon.name} dataKey={s.pokemon.name}
                      stroke={CHART_COLORS[i + 1]} fill={CHART_COLORS[i + 1]} fillOpacity={0.06} strokeWidth={2} />
                  ))}
                  <Legend wrapperStyle={{ fontSize: 12, fontFamily: typography.fontFamily }} />
                  <Tooltip contentStyle={{ background: colors.gray900, border: 'none', borderRadius: radius.md, fontSize: typography.fontSize.sm, color: colors.white }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SimilarPage;
