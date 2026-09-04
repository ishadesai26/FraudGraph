import React from 'react';

export function RiskBadge({ level = 'LOW', score = null, size = 'md' }) {
  const normLevel = (level || 'LOW').toUpperCase();

  const config = {
    CRITICAL: {
      bg: 'rgba(239, 68, 68, 0.12)',
      text: '#F87171',
      border: 'rgba(239, 68, 68, 0.35)',
      dot: '#EF4444',
      label: 'CRITICAL',
    },
    HIGH: {
      bg: 'rgba(249, 115, 22, 0.12)',
      text: '#FB923C',
      border: 'rgba(249, 115, 22, 0.35)',
      dot: '#F97316',
      label: 'HIGH',
    },
    MEDIUM: {
      bg: 'rgba(245, 158, 11, 0.12)',
      text: '#FBBF24',
      border: 'rgba(245, 158, 11, 0.35)',
      dot: '#F59E0B',
      label: 'MEDIUM',
    },
    LOW: {
      bg: 'rgba(16, 185, 129, 0.12)',
      text: '#34D399',
      border: 'rgba(16, 185, 129, 0.35)',
      dot: '#10B981',
      label: 'LOW',
    },
  }[normLevel] || {
    bg: 'rgba(100, 116, 139, 0.12)',
    text: '#94A3B8',
    border: 'rgba(100, 116, 139, 0.35)',
    dot: '#64748B',
    label: normLevel,
  };

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 font-medium',
    md: 'text-[11px] px-2.5 py-0.5 font-semibold',
    lg: 'text-xs px-3 py-1 font-bold',
  }[size] || 'text-[11px] px-2.5 py-0.5';

  return (
    <span
      style={{
        backgroundColor: config.bg,
        color: config.text,
        borderColor: config.border,
      }}
      className={`inline-flex items-center gap-1.5 rounded border ${sizeClasses} font-mono tracking-wider uppercase transition-colors`}
    >
      <span
        style={{ backgroundColor: config.dot }}
        className="w-1.5 h-1.5 rounded-full animate-soc-pulse flex-shrink-0"
      />
      <span>{config.label}</span>
      {score !== null && score !== undefined && (
        <span className="opacity-90 font-bold ml-0.5">
          {typeof score === 'number' ? score.toFixed(1) : score}
        </span>
      )}
    </span>
  );
}

export default RiskBadge;
