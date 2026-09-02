import React from 'react';
import { AlertTriangle, ShieldCheck, Cpu, Network, CheckCircle2 } from 'lucide-react';
import RiskBadge from './RiskBadge';

export function EvidenceTable({ evidence = [], protectiveFactors = [], contributingSignals = [] }) {
  return (
    <div className="space-y-6">
      {/* Primary Evidence Section */}
      <div className="glass-panel p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <AlertTriangle className="text-amber-400" size={18} />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Why Flagged? Forensic Evidence Breakdown
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {evidence.length} Identified Signals
          </span>
        </div>

        {evidence.length === 0 ? (
          <p className="text-xs text-slate-400 italic py-3">No suspicious signals recorded for this entity.</p>
        ) : (
          <div className="space-y-3">
            {evidence.map((item, idx) => {
              const isGraph = item.source === 'GRAPH_NETWORK';
              return (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-colors space-y-2"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="p-1 rounded bg-slate-800 text-slate-300">
                        {isGraph ? <Network size={14} className="text-cyan-400" /> : <Cpu size={14} className="text-amber-400" />}
                      </span>
                      <span className="text-xs font-mono font-bold text-slate-200 uppercase">
                        {item.signal.replace(/_/g, ' ')}
                      </span>
                      {item.source && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-400 font-mono">
                          {item.source}
                        </span>
                      )}
                    </div>
                    <RiskBadge level={item.severity || 'MEDIUM'} size="sm" />
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">{item.description}</p>
                  {(item.value !== undefined || item.importance !== undefined) && (
                    <div className="flex items-center gap-4 text-[11px] text-slate-400 pt-1 font-mono">
                      {item.value !== undefined && (
                        <span>Value: <strong className="text-slate-200">{String(item.value)}</strong></span>
                      )}
                      {item.importance !== undefined && (
                        <span>Weight: <strong className="text-slate-200">{(item.importance * 100).toFixed(1)}%</strong></span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Contributing Multi-Factor Signal Weights */}
      {contributingSignals.length > 0 && (
        <div className="glass-panel p-5 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <Cpu className="text-cyan-400" size={18} />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Composite Model & Graph Signal Contributions
            </h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {contributingSignals.map((sig, idx) => (
              <div key={idx} className="p-3 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400 font-medium">{sig.name.replace(/_/g, ' ')}</span>
                  <span className="font-mono text-cyan-400 font-bold">{(sig.importance * 100).toFixed(0)}% wt</span>
                </div>
                <div className="text-lg font-bold font-mono text-slate-100">{sig.value.toFixed(1)} / 100</div>
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-cyan-500 h-full rounded-full"
                    style={{ width: `${Math.min(100, sig.value)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Protective / Mitigating Factors Section */}
      {protectiveFactors.length > 0 && (
        <div className="glass-panel p-5 space-y-3 border-emerald-500/20 bg-emerald-950/10">
          <div className="flex items-center gap-2 pb-2 border-b border-emerald-900/30">
            <CheckCircle2 className="text-emerald-400" size={18} />
            <h3 className="text-sm font-bold uppercase tracking-wider text-emerald-400">
              Mitigating & Protective Factors
            </h3>
          </div>
          <div className="space-y-2">
            {protectiveFactors.map((p, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0"></span>
                <div>
                  <strong className="text-emerald-300 font-mono mr-1">{p.signal}:</strong>
                  <span>{p.description}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default EvidenceTable;
