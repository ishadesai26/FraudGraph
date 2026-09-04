import React from 'react';

export function RiskMeter({ score = 0, level = 'LOW', size = 'lg' }) {
  const normScore = Math.max(0, Math.min(100, Number(score) || 0));

  const getColor = (s) => {
    if (s >= 80) return { stroke: '#EF4444', text: '#F87171', glow: 'rgba(239, 68, 68, 0.25)', label: 'CRITICAL' };
    if (s >= 60) return { stroke: '#F97316', text: '#FB923C', glow: 'rgba(249, 115, 22, 0.25)', label: 'HIGH' };
    if (s >= 35) return { stroke: '#F59E0B', text: '#FBBF24', glow: 'rgba(245, 158, 11, 0.25)', label: 'MEDIUM' };
    return { stroke: '#10B981', text: '#34D399', glow: 'rgba(16, 185, 129, 0.25)', label: 'LOW' };
  };

  const colors = getColor(normScore);
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-3 bg-soc-panel border border-soc-border rounded relative overflow-hidden">
      <div className="relative flex items-center justify-center">
        <svg className="w-24 h-24 transform -rotate-90">
          {/* Background Track */}
          <circle
            cx="48"
            cy="48"
            r={radius}
            stroke="#162032"
            strokeWidth="6"
            fill="transparent"
          />
          {/* Active Colored Arc */}
          <circle
            cx="48"
            cy="48"
            r={radius}
            stroke={colors.stroke}
            strokeWidth="6"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{
              transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
              filter: `drop-shadow(0 0 4px ${colors.glow})`,
            }}
          />
        </svg>

        {/* Centered Score */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-xl font-extrabold font-mono tracking-tight" style={{ color: colors.text }}>
            {normScore.toFixed(1)}
          </span>
          <span className="text-[9px] text-slate-400 font-mono font-medium uppercase tracking-wider">
            / 100
          </span>
        </div>
      </div>

      <div
        className="mt-1 text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded border"
        style={{
          backgroundColor: `${colors.stroke}15`,
          color: colors.text,
          borderColor: `${colors.stroke}40`,
        }}
      >
        {colors.label} RISK
      </div>
    </div>
  );
}

export default RiskMeter;
