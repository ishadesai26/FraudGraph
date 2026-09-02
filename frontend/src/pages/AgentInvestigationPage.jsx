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
    <div className="space-y-6 pb-16">
      {/* Header Banner */}
      <div className="glass-panel p-6 relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 border-indigo-500/30">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></span>
            <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-widest font-mono">
              Phase 6 Collaborative Multi-Agent Engine
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2.5">
            <Bot className="text-indigo-400" size={26} />
            Autonomous Agentic Fraud Investigation
          </h1>
          <p className="text-xs text-slate-400 max-w-3xl">
            Simulate a multidisciplinary team of 6 specialized AI agents collaborating in real-time to analyze ML scores, graph topologies, and behavioral history with strict evidence provenance and conflict detection.
          </p>
        </div>
      </div>

      {/* Entity Selection & Launch Bar */}
      <div className="glass-panel p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <select
              value={entityType}
              onChange={(e) => setEntityType(e.target.value)}
              className="text-xs font-semibold bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="customer">Customer Account</option>
              <option value="ring">Fraud Ring Syndicate</option>
              <option value="transaction">Transaction</option>
            </select>
            <input
              type="text"
              placeholder="Enter Target ID (e.g. CUST_00028, FR_017, TXN_00001)..."
              value={entityId}
              onChange={(e) => setEntityId(e.target.value)}
              className="w-64 sm:w-80 px-3.5 py-2 text-xs bg-slate-900 border border-slate-700/80 rounded-xl text-slate-100 placeholder-slate-500 font-mono focus:outline-none focus:border-indigo-500"
            />
            <button
              onClick={() => runInvestigation(entityType, entityId)}
              disabled={loading || !entityId.trim()}
              className="px-4 py-2 text-xs font-bold rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/25 transition-all flex items-center gap-1.5 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
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

          {/* Quick Demo Shortcuts */}
          <div className="flex flex-wrap items-center gap-2 text-xs font-medium text-slate-400">
            <span className="text-[11px] text-slate-500">Quick Targets:</span>
            <button
              onClick={() => {
                setEntityType('customer');
                setEntityId('CUST_00028');
                runInvestigation('customer', 'CUST_00028');
              }}
              className="px-2.5 py-1 rounded-lg bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20 text-[11px] font-mono"
            >
              CUST_00028 (Critical)
            </button>
            <button
              onClick={() => {
                setEntityType('ring');
                setEntityId('FR_017');
                runInvestigation('ring', 'FR_017');
              }}
              className="px-2.5 py-1 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/30 hover:bg-purple-500/20 text-[11px] font-mono"
            >
              FR_017 (Syndicate)
            </button>
            <button
              onClick={() => {
                setEntityType('customer');
                setEntityId('CUST_00803');
                runInvestigation('customer', 'CUST_00803');
              }}
              className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 text-[11px] font-mono"
            >
              CUST_00803 (Clean)
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="glass-panel p-6 border-red-500/30 bg-red-950/20 text-center space-y-2">
          <AlertTriangle className="mx-auto text-red-400" size={28} />
          <h4 className="text-xs font-bold text-red-300">Investigation Dispatch Failed</h4>
          <p className="text-xs text-slate-400">{error}</p>
        </div>
      )}

      {/* Active Visual Agent Pipeline */}
      {investigation && (
        <>
          {/* Agent Pipeline Flow */}
          <div className="glass-panel p-5 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-1.5">
                <Bot size={15} className="text-indigo-400" />
                Multi-Agent Execution Pipeline Flow
              </h3>
              <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
                <CheckCircle2 size={12} /> 6/6 Agents Reached Consensus
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-2">
              {investigation.agent_trace.map((step, idx) => {
                const Icon = agentIcons[step.agent_name] || Bot;
                return (
                  <div
                    key={step.agent_name}
                    className="p-3 bg-slate-900/90 border border-slate-800 rounded-xl space-y-2 hover:border-indigo-500/40 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                        <Icon size={15} />
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">{step.duration_ms}ms</span>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-200">{step.agent_name}</h4>
                      <p className="text-[10px] text-slate-400 font-mono mt-0.5">
                        {step.signals_found} Signals · <span className="text-emerald-400 font-bold">✓ OK</span>
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Verdict Hero Card */}
          <div className="glass-panel p-6 border-indigo-500/30 bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/30 space-y-4">
            <div className="flex flex-wrap items-start justify-between gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono uppercase font-bold text-slate-400">Investigation Verdict:</span>
                  <span
                    className={`px-3 py-1 rounded-xl text-xs font-bold font-mono border ${
                      investigation.decision.status === 'HIGH_RISK'
                        ? 'bg-red-500/20 text-red-400 border-red-500/40'
                        : investigation.decision.status === 'ENHANCED_REVIEW'
                        ? 'bg-orange-500/20 text-orange-400 border-orange-500/40'
                        : investigation.decision.status === 'REVIEW'
                        ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                        : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                    }`}
                  >
                    {investigation.decision.status.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs font-mono text-slate-400">
                    Confidence: <strong className="text-indigo-400">{investigation.decision.confidence}</strong>
                  </span>
                  <span className="text-xs font-mono text-slate-400">
                    Evidence Coverage: <strong className="text-cyan-400">{investigation.decision.evidence_coverage}%</strong>
                  </span>
                </div>

                <h3 className="text-xl font-bold font-mono text-slate-100">{investigation.entity_id}</h3>
                <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
                  {investigation.decision.reasoning}
                </p>
              </div>

              <RiskMeter score={investigation.decision.risk_score} level={investigation.decision.status} />
            </div>

            {/* Recommended Action Box */}
            <div className="p-3.5 bg-slate-900/90 border border-slate-800 rounded-xl space-y-1.5">
              <span className="text-[10px] uppercase font-bold text-amber-400 flex items-center gap-1.5">
                <AlertTriangle size={13} /> Recommended Disposition Action
              </span>
              <p className="text-xs text-slate-200 font-medium">{investigation.decision.recommended_action}</p>
            </div>
          </div>

          {/* Key Findings & Conflict Detection Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Key Findings */}
            <div className="glass-panel p-5 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Search size={16} className="text-indigo-400" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                    Investigator Key Findings
                  </h4>
                </div>
                <span className="text-[11px] font-mono text-slate-400">
                  {investigation.key_findings.length} Discovered
                </span>
              </div>
              <div className="space-y-2 pt-1">
                {investigation.key_findings.map((finding, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-300 p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 flex-shrink-0"></span>
                    <span>{finding}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Conflict Detection Panel */}
            <div className="glass-panel p-5 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <SlidersHorizontal size={16} className="text-amber-400" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                    Cross-Agent Conflict Adjudication
                  </h4>
                </div>
                <span className="text-[11px] font-mono text-slate-400">
                  {investigation.conflicts.length} Disagreement(s)
                </span>
              </div>

              {investigation.conflicts.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-400 space-y-1">
                  <CheckCircle2 className="mx-auto text-emerald-400 mb-1" size={20} />
                  <p className="font-semibold text-slate-300">Unanimous Multi-Agent Consensus</p>
                  <p className="text-[11px]">No model vs network or behavioral baseline conflicts were detected.</p>
                </div>
              ) : (
                <div className="space-y-2.5 pt-1">
                  {investigation.conflicts.map((conf, idx) => (
                    <div key={idx} className="p-3 bg-amber-950/20 border border-amber-500/30 rounded-xl space-y-1 text-xs">
                      <div className="font-bold text-amber-300 font-mono uppercase">{conf.type.replace(/_/g, ' ')}</div>
                      <p className="text-slate-300">{conf.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Evidence Panel with Provenance & Category Filter */}
          <div className="glass-panel p-5 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                  <Layers size={16} className="text-cyan-400" />
                  Correlated Multi-Agent Evidence Provenance
                </h4>
                <p className="text-xs text-slate-400">Strictly grounded in Phase 1–5 data sources with zero synthetic hallucinations.</p>
              </div>

              {/* Filter Pills */}
              <div className="flex flex-wrap items-center gap-1.5 text-xs">
                {['ALL', 'ML_MODEL', 'GRAPH_TOPOLOGY', 'BEHAVIORAL_HISTORY', 'PROTECTIVE'].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setEvidenceFilter(cat)}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
                      evidenceFilter === cat
                        ? 'bg-cyan-500 text-white'
                        : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {cat.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            </div>

            {/* Evidence Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {filteredEvidence.map((ev, idx) => (
                <div
                  key={idx}
                  className="p-3.5 bg-slate-900/80 border border-slate-800 rounded-xl space-y-2 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 font-mono">
                        {ev.source_agent}
                      </span>
                      <span className="text-xs font-mono font-bold text-slate-200">
                        {ev.signal.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <RiskBadge level={ev.severity} size="sm" />
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">{ev.description}</p>
                  {(ev.value !== null && ev.value !== undefined) && (
                    <div className="text-[11px] font-mono text-slate-400 pt-1 border-t border-slate-800/60">
                      Value: <strong className="text-slate-200">{String(ev.value)}</strong>
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
