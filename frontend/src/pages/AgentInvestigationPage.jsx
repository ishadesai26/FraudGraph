import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Bot,
  Cpu,
  Network,
  Activity,
  Layers,
  Search,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  ShieldAlert,
  ArrowRight,
  ShieldCheck,
  Zap,
  Info,
  SlidersHorizontal,
} from 'lucide-react';
import apiService from '../services/api';
import RiskBadge from '../components/RiskBadge';
import RiskMeter from '../components/RiskMeter';

export function AgentInvestigationPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialType = searchParams.get('type') || 'customer';
  const initialId = searchParams.get('id') || 'CUST_00028';

  const [entityType, setEntityType] = useState(initialType);
  const [entityId, setEntityId] = useState(initialId);
  const [loading, setLoading] = useState(false);
  const [investigation, setInvestigation] = useState(null);
  const [error, setError] = useState(null);
  const [evidenceFilter, setEvidenceFilter] = useState('ALL');

  const runInvestigation = async (type = entityType, id = entityId) => {
    if (!id.trim()) return;
    try {
      setLoading(true);
      setError(null);
      const res = await apiService.investigateWithAgents(type, id.trim());
      setInvestigation(res);
      setSearchParams({ type, id });
    } catch (err) {
      setError(err.message);
      setInvestigation(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialId) {
      runInvestigation(initialType, initialId);
    }
  }, []);

  const agentIcons = {
    RiskAgent: Cpu,
    GraphAgent: Network,
    BehaviorAgent: Activity,
    EvidenceAgent: Layers,
    InvestigatorAgent: Search,
    DecisionAgent: ShieldAlert,
  };

  const filteredEvidence = investigation?.evidence_items?.filter((ev) => {
    if (evidenceFilter === 'ALL') return true;
    return ev.category === evidenceFilter;
  }) || [];

  return (
    <div className="space-y-4 pb-16">
      {/* Header Banner */}
      <div className="soc-panel p-5 relative overflow-hidden bg-gradient-to-r from-[#0D131F] via-[#0D131F] to-[#141228] border-soc-border">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-soc-pulse"></span>
            <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest font-mono">
              PHASE 6 COLLABORATIVE MULTI-AGENT SWARM
            </span>
          </div>
          <h1 className="text-xl md:text-2xl font-extrabold text-slate-100 flex items-center gap-2.5 font-mono">
            <Bot className="text-cyan-400" size={24} />
            AUTONOMOUS AGENTIC FRAUD INVESTIGATION
          </h1>
          <p className="text-xs text-slate-400 font-sans leading-relaxed max-w-3xl">
            Simulate a multidisciplinary team of 6 specialized AI agents collaborating in real time to analyze ML risk scores, graph community topologies, and behavioral velocity with strict evidence provenance and cross-agent conflict adjudication.
          </p>
        </div>
      </div>

      {/* Target Entity Selection & Trigger Bar */}
      <div className="soc-panel p-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={entityType}
              onChange={(e) => setEntityType(e.target.value)}
              className="text-xs font-mono font-semibold bg-soc-surface border border-soc-border rounded px-3 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="customer">Customer Account</option>
              <option value="ring">Fraud Ring Syndicate</option>
              <option value="transaction">Transaction</option>
            </select>
            <input
              type="text"
              placeholder="Enter Target ID (CUST_00028, FR_017, TXN_00001)..."
              value={entityId}
              onChange={(e) => setEntityId(e.target.value)}
              className="w-64 sm:w-80 px-3 py-1.5 text-xs bg-soc-surface border border-soc-border rounded text-slate-100 placeholder-slate-400 font-mono focus:outline-none focus:border-cyan-500"
            />
            <button
              onClick={() => runInvestigation(entityType, entityId)}
              disabled={loading || !entityId.trim()}
              className="px-4 py-1.5 text-xs font-mono font-bold rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 transition-all flex items-center gap-1.5 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                  <span>Agents Investigating...</span>
                </>
              ) : (
                <>
                  <Sparkles size={14} />
                  <span>Launch Investigation</span>
                </>
              )}
            </button>
          </div>

          {/* Quick Target Chips */}
          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
            <span className="text-[10px] text-slate-400 uppercase">Presets:</span>
            <button
              onClick={() => {
                setEntityType('customer');
                setEntityId('CUST_00028');
                runInvestigation('customer', 'CUST_00028');
              }}
              className="px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20 text-[10px]"
            >
              CUST_00028 (Critical)
            </button>
            <button
              onClick={() => {
                setEntityType('ring');
                setEntityId('FR_017');
                runInvestigation('ring', 'FR_017');
              }}
              className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 hover:bg-purple-500/20 text-[10px]"
            >
              FR_017 (Syndicate)
            </button>
            <button
              onClick={() => {
                setEntityType('customer');
                setEntityId('CUST_00803');
                runInvestigation('customer', 'CUST_00803');
              }}
              className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 text-[10px]"
            >
              CUST_00803 (Clean)
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="soc-panel p-5 border-red-500/30 bg-red-950/20 text-center space-y-1.5">
          <AlertTriangle className="mx-auto text-red-400" size={26} />
          <h4 className="text-xs font-bold text-red-300 font-mono">Agent Dispatch Failed</h4>
          <p className="text-xs text-slate-400 font-mono">{error}</p>
        </div>
      )}

      {/* Active Multi-Agent Pipeline Visualization */}
      {investigation && (
        <>
          {/* Agent Pipeline Execution Grid */}
          <div className="soc-panel p-4 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-soc-border">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono flex items-center gap-1.5">
                <Bot size={14} className="text-cyan-400" />
                6-AGENT EXECUTION TRACE
              </h3>
              <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-1 font-bold">
                <CheckCircle2 size={12} /> ALL AGENTS REACHED CONSENSUS
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-1">
              {investigation.agent_trace.map((step) => {
                const Icon = agentIcons[step.agent_name] || Bot;
                return (
                  <div
                    key={step.agent_name}
                    className="p-2.5 bg-soc-surface border border-soc-border rounded space-y-1.5 hover:border-cyan-500/40 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="w-6 h-6 rounded bg-[#0D131F] border border-soc-border flex items-center justify-center text-cyan-400">
                        <Icon size={13} />
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">{step.duration_ms}ms</span>
                    </div>
                    <div>
                      <h4 className="text-[11px] font-bold font-mono text-slate-200">{step.agent_name}</h4>
                      <p className="text-[10px] text-slate-400 font-mono mt-0.5">
                        {step.signals_found} Signals · <span className="text-emerald-400 font-bold">✓ DONE</span>
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Verdict Hero Card */}
          <div className="soc-panel p-5 border-cyan-500/25 bg-gradient-to-r from-[#0D131F] via-[#0D131F] to-[#121B28] space-y-3.5">
            <div className="flex flex-wrap items-start justify-between gap-6">
              <div className="space-y-2 max-w-3xl">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-xs font-mono uppercase font-bold text-slate-400">Disposition Verdict:</span>
                  <span
                    className={`px-2.5 py-0.5 rounded text-xs font-bold font-mono border ${
                      investigation.decision.status === 'HIGH_RISK'
                        ? 'bg-red-500/15 text-red-400 border-red-500/35'
                        : investigation.decision.status === 'ENHANCED_REVIEW'
                        ? 'bg-orange-500/15 text-orange-400 border-orange-500/35'
                        : investigation.decision.status === 'REVIEW'
                        ? 'bg-amber-500/15 text-amber-400 border-amber-500/35'
                        : 'bg-emerald-500/15 text-emerald-400 border-emerald-500/35'
                    }`}
                  >
                    {investigation.decision.status.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs font-mono text-slate-400">
                    Confidence: <strong className="text-cyan-400">{investigation.decision.confidence}</strong>
                  </span>
                  <span className="text-xs font-mono text-slate-400">
                    Coverage: <strong className="text-slate-200">{investigation.decision.evidence_coverage}%</strong>
                  </span>
                </div>

                <h3 className="text-xl font-bold font-mono text-slate-100">{investigation.entity_id}</h3>
                <p className="text-xs text-slate-300 font-sans leading-relaxed">
                  {investigation.decision.reasoning}
                </p>
              </div>

              <RiskMeter score={investigation.decision.risk_score} level={investigation.decision.status} />
            </div>

            {/* Recommended Disposition Action */}
            <div className="p-3 bg-soc-panel border border-soc-border rounded space-y-1">
              <span className="text-[10px] uppercase font-bold text-amber-400 flex items-center gap-1.5 font-mono">
                <AlertTriangle size={12} /> RECOMMENDED DISPOSITION ACTION
              </span>
              <p className="text-xs text-slate-200 font-sans font-medium">{investigation.decision.recommended_action}</p>
            </div>
          </div>

          {/* Key Findings & Conflict Adjudication Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Key Findings */}
            <div className="soc-panel p-4 space-y-2.5">
              <div className="flex items-center justify-between pb-2 border-b border-soc-border">
                <div className="flex items-center gap-1.5">
                  <Search size={15} className="text-cyan-400" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
                    INVESTIGATOR KEY FINDINGS
                  </h4>
                </div>
                <span className="text-[10px] font-mono text-slate-400">
                  {investigation.key_findings.length} Discovered
                </span>
              </div>
              <div className="space-y-1.5">
                {investigation.key_findings.map((finding, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-300 p-2 rounded bg-soc-surface border border-soc-border/70">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 flex-shrink-0"></span>
                    <span className="leading-relaxed">{finding}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Conflict Adjudication Panel */}
            <div className="soc-panel p-4 space-y-2.5">
              <div className="flex items-center justify-between pb-2 border-b border-soc-border">
                <div className="flex items-center gap-1.5">
                  <SlidersHorizontal size={15} className="text-amber-400" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
                    CROSS-AGENT CONFLICT ADJUDICATION
                  </h4>
                </div>
                <span className="text-[10px] font-mono text-slate-400">
                  {investigation.conflicts.length} Disagreements
                </span>
              </div>

              {investigation.conflicts.length === 0 ? (
                <div className="p-5 text-center text-xs text-slate-400 space-y-1 font-mono">
                  <CheckCircle2 className="mx-auto text-emerald-400 mb-1" size={18} />
                  <p className="font-bold text-slate-200">Unanimous Swarm Consensus</p>
                  <p className="text-[11px] text-slate-400">Zero model vs graph or behavioral baseline conflicts detected.</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {investigation.conflicts.map((conf, idx) => (
                    <div key={idx} className="p-2.5 bg-amber-950/15 border border-amber-500/30 rounded space-y-1 text-xs">
                      <div className="font-bold text-amber-300 font-mono uppercase text-[11px]">
                        {conf.type.replace(/_/g, ' ')}
                      </div>
                      <p className="text-slate-300 font-sans leading-relaxed">{conf.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Evidence Panel with Provenance & Category Filter */}
          <div className="soc-panel p-4 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3 pb-2.5 border-b border-soc-border">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-1.5 font-mono">
                  <Layers size={14} className="text-cyan-400" />
                  CORRELATED MULTI-AGENT EVIDENCE PROVENANCE
                </h4>
                <p className="text-[11px] text-slate-400">Strictly grounded in Phase 1-5 forensic data sources.</p>
              </div>

              {/* Filter Pills */}
              <div className="flex flex-wrap items-center gap-1 text-xs font-mono">
                {['ALL', 'ML_MODEL', 'GRAPH_TOPOLOGY', 'BEHAVIORAL_HISTORY', 'PROTECTIVE'].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setEvidenceFilter(cat)}
                    className={`px-2 py-0.5 rounded font-semibold text-[10px] transition-colors ${
                      evidenceFilter === cat
                        ? 'bg-cyan-500 text-slate-950 font-bold'
                        : 'bg-soc-surface border border-soc-border text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {cat.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            </div>

            {/* Evidence Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
              {filteredEvidence.map((ev, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-soc-surface border border-soc-border rounded space-y-1.5 hover:border-slate-700 transition-colors text-xs"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5">
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/25 font-mono">
                        {ev.source_agent}
                      </span>
                      <span className="font-mono font-bold text-slate-200 text-xs">
                        {ev.signal.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <RiskBadge level={ev.severity} size="sm" />
                  </div>
                  <p className="text-xs text-slate-300 font-sans leading-relaxed">{ev.description}</p>
                  {(ev.value !== null && ev.value !== undefined) && (
                    <div className="text-[10px] font-mono text-slate-400 pt-1 border-t border-soc-border/60">
                      Feature Value: <strong className="text-slate-200">{String(ev.value)}</strong>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default AgentInvestigationPage;
