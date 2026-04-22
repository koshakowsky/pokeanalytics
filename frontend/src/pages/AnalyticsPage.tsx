import React, { useState, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import type { ColDef } from 'ag-grid-community';
import { gridTheme } from '../setupGrid';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts';
import { fetchCategories, fetchTypeDistribution, fetchGenerationStats } from '../api/pokemonApi';
import type { CategoryStat, TypeDistribution, GenerationStats } from '../types/pokemon';
import { colors, typography, spacing, radius, shadows, transitions, TYPE_COLORS, CHART_COLORS } from '../styles/tokens';

const cardStyle: React.CSSProperties = {
  background: colors.white, borderRadius: radius.xl, padding: spacing.lg,
  boxShadow: shadows.md, border: `1px solid ${colors.gray200}`,
};

const AnalyticsPage: React.FC = () => {
  const [groupBy, setGroupBy] = useState('type');
  const [categories, setCategories] = useState<CategoryStat[]>([]);
  const [typeDist, setTypeDist] = useState<TypeDistribution[]>([]);
  const [genStats, setGenStats] = useState<GenerationStats[]>([]);

  useEffect(() => { fetchCategories(groupBy).then(setCategories); }, [groupBy]);
  useEffect(() => { fetchTypeDistribution().then(setTypeDist); fetchGenerationStats().then(setGenStats); }, []);

  const colDefs: ColDef<CategoryStat>[] = [
    { headerName: 'Category', field: 'category', flex: 1, minWidth: 110, sortable: true,
      cellStyle: { textTransform: 'capitalize', fontWeight: typography.fontWeight.semibold, color: colors.gray900 } },
    { headerName: 'Quantity', field: 'count', width: 72, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'Avg Total', field: 'avg_stat_total', width: 85, sortable: true,
      cellStyle: { fontWeight: typography.fontWeight.bold, fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'HP', field: 'avg_hp', width: 60, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'ATK', field: 'avg_attack', width: 60, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'DEF', field: 'avg_defense', width: 60, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'SpA', field: 'avg_sp_attack', width: 60, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'SpD', field: 'avg_sp_defense', width: 60, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'SPD', field: 'avg_speed', width: 60, sortable: true, cellStyle: { fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'Min', field: 'min_stat_total', width: 56, sortable: true, cellStyle: { color: colors.gray400, fontVariantNumeric: 'tabular-nums' } },
    { headerName: 'Max', field: 'max_stat_total', width: 56, sortable: true, cellStyle: { color: colors.gray400, fontVariantNumeric: 'tabular-nums' } },
  ];

  const groups = [
    { v: 'type', l: 'Type', icon: '🏷️' },
    { v: 'color', l: 'Color', icon: '🎨' },
    { v: 'generation', l: 'Generation', icon: '📅' },
    { v: 'habitat', l: 'Habitat', icon: '🌍' },
    { v: 'shape', l: 'Shape', icon: '📐' },
    { v: 'growth_rate', l: 'Growth rate', icon: '📈' },
  ];

  const tooltipStyle = {
    contentStyle: {
      background: colors.gray900, border: 'none', borderRadius: radius.md,
      fontSize: typography.fontSize.sm, color: colors.white, padding: '8px 12px',
      boxShadow: shadows.lg,
    },
    itemStyle: { color: colors.gray200 },
  };

  return (
    <div>
      <div style={{ marginBottom: spacing.xl }}>
        <h1 style={{
          fontSize: typography.fontSize['3xl'], fontWeight: typography.fontWeight.extrabold,
          color: colors.gray900, letterSpacing: '-0.03em', marginBottom: 4,
        }}>Category analysis</h1>
        <p style={{ fontSize: typography.fontSize.md, color: colors.gray500 }}>
          Explore Pokemon stats for various attributes
        </p>
      </div>

      {/* ── Group buttons ── */}
      <div style={{ display: 'flex', gap: spacing.sm, flexWrap: 'wrap', marginBottom: spacing.lg }}>
        {groups.map(g => (
          <button key={g.v} onClick={() => setGroupBy(g.v)} style={{
            padding: `${spacing.sm}px ${spacing.base}px`,
            borderRadius: radius.lg, cursor: 'pointer',
            fontSize: typography.fontSize.sm, fontWeight: typography.fontWeight.medium,
            fontFamily: typography.fontFamily, transition: transitions.fast,
            display: 'flex', alignItems: 'center', gap: spacing.xs,
            border: groupBy === g.v ? `2px solid ${colors.primary500}` : `1px solid ${colors.gray200}`,
            background: groupBy === g.v ? colors.primary50 : colors.white,
            color: groupBy === g.v ? colors.primary700 : colors.gray600,
            boxShadow: groupBy === g.v ? shadows.glow(colors.primary500) : 'none',
          }}>
            <span>{g.icon}</span>{g.l}
          </button>
        ))}
      </div>

      {/* ── Table ── */}
      <div style={{ ...cardStyle, padding: 0, overflow: 'hidden', height: 380, marginBottom: spacing.xl }}>
        <AgGridReact<CategoryStat>
          theme={gridTheme}
          rowData={categories} columnDefs={colDefs}
          defaultColDef={{ resizable: true }} animateRows />
      </div>

      {/* ── Charts ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.xl }}>
        <div style={cardStyle}>
          <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: typography.fontWeight.bold, color: colors.gray900, marginBottom: spacing.base }}>
            Average Total Stats
          </h3>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={categories.slice(0, 12)} margin={{ bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={colors.gray100} />
              <XAxis dataKey="category" angle={-45} textAnchor="end" height={80}
                style={{ fontSize: 11, fontFamily: typography.fontFamily }} tick={{ fill: colors.gray500 }} />
              <YAxis tick={{ fill: colors.gray400, fontSize: 11 }} />
              <Tooltip {...tooltipStyle} />
              <Bar dataKey="avg_stat_total" fill={colors.primary500} radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={cardStyle}>
          <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: typography.fontWeight.bold, color: colors.gray900, marginBottom: spacing.base }}>
            By type
          </h3>
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie data={typeDist} dataKey="count" nameKey="type_name" cx="50%" cy="50%"
                outerRadius={110} innerRadius={50}
                label={({ type_name, percentage }: any) => `${type_name} ${percentage}%`}
                style={{ fontSize: 11, fontFamily: typography.fontFamily }}>
                {typeDist.map((e, i) => (
                  <Cell key={e.type_name} fill={TYPE_COLORS[e.type_name] || CHART_COLORS[i % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip {...tooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div style={{ ...cardStyle, gridColumn: '1 / -1' }}>
          <h3 style={{ fontSize: typography.fontSize.lg, fontWeight: typography.fontWeight.bold, color: colors.gray900, marginBottom: spacing.base }}>
            Pokemons by generation
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={genStats}>
              <CartesianGrid strokeDasharray="3 3" stroke={colors.gray100} />
              <XAxis dataKey="generation" tick={{ fill: colors.gray500, fontSize: 12 }} />
              <YAxis tick={{ fill: colors.gray400, fontSize: 11 }} />
              <Tooltip {...tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 12, fontFamily: typography.fontFamily }} />
              <Bar dataKey="total_pokemon" name="Total" fill={colors.primary500} radius={[4,4,0,0]} />
              <Bar dataKey="legendary_count" name="Legendary" fill={colors.accent500} radius={[4,4,0,0]} />
              <Bar dataKey="mythical_count" name="Mythical" fill="#ec4899" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
