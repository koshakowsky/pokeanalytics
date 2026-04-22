import React, { useState, useEffect, useCallback } from 'react';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { gridTheme } from '../setupGrid';
import { fetchPokemonSearch, fetchTypes, fetchStatRanges } from '../api/pokemonApi';
import type { PokemonType, SearchFilters, PokemonListItem } from '../types/pokemon';
import TypeBadge from '../components/shared/TypeBadge';
import StatBar from '../components/shared/StatBar';
import { colors, typography, spacing, radius, shadows, transitions } from '../styles/tokens';


const card = (extra?: React.CSSProperties): React.CSSProperties => ({
  background: colors.white,
  borderRadius: radius.xl,
  border: `1px solid ${colors.gray200}`,
  boxShadow: shadows.md,
  ...extra,
});

const label: React.CSSProperties = {
  display: 'block', fontSize: typography.fontSize.xs,
  fontWeight: typography.fontWeight.semibold, color: colors.gray400,
  marginBottom: 4, letterSpacing: '0.04em', textTransform: 'uppercase',
};

const input: React.CSSProperties = {
  width: '100%', padding: '8px 12px', borderRadius: radius.sm,
  border: `1px solid ${colors.gray200}`, fontSize: typography.fontSize.md,
  fontFamily: typography.fontFamily, color: colors.gray800,
  background: colors.white, transition: transitions.fast,
  outline: 'none', boxSizing: 'border-box',
};

