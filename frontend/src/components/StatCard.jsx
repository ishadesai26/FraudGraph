import React from 'react';

export function StatCard({ title, value, subtext, icon: Icon, color = 'cyan', badge = null }) {
  const colorStyles = {
    cyan: { text: '#06B6D4', bg: 'rgba(6, 182, 212, 0.1)', border: 'rgba(6, 182, 212, 0.25)' },
    red: { text: '#EF4444', bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.25)' },
    orange: { text: '#F97316', bg: 'rgba(249, 115, 22, 0.1)', border: 'rgba(249, 115, 22, 0.25)' },
    purple: { text: '#8B5CF6', bg: 'rgba(139, 92, 246, 0.1)', border: 'rgba(139, 92, 246, 0.25)' },
    emerald: { text: '#10B981', bg: 'rgba(16, 185, 129, 0.1)', border: 'rgba(16, 185, 129, 0.25)' },
  }[color] || { text: '#06B6D4', bg: 'rgba(6, 182, 212, 0.1)', border: 'rgba(6, 182, 212, 0.25)' };

  return (
    <div className="glass-card p-5 relative overflow-hidden flex flex-col justify-between">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-bold font-mono text-slate-50 mt-1 tracking-tight">{value}</h3>
        </div>
        {Icon && (
          <div
            style={{ backgroundColor: colorStyles.bg, borderColor: colorStyles.border }}
            className="p-2.5 rounded-xl border flex items-center justify-center text-slate-100"
          >
            <Icon size={20} style={{ color: colorStyles.text }} />
          </div>
        )}
      </div>
      {(subtext || badge) && (
        <div className="mt-4 flex items-center justify-between pt-3 border-t border-slate-800/80 text-xs text-slate-400">
          <span>{subtext}</span>
          {badge && <div>{badge}</div>}
        </div>
      )}
    </div>
  );
}

export default StatCard;
