import React from 'react';

export function RiskMeter({ score = 0, level = 'LOW', size = 'lg' }) {
  const normScore = Math.max(0, Math.min(100, Number(score) || 0));
  
  const getColor = (s) => {
    if (s >= 80) return { stroke: '#EF4444', text: '#F87171', glow: 'rgba(239, 68, 68, 0.3)' };
    if (s >= 60) return { stroke: '#F97316', text: '#FB923C', glow: 'rgba(249, 115, 22, 0.3)' };
    if (s >= 35) return { stroke: '#F59E0B', text: '#FBBF24', glow: 'rgba(245, 158, 11, 0.3)' };
    return { stroke: '#10B981', text: '#34D399', glow: 'rgba(16, 185, 129, 0.3)' };
  };

  const colors = getColor(normScore);
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-4 bg-slate-900/60 border border-slate-800 rounded-xl relative overflow-hidden">
      <div className="relative flex items-center justify-center">
        <svg className="w-28 h-28 transform -rotate-90">
          {/* Background Track */}
          <circle
            cx="56"
            cy="56"
            r={radius}
            stroke="#1E293B"
            strokeWidth="8"
            fill="transparent"
          />
          {/* Animated Value Arc */}
          <circle
            cx="56"
            cy="56"
            r={radius}
            stroke={colors.stroke}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{
              transition: 'stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1)',
              filter: `drop-shadow(0 0 6px ${colors.glow})`,
            }}
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-2xl font-black font-mono tracking-tight" style={{ color: colors.text }}>
            {normScore.toFixed(1)}
          </span>
          <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">/ 100</span>
        </div>
      </div>
      <div className="mt-2 text-xs font-semibold uppercase tracking-wider px-2.5 py-0.5 rounded-full" style={{ backgroundColor: `${colors.stroke}20`, color: colors.text }}>
        {level} RISK
      </div>
    </div>
  );
}

export default RiskMeter;
