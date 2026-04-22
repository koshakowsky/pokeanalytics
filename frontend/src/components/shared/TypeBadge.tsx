import React from 'react';
import { TYPE_COLORS } from '../../styles/tokens';
import { typography, radius } from '../../styles/tokens';

interface Props {
  typeName: string;
  size?: 'sm' | 'md' | 'lg';
}

const TypeBadge: React.FC<Props> = ({ typeName, size = 'md' }) => {
  const bg = TYPE_COLORS[typeName] || '#94a3b8';
  const config = {
    sm: { padding: '1px 7px', fontSize: typography.fontSize.xs, borderRadius: radius.sm },
    md: { padding: '2px 10px', fontSize: typography.fontSize.sm, borderRadius: radius.md },
    lg: { padding: '4px 14px', fontSize: typography.fontSize.base, borderRadius: radius.md },
  };

  return (
    <span style={{
      background: `${bg}18`,
      color: bg,
      border: `1px solid ${bg}40`,
      fontWeight: typography.fontWeight.semibold,
      textTransform: 'uppercase',
      display: 'inline-block',
      marginRight: 4,
      letterSpacing: '0.04em',
      lineHeight: 1.6,
      ...config[size],
    }}>
      {typeName}
    </span>
  );
};

export default TypeBadge;