const SearchPage: React.FC = () => {
  const [types, setTypes] = useState<PokemonType[]>([]);
  const [statRanges, setStatRanges] = useState<Record<string, any>>({});
  const [filters, setFilters] = useState<SearchFilters>({ sort_by: 'stat_total', sort_order: 'desc' });
  const [results, setResults] = useState<PokemonListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<PokemonListItem | null>(null);

  useEffect(() => { fetchTypes().then(setTypes); fetchStatRanges().then(setStatRanges); }, []);

  const doSearch = useCallback(async () => {
    setLoading(true);
    try {
      const clean: Record<string, any> = {};
      Object.entries(filters).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '' && v !== 0) clean[k] = v;
      });
      const data = await fetchPokemonSearch({ ...clean, limit: 100, offset: 0 });
      setResults(data.items); setTotal(data.total);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [filters]);

  useEffect(() => { const t = setTimeout(doSearch, 350); return () => clearTimeout(t); }, [doSearch]);

  const colDefs: ColDef<PokemonListItem>[] = [
    {
      headerName: '', field: 'sprite_url', width: 52, sortable: false,
      cellRenderer: (p: any) => p.value
        ? <img src={p.value} alt="" style={{ width: 32, height: 32, imageRendering: 'pixelated', borderRadius: 4 }} />
        : null,
    },
    { headerName: '#', field: 'id', width: 52, sortable: true,
      cellStyle: { color: colors.gray400, fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'Name', field: 'name', flex: 1, minWidth: 120, sortable: true,
      cellStyle: { fontWeight: typography.fontWeight.semibold, textTransform: 'capitalize', color: colors.gray900 } },
    {
      headerName: 'Types', field: 'types', width: 170, sortable: false,
      cellRenderer: (p: any) => (
        <span>{p.value?.map((t: PokemonType) => <TypeBadge key={t.id} typeName={t.name} size="sm" />)}</span>
      ),
    },
    { headerName: 'Total', field: 'stat_total', width: 68, sortable: true,
      cellStyle: { fontWeight: typography.fontWeight.bold, fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'HP', field: 'hp', width: 54, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'ATK', field: 'attack', width: 54, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'DEF', field: 'defense', width: 54, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'SpA', field: 'sp_attack', width: 54, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'SpD', field: 'sp_defense', width: 54, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'SPD', field: 'speed', width: 54, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'Gen', field: 'generation', width: 48, sortable: true,
      cellStyle: { color: colors.gray400 } },
    {
      headerName: '', width: 72, sortable: false,
      valueGetter: (p: any) => p.data?.is_legendary ? '⭐ Legend' : p.data?.is_mythical ? '✨ Mythic' : '',
      cellStyle: { fontSize: typography.fontSize.xs, color: colors.accent500 },
    },
  ];

  return (
    <div>
      {/* ── Page header ── */}
      <div style={{ marginBottom: spacing.xl }}>
        <h1 style={{
          fontSize: typography.fontSize['3xl'], fontWeight: typography.fontWeight.extrabold,
          color: colors.gray900, letterSpacing: '-0.03em', marginBottom: 4,
        }}>
          Pokemon select
        </h1>
        <p style={{ fontSize: typography.fontSize.md, color: colors.gray500 }}>
          Filter and find Pokemon by stats, types, and generations
        </p>
      </div>

      {/* ── Filters ── */}
      <div style={{
        ...card({ padding: spacing.lg, marginBottom: spacing.lg }),
        display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(170px, 1fr))', gap: spacing.base,
      }}>
        <div>
          <span style={label}>Name</span>
          <input type="text" placeholder="Pikachu..." value={filters.name || ''}
            onChange={e => setFilters(f => ({ ...f, name: e.target.value || undefined }))}
            style={input} />
        </div>
        <div>
          <span style={label}>Type</span>
          <select multiple value={filters.types || []}
            onChange={e => {
              const sel = Array.from(e.target.selectedOptions, o => o.value);
              setFilters(f => ({ ...f, types: sel.length ? sel : undefined }));
            }} style={{ ...input, height: 72, cursor: 'pointer' }}>
            {types.map(t => <option key={t.id} value={t.name} style={{ textTransform: 'capitalize' }}>{t.name}</option>)}
          </select>
        </div>
        <div>
          <span style={label}>Generation</span>
          <select value={filters.generation ?? ''}
            onChange={e => setFilters(f => ({ ...f, generation: e.target.value ? +e.target.value : undefined }))}
            style={{ ...input, cursor: 'pointer' }}>
            <option value="">All</option>
            {[1,2,3,4,5,6,7,8,9].map(g => <option key={g} value={g}>Generation {g}</option>)}
          </select>
        </div>
                <div>
          <span style={label}>Group</span>
          <select
            value={
              filters.is_legendary === true ? 'legendary' :
              (filters as any).is_mythical === true ? 'mythical' :
              filters.is_legendary === false ? 'regular' : ''
            }
            onChange={e => {
              const v = e.target.value;
              setFilters(f => ({
                ...f,
                is_legendary: v === 'legendary' ? true : v === 'regular' ? false : undefined,
                is_mythical: v === 'mythical' ? true : undefined,
              } as any));
            }}
            style={{ ...input, cursor: 'pointer' }}
          >
            <option value="">All</option>
            <option value="legendary">⭐ Legendary</option>
            <option value="mythical">✨ Mythical</option>
            <option value="regular">Regular</option>
          </select>
        </div>
        {[
          { key: 'min_stat_total', name: 'Total', max: statRanges.stat_total?.max ?? 800 },
          { key: 'min_attack', name: 'ATK', max: 200 },
          { key: 'min_defense', name: 'DEF', max: 250 },
          { key: 'min_speed', name: 'SPD', max: 200 },
        ].map(s => (
          <div key={s.key}>
            <span style={label}>min. {s.name}: <span style={{ color: colors.primary500 }}>{(filters as any)[s.key] ?? 0}</span></span>
            <input type="range" min={0} max={s.max}
              value={(filters as any)[s.key] ?? 0}
              onChange={e => {
                const v = +e.target.value;
                setFilters(f => ({ ...f, [s.key]: v > 0 ? v : undefined }));
              }}
              style={{ width: '100%', accentColor: colors.primary500, cursor: 'pointer' }} />
          </div>
        ))}
      </div>

      {/* ── Results bar ── */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        marginBottom: spacing.md,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
          <span style={{
            fontSize: typography.fontSize['2xl'], fontWeight: typography.fontWeight.bold,
            color: colors.gray900, fontVariantNumeric: 'tabular-nums',
          }}>{total}</span>
          <span style={{ fontSize: typography.fontSize.md, color: colors.gray500 }}>Pokemon found</span>
        </div>
        <button onClick={() => setFilters({ sort_by: 'stat_total', sort_order: 'desc' })}
          style={{
            padding: `${spacing.sm}px ${spacing.base}px`, borderRadius: radius.md,
            border: `1px solid ${colors.gray200}`, background: colors.white,
            fontSize: typography.fontSize.sm, fontWeight: typography.fontWeight.medium,
            color: colors.gray600, cursor: 'pointer', transition: transitions.fast,
            fontFamily: typography.fontFamily,
          }}>
          Reset filters
        </button>
      </div>

      {/* ── Grid ── */}
      <div style={{ ...card({ overflow: 'hidden' }), height: 560 }}>
        <AgGridReact<PokemonListItem>
          theme={gridTheme}
          rowData={results} columnDefs={colDefs}
          defaultColDef={{ resizable: true, filter: true }}
          rowHeight={44} animateRows
          rowSelection={{ mode: 'singleRow', checkboxes: false }}
          onRowClicked={e => setSelected(e.data || null)}
          loading={loading}
        />
      </div>

      {/* ── Selected card ── */}
      {selected && (
        <div style={{
          ...card({ padding: spacing.xl, marginTop: spacing.lg }),
          borderLeft: `4px solid ${colors.primary500}`,
        }}>
          <div style={{ display: 'flex', gap: spacing.xl, alignItems: 'flex-start' }}>
            <div style={{ textAlign: 'center' }}>
              {selected.sprite_url && (
                <div style={{
                  width: 96, height: 96, borderRadius: radius.lg,
                  background: colors.gray50, display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <img src={selected.sprite_url} alt="" style={{ width: 80, height: 80, imageRendering: 'pixelated' }} />
                </div>
              )}
              <div style={{ marginTop: spacing.sm }}>
                {selected.types.map(t => <TypeBadge key={t.id} typeName={t.name} size="md" />)}
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: spacing.sm, marginBottom: spacing.md }}>
                <span style={{ fontSize: typography.fontSize.sm, color: colors.gray400, fontWeight: typography.fontWeight.semibold }}>
                  #{String(selected.id).padStart(3, '0')}
                </span>
                <h3 style={{
                  fontSize: typography.fontSize.xl, fontWeight: typography.fontWeight.bold,
                  textTransform: 'capitalize', color: colors.gray900, letterSpacing: '-0.02em',
                }}>
                  {selected.name}
                </h3>
                <span style={{
                  fontSize: typography.fontSize.xs, fontWeight: typography.fontWeight.semibold,
                  color: colors.primary500, background: colors.primary50,
                  padding: '2px 8px', borderRadius: radius.sm,
                }}>
                  Total {selected.stat_total}
                </span>
              </div>
              <div style={{ maxWidth: 380 }}>
                {(['hp','attack','defense','sp_attack','sp_defense','speed'] as const).map(s =>
                  <StatBar key={s} label={s} value={selected[s]} />
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
