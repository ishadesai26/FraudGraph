import React from 'react';

export function RiskBadge({ level = 'LOW', score = null, size = 'md' }) {
  const normLevel = (level || 'LOW').toUpperCase();

  const config = {
    CRITICAL: {
      bg: 'rgba(239, 68, 68, 0.15)',
      text: '#F87171',
      border: 'rgba(239, 68, 68, 0.4)',
      dot: '#EF4444',
      label: 'CRITICAL',
    },
    HIGH: {
      bg: 'rgba(249, 115, 22, 0.15)',
      text: '#FB923C',
      border: 'rgba(249, 115, 22, 0.4)',
      dot: '#F97316',
      label: 'HIGH',
    },
    MEDIUM: {
      bg: 'rgba(245, 158, 11, 0.15)',
      text: '#FBBF24',
      border: 'rgba(245, 158, 11, 0.4)',
      dot: '#F59E0B',
      label: 'MEDIUM',
    },
    LOW: {
      bg: 'rgba(16, 185, 129, 0.15)',
      text: '#34D399',
      border: 'rgba(16, 185, 129, 0.4)',
      dot: '#10B981',
      label: 'LOW',
    },
  }[normLevel] || {
    bg: 'rgba(100, 116, 139, 0.15)',
    text: '#94A3B8',
    border: 'rgba(100, 116, 139, 0.4)',
    dot: '#64748B',
    label: normLevel,
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 font-medium',
    md: 'text-xs px-2.5 py-1 font-semibold',
    lg: 'text-sm px-3.5 py-1.5 font-bold',
  }[size] || 'text-xs px-2.5 py-1';

  return (
    <span
      style={{
        backgroundColor: config.bg,
        color: config.text,
        borderColor: config.border,
      }}
      className={`inline-flex items-center gap-1.5 rounded-full border ${sizeClasses} tracking-wide uppercase transition-colors`}
    >
      <span
        style={{ backgroundColor: config.dot }}
        className="w-1.5 h-1.5 rounded-full animate-pulse"
      />
      <span>{config.label}</span>
      {score !== null && (
        <span className="font-mono opacity-85 font-normal ml-0.5">
          ({typeof score === 'number' ? score.toFixed(1) : score})
        </span>
      )}
    </span>
  );
}

export default RiskBadge;
