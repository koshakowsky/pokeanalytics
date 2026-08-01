import React, { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { gridTheme } from '../setupGrid';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Radar, Legend, Tooltip, ResponsiveContainer,
} from 'recharts';
import { fetchPokemonList, comparePokemon } from '../api/pokemonApi';
import type { PokemonListItem, CompareResponse, PokemonType } from '../types/pokemon';
import TypeBadge from '../components/shared/TypeBadge';
import { colors, typography, spacing, radius, shadows, transitions, CHART_COLORS } from '../styles/tokens';
import {
  card, searchInputStyle, dropdownPanel, dropdownRow,
  pageTitle, pageSubtitle, errorBanner,
} from '../styles/ui';

const CLR = CHART_COLORS;

const ComparePage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [hints, setHints] = useState<PokemonListItem[]>([]);
  const [selIds, setSelIds] = useState<number[]>([]);
  const [selPoke, setSelPoke] = useState<PokemonListItem[]>([]);
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (query.length < 1) { setHints([]); return; }
    const t = setTimeout(async () => {
      try {
        const d = await fetchPokemonList({ name: query, limit: 10, offset: 0 });
        setHints(d.items.filter(p => !selIds.includes(p.id)));
      } catch (e) { console.error(e); }
    }, 300);
    return () => clearTimeout(t);
  }, [query, selIds]);

  const add = (p: PokemonListItem) => { if (selIds.length >= 6) return; setSelIds(prev => [...prev, p.id]); setSelPoke(prev => [...prev, p]); setQuery(''); setHints([]); };
  const remove = (id: number) => { setSelIds(prev => prev.filter(x => x !== id)); setSelPoke(prev => prev.filter(x => x.id !== id)); setResult(null); };
  const doCompare = async () => {
    if (selIds.length < 2) return;
    setBusy(true); setError(null);
    try { setResult(await comparePokemon(selIds)); }
    catch (e) { console.error(e); setError('Comparison failed. Please try again.'); }
    setBusy(false);
  };

  const rows = () => {
    if (!result) return [];
    const stats = ['hp','attack','defense','sp_attack','sp_defense','speed','stat_total'];
    const lbl: Record<string,string> = { hp:'HP', attack:'Attack', defense:'Defense', sp_attack:'Sp.Atk', sp_defense:'Sp.Def', speed:'Speed', stat_total:'TOTAL' };
    return stats.map(s => { const r: any = { stat: lbl[s] || s }; const c = result.stat_comparison[s]; if (c) { Object.entries(c.values).forEach(([n,v]) => { r[n] = v; }); r._leader = c.leader; r._spread = c.spread; } return r; });
  };

  const gridCols: ColDef[] = [
    { headerName: 'Stat', field: 'stat', width: 100, pinned: 'left', cellStyle: { fontWeight: typography.fontWeight.semibold, color: colors.gray600 } },
    ...(result?.pokemon || []).map((p, i) => ({
      headerName: p.name.charAt(0).toUpperCase() + p.name.slice(1), field: p.name, width: 110, sortable: true,
      cellStyle: (params: any) => {
        const lead = params.data?._leader?.includes(p.name);
        return { fontWeight: lead ? typography.fontWeight.bold : typography.fontWeight.normal, color: lead ? CLR[i] : colors.gray700, background: lead ? `${CLR[i]}10` : 'transparent', fontVariantNumeric: 'tabular-nums' };
      },
    })),
    { headerName: '±', field: '_spread', width: 56, cellStyle: { color: colors.gray400, fontVariantNumeric: 'tabular-nums' } },
  ];

  const radar = result ? ['HP','ATK','DEF','SpA','SpD','SPD'].map((l, i) => { const k = ['hp','attack','defense','sp_attack','sp_defense','speed'] as const; const r: any = { stat: l }; result.pokemon.forEach(p => { r[p.name] = (p as any)[k[i]]; }); return r; }) : [];

  return (
    <div>
      <div style={{ marginBottom: spacing.xl }}>
        <h1 style={pageTitle}>Compare Pokemon</h1>
        <p style={pageSubtitle}>Select 2 to 6 Pokemon for a detailed stat comparison</p>
      </div>

      {error && <div style={errorBanner}>{error}</div>}

      {/* Search */}
      <div style={{ position: 'relative', maxWidth: 420, marginBottom: spacing.lg }}>
        <input type="text" placeholder="Start typing the Pokemon's name..." value={query} onChange={e => setQuery(e.target.value)}
          data-testid="compare-search" style={searchInputStyle} />
        {hints.length > 0 && (
          <div style={dropdownPanel}>
            {hints.map(p => (
              <div key={p.id} data-testid="compare-suggestion" onClick={() => add(p)} style={dropdownRow}
                onMouseEnter={e => (e.currentTarget.style.background = colors.gray50)} onMouseLeave={e => (e.currentTarget.style.background = colors.white)}>
                {p.sprite_url && <img src={p.sprite_url} alt="" style={{ width: 32, height: 32, marginRight: spacing.sm, borderRadius: 4 }} />}
                <span style={{ textTransform: 'capitalize', fontWeight: typography.fontWeight.medium, color: colors.gray800 }}>#{p.id} {p.name}</span>
                <span style={{ marginLeft: 'auto' }}>{p.types.map(t => <TypeBadge key={t.id} typeName={t.name} size="sm" />)}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Chips */}
      <div style={{ display: 'flex', gap: spacing.sm, flexWrap: 'wrap', marginBottom: spacing.lg }}>
        {selPoke.map((p, i) => (
          <div key={p.id} data-testid="compare-chip" style={{
            display: 'flex', alignItems: 'center', padding: `${spacing.xs}px ${spacing.md}px`, borderRadius: radius.lg,
            border: `2px solid ${CLR[i]}`, background: `${CLR[i]}08`, transition: transitions.fast,
          }}>
            {p.sprite_url && <img src={p.sprite_url} alt="" style={{ width: 32, height: 32, borderRadius: 4 }} />}
            <span style={{ textTransform: 'capitalize', fontWeight: typography.fontWeight.semibold, margin: `0 ${spacing.sm}px`, color: colors.gray800, fontSize: typography.fontSize.md }}>{p.name}</span>
            <button data-testid="compare-chip-remove" onClick={() => remove(p.id)} style={{ background: 'none', border: 'none', color: colors.error, fontSize: 16, cursor: 'pointer', fontWeight: typography.fontWeight.bold, lineHeight: 1, padding: 2 }}>×</button>
          </div>
        ))}
        {selIds.length >= 2 && (
          <button data-testid="compare-run" onClick={doCompare} disabled={busy} style={{
            padding: `${spacing.sm}px ${spacing.xl}px`, borderRadius: radius.lg, border: 'none',
            background: `linear-gradient(135deg, ${colors.primary500}, ${colors.primary600})`,
            color: colors.white, fontWeight: typography.fontWeight.semibold, fontSize: typography.fontSize.md,
            cursor: 'pointer', fontFamily: typography.fontFamily, transition: transitions.fast,
            boxShadow: shadows.glow(colors.primary500),
          }}>
            {busy ? 'Comparing...' : '⚡ Compare'}
          </button>
        )}
      </div>

      {result && (
        <>
          <div data-testid="compare-grid" style={card({ overflow: 'hidden', height: 340, marginBottom: spacing.xl })}>
            <AgGridReact theme={gridTheme} rowData={rows()} columnDefs={gridCols} defaultColDef={{ resizable: true }} animateRows />
          </div>
          <div data-testid="compare-radar" style={card({ maxWidth: 640, margin: '0 auto', padding: spacing.xl })}>
            <h3 style={{ textAlign: 'center', fontSize: typography.fontSize.lg, fontWeight: typography.fontWeight.bold, color: colors.gray900, marginBottom: spacing.base }}>Feature Profiles</h3>
            <ResponsiveContainer width="100%" height={380}>
              <RadarChart data={radar}>
                <PolarGrid stroke={colors.gray200} />
                <PolarAngleAxis dataKey="stat" tick={{ fill: colors.gray600, fontSize: 12, fontWeight: 600 }} />
                <PolarRadiusAxis tick={{ fill: colors.gray400, fontSize: 10 }} />
                {result.pokemon.map((p, i) => (
                  <Radar key={p.id} name={p.name} dataKey={p.name} stroke={CLR[i]} fill={CLR[i]} fillOpacity={0.1} strokeWidth={2} />
                ))}
                <Legend wrapperStyle={{ fontSize: 12, fontFamily: typography.fontFamily }} />
                <Tooltip contentStyle={{ background: colors.gray900, border: 'none', borderRadius: radius.md, fontSize: typography.fontSize.sm, color: colors.white }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
};

export default ComparePage;
