import React from 'react';

export function StatCard({ title, value, subtext, icon: Icon, color = 'cyan', badge = null }) {
  const colorMap = {
    cyan: {
      text: '#06B6D4',
      bg: 'rgba(6, 182, 212, 0.08)',
      border: 'rgba(6, 182, 212, 0.25)',
      bar: '#06B6D4',
    },
    red: {
      text: '#EF4444',
      bg: 'rgba(239, 68, 68, 0.08)',
      border: 'rgba(239, 68, 68, 0.25)',
      bar: '#EF4444',
    },
    orange: {
      text: '#F97316',
      bg: 'rgba(249, 115, 22, 0.08)',
      border: 'rgba(249, 115, 22, 0.25)',
      bar: '#F97316',
    },
    purple: {
      text: '#8B5CF6',
      bg: 'rgba(139, 92, 246, 0.08)',
      border: 'rgba(139, 92, 246, 0.25)',
      bar: '#8B5CF6',
    },
    emerald: {
      text: '#10B981',
      bg: 'rgba(16, 185, 129, 0.08)',
      border: 'rgba(16, 185, 129, 0.25)',
      bar: '#10B981',
    },
  }[color] || {
    text: '#06B6D4',
    bg: 'rgba(6, 182, 212, 0.08)',
    border: 'rgba(6, 182, 212, 0.25)',
    bar: '#06B6D4',
  };

  return (
    <div className="soc-card p-4 relative overflow-hidden flex flex-col justify-between border-soc-border hover:border-slate-700 transition-colors">
      {/* Subtle Top Accent Hairline */}
      <div
        className="absolute top-0 left-0 right-0 h-[2px]"
        style={{ backgroundColor: colorMap.bar }}
      />

      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
            {title}
          </p>
          <div className="text-2xl font-bold font-mono text-slate-50 tracking-tight">
            {value}
          </div>
        </div>

        {Icon && (
          <div
            style={{ backgroundColor: colorMap.bg, borderColor: colorMap.border }}
            className="w-8 h-8 rounded border flex items-center justify-center text-slate-100 flex-shrink-0"
          >
            <Icon size={16} style={{ color: colorMap.text }} />
          </div>
        )}
      </div>

      {(subtext || badge) && (
        <div className="mt-3 pt-2.5 border-t border-soc-border/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <span className="truncate">{subtext}</span>
          {badge && <div className="flex-shrink-0 ml-2">{badge}</div>}
        </div>
      )}
    </div>
  );
}

export default StatCard;
