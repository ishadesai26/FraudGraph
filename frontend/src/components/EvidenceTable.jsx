import React from 'react';
import { AlertTriangle, ShieldCheck, Cpu, Network, CheckCircle2 } from 'lucide-react';
import RiskBadge from './RiskBadge';

export function EvidenceTable({ evidence = [], protectiveFactors = [], contributingSignals = [] }) {
  return (
    <div className="space-y-4">
      {/* Primary Evidence Section */}
      <div className="soc-panel p-4 space-y-3">
        <div className="flex items-center justify-between pb-2.5 border-b border-soc-border">
          <div className="flex items-center gap-2">
            <AlertTriangle className="text-amber-400" size={16} />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
              FORENSIC EVIDENCE & RISK SIGNALS
            </h3>
          </div>
          <span className="text-[11px] text-slate-400 font-mono">
            {evidence.length} Identified Signals
          </span>
        </div>

        {evidence.length === 0 ? (
          <p className="text-xs text-slate-400 italic py-2">No suspicious signals recorded for this entity.</p>
        ) : (
          <div className="space-y-2">
            {evidence.map((item, idx) => {
              const isGraph = item.source === 'GRAPH_NETWORK';
              return (
                <div
                  key={idx}
                  className="p-3 rounded bg-soc-surface border border-soc-border hover:border-slate-700 transition-colors space-y-2"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="p-1 rounded bg-[#0D131F] border border-soc-border text-slate-300">
                        {isGraph ? <Network size={13} className="text-cyan-400" /> : <Cpu size={13} className="text-amber-400" />}
                      </span>
                      <span className="text-xs font-mono font-bold text-slate-200 uppercase tracking-tight">
                        {item.signal.replace(/_/g, ' ')}
                      </span>
                      {item.source && (
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-[#0D131F] text-slate-400 border border-soc-border font-mono">
                          {item.source}
                        </span>
                      )}
                    </div>
                    <RiskBadge level={item.severity || 'MEDIUM'} size="sm" />
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">{item.description}</p>

                  {(item.value !== undefined || item.importance !== undefined) && (
                    <div className="flex items-center gap-4 text-[11px] text-slate-400 pt-1 font-mono border-t border-soc-border/60">
                      {item.value !== undefined && (
                        <span>Value: <strong className="text-slate-200">{String(item.value)}</strong></span>
                      )}
                      {item.importance !== undefined && (
                        <span className="flex items-center gap-1.5">
                          <span>Weight:</span>
                          <strong className="text-cyan-400">{(item.importance * 100).toFixed(1)}%</strong>
                        </span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Contributing Multi-Factor Quantitative Weights */}
      {contributingSignals.length > 0 && (
        <div className="soc-panel p-4 space-y-3">
          <div className="flex items-center gap-2 pb-2.5 border-b border-soc-border">
            <Cpu className="text-cyan-400" size={16} />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
              QUANTITATIVE MODEL & GRAPH CONTRIBUTIONS
            </h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {contributingSignals.map((sig, idx) => (
              <div key={idx} className="p-3 bg-soc-surface border border-soc-border rounded space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-300 font-mono font-semibold text-[11px]">
                    {sig.name.replace(/_/g, ' ')}
                  </span>
                  <span className="font-mono text-cyan-400 font-bold text-[10px]">
                    {(sig.importance * 100).toFixed(0)}% wt
                  </span>
                </div>
                <div className="text-lg font-bold font-mono text-slate-100">
                  {sig.value.toFixed(1)} <span className="text-xs font-normal text-slate-400">/ 100</span>
                </div>
                <div className="w-full bg-[#080B11] rounded-full h-1.5 overflow-hidden border border-soc-border">
                  <div
                    className="bg-cyan-500 h-full rounded-full transition-all duration-300"
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
        <div className="soc-panel p-4 space-y-2.5 border-emerald-500/20 bg-emerald-950/5">
          <div className="flex items-center gap-2 pb-2 border-b border-emerald-900/30">
            <CheckCircle2 className="text-emerald-400" size={15} />
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 font-mono">
              MITIGATING & PROTECTIVE FACTORS
            </h3>
          </div>
          <div className="space-y-1.5">
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
