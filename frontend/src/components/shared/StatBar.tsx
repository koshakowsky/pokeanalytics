import React from 'react';
import { colors, typography, transitions } from '../../styles/tokens';

interface Props {
  label: string;
  value: number;
  maxValue?: number;
}

const STAT_COLORS: Record<string, string> = {
  hp: '#ef4444',
  attack: '#f97316',
  defense: '#f59e0b',
  sp_attack: '#3b82f6',
  sp_defense: '#22c55e',
  speed: '#ec4899',
};

const LABELS: Record<string, string> = {
  hp: 'HP', attack: 'ATK', defense: 'DEF',
  sp_attack: 'SP.ATK', sp_defense: 'SP.DEF', speed: 'SPD',
};

const StatBar: React.FC<Props> = ({ label, value, maxValue = 255 }) => {
  const pct = Math.min((value / maxValue) * 100, 100);
  const barColor = STAT_COLORS[label] || colors.primary500;

  return (
    <div style={{ display: 'flex', alignItems: 'center', marginBottom: 6, gap: 8 }}>
      <span style={{
        width: 48, fontSize: typography.fontSize.xs,
        fontWeight: typography.fontWeight.semibold,
        color: colors.gray400, textAlign: 'right',
        letterSpacing: '0.03em',
      }}>
        {LABELS[label] || label}
      </span>
      <span style={{
        width: 30, fontSize: typography.fontSize.sm,
        fontWeight: typography.fontWeight.bold,
        color: colors.gray800, textAlign: 'right',
        fontVariantNumeric: 'tabular-nums',
      }}>
        {value}
      </span>
      <div style={{
        flex: 1, height: 6, background: colors.gray100,
        borderRadius: 3, overflow: 'hidden',
      }}>
        <div style={{
          width: `${pct}%`, height: '100%',
          background: `linear-gradient(90deg, ${barColor}, ${barColor}cc)`,
          borderRadius: 3,
          transition: transitions.slow,
        }} />
      </div>
    </div>
  );
};

export default StatBar;
