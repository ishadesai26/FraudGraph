import React, { useState, useEffect } from 'react';
import {
  Zap,
  Play,
  CheckCircle2,
  AlertTriangle,
  Cpu,
  Network,
  Activity,
  Layers,
  Search,
  ShieldAlert,
  Bot,
  IndianRupee,
  Clock,
  Smartphone,
  Globe,
  Store,
  CreditCard,
  Sparkles,
} from 'lucide-react';
import apiService from '../services/api';
import RiskBadge from '../components/RiskBadge';
import RiskMeter from '../components/RiskMeter';

export function SimulationPage() {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState('FRAUD_RING_SYNDICATE');
  const [transactionPayload, setTransactionPayload] = useState({
    customer_id: 'CUST_00028',
    amount: 45000.0,
    merchant_id: 'MERCH_0067',
    payment_type: 'UPI',
    device_id: 'DEV_00028',
    ip_id: 'IP_00028',
    city: 'Mumbai',
    seconds_since_previous: 25,
  });
  const [loading, setLoading] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadScenarios() {
      try {
        const list = await apiService.getSimulationScenarios();
        setScenarios(list || []);
      } catch (err) {
        console.error('Failed to load scenarios:', err);
      }
    }
    loadScenarios();
  }, []);

  const handleScenarioSelect = (sc) => {
    setSelectedScenario(sc.scenario_id);
    setTransactionPayload(sc.sample_payload);
  };

  const handleSimulate = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiService.simulateAndAnalyze({
        scenario_id: selectedScenario,
        transaction: transactionPayload,
      });
      setSimulationResult(res);
    } catch (err) {
      setError(err.message);
      setSimulationResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 pb-16">
      {/* Header Banner */}
      <div className="soc-panel p-5 relative overflow-hidden bg-gradient-to-r from-[#0D131F] via-[#0D131F] to-[#1E1710] border-soc-border">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-soc-pulse"></span>
            <span className="text-[10px] font-bold text-amber-400 uppercase tracking-widest font-mono">
              LIVE GATEWAY INGRESS SIMULATOR
            </span>
          </div>
          <h1 className="text-xl md:text-2xl font-extrabold text-slate-100 flex items-center gap-2.5 font-mono">
            <Zap className="text-amber-400" size={24} />
            REAL-TIME TRANSACTION RISK SIMULATOR
          </h1>
          <p className="text-xs text-slate-400 font-sans leading-relaxed max-w-3xl">
            Simulate incoming live transactions through the live feature extraction pipeline, Random Forest inference models, and collaborative 6-agent forensic investigation swarm in real time.
          </p>
        </div>
      </div>

      {/* Scenario Selection Grid */}
      <div className="space-y-2.5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono">
          1. SELECT CONTROLLED SIMULATION SCENARIO
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {scenarios.map((sc) => {
            const isSelected = selectedScenario === sc.scenario_id;
            return (
              <div
                key={sc.scenario_id}
                onClick={() => handleScenarioSelect(sc)}
                className={`p-3.5 rounded border cursor-pointer transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-amber-500/10 border-amber-500/60 shadow-sm'
                    : 'bg-soc-surface border-soc-border hover:border-slate-700'
                }`}
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] font-mono font-bold uppercase text-amber-400">
                      {sc.scenario_id}
                    </span>
                    <RiskBadge level={sc.expected_risk_tier} size="sm" />
                  </div>
                  <h4 className="text-xs font-bold text-slate-100">{sc.title}</h4>
                  <p className="text-[11px] text-slate-400 font-sans leading-relaxed">{sc.description}</p>
                </div>
                <div className="pt-2 mt-2 border-t border-soc-border/60 flex items-center justify-between text-[10px] font-mono text-slate-400">
                  <span>₹{sc.sample_payload.amount.toLocaleString()}</span>
                  <span className="text-cyan-400">{sc.sample_payload.customer_id}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Payload Editor & Execution Trigger */}
      <div className="soc-panel p-4 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-soc-border font-mono text-xs">
          <h4 className="font-bold uppercase tracking-wider text-slate-200">
            2. INGRESS TRANSACTION PAYLOAD PARAMETERS
          </h4>
          <span className="text-[10px] text-slate-400">Gateway Payload Inspector</span>
        </div>

        {/* Inputs Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs font-mono">
          <div>
            <label className="block text-[9px] uppercase font-bold text-slate-400 mb-1">Customer ID</label>
            <input
              type="text"
              value={transactionPayload.customer_id}
              onChange={(e) => setTransactionPayload({ ...transactionPayload, customer_id: e.target.value })}
              className="w-full bg-soc-surface border border-soc-border rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-amber-500"
            />
          </div>
          <div>
            <label className="block text-[9px] uppercase font-bold text-slate-400 mb-1">Amount (₹)</label>
            <input
              type="number"
              value={transactionPayload.amount}
              onChange={(e) => setTransactionPayload({ ...transactionPayload, amount: parseFloat(e.target.value) || 0 })}
              className="w-full bg-soc-surface border border-soc-border rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-amber-500"
            />
          </div>
          <div>
            <label className="block text-[9px] uppercase font-bold text-slate-400 mb-1">Payment Type</label>
            <select
              value={transactionPayload.payment_type}
              onChange={(e) => setTransactionPayload({ ...transactionPayload, payment_type: e.target.value })}
              className="w-full bg-soc-surface border border-soc-border rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-amber-500"
            >
              <option value="UPI">UPI</option>
              <option value="CREDIT_CARD">CREDIT_CARD</option>
              <option value="DEBIT_CARD">DEBIT_CARD</option>
              <option value="NET_BANKING">NET_BANKING</option>
            </select>
          </div>
          <div>
            <label className="block text-[9px] uppercase font-bold text-slate-400 mb-1">Velocity Delta (s)</label>
            <input
              type="number"
              value={transactionPayload.seconds_since_previous || 0}
              onChange={(e) => setTransactionPayload({ ...transactionPayload, seconds_since_previous: parseInt(e.target.value, 10) || 0 })}
              className="w-full bg-soc-surface border border-soc-border rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        {/* Trigger Button */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={handleSimulate}
            disabled={loading}
            className="px-5 py-2 text-xs font-mono font-bold rounded bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-sm transition-all flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                <span>Executing Pipeline & Agents...</span>
              </>
            ) : (
              <>
                <Play size={14} className="fill-current" />
                <span>Simulate & Score Transaction</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="soc-panel p-5 border-red-500/30 bg-red-950/20 text-center space-y-1.5">
          <AlertTriangle className="mx-auto text-red-400" size={26} />
          <h4 className="text-xs font-bold text-red-300 font-mono">Simulation Execution Failed</h4>
          <p className="text-xs text-slate-400 font-mono">{error}</p>
        </div>
      )}

      {/* Simulation Results Section */}
      {simulationResult && (
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
          {/* Live Risk Breakdown Banner */}
          <div className="soc-panel p-5 border-amber-500/30 bg-gradient-to-r from-[#0D131F] via-[#0D131F] to-[#1E1610] space-y-3.5">
            <div className="flex flex-wrap items-start justify-between gap-6">
              <div className="space-y-2 max-w-3xl">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-xs font-mono uppercase font-bold text-slate-400">Simulation Disposition:</span>
                  <RiskBadge level={simulationResult.decision.status} size="md" />
                  <span className="text-xs font-mono text-slate-400">
                    Confidence: <strong className="text-amber-400">{simulationResult.decision.confidence}</strong>
                  </span>
                  <span className="text-xs font-mono text-slate-400">
                    Coverage: <strong className="text-cyan-400">{simulationResult.decision.evidence_coverage}%</strong>
                  </span>
                </div>

                <h3 className="text-2xl font-bold font-mono text-slate-100">
                  ₹{transactionPayload.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </h3>
                <p className="text-xs text-slate-300 font-sans leading-relaxed">
                  {simulationResult.decision.reasoning}
                </p>
              </div>

              <RiskMeter score={simulationResult.risk.composite_risk_score} level={simulationResult.decision.status} />
            </div>

            {/* Model Scoring Signals Matrix */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-2.5 border-t border-soc-border font-mono text-xs">
              <div className="p-2.5 bg-soc-panel rounded border border-soc-border">
                <span className="text-[9px] text-slate-400 uppercase font-bold">Composite Score</span>
                <div className="text-base font-bold text-slate-100 mt-0.5">{simulationResult.risk.composite_risk_score} / 100</div>
              </div>
              <div className="p-2.5 bg-soc-panel rounded border border-soc-border">
                <span className="text-[9px] text-slate-400 uppercase font-bold">Supervised ML</span>
                <div className="text-base font-bold text-cyan-400 mt-0.5">{(simulationResult.risk.supervised_ml_probability * 100).toFixed(1)}%</div>
              </div>
              <div className="p-2.5 bg-soc-panel rounded border border-soc-border">
                <span className="text-[9px] text-slate-400 uppercase font-bold">Anomaly Score</span>
                <div className="text-base font-bold text-amber-400 mt-0.5">{simulationResult.risk.unsupervised_anomaly_score} / 100</div>
              </div>
              <div className="p-2.5 bg-soc-panel rounded border border-soc-border">
                <span className="text-[9px] text-slate-400 uppercase font-bold">Network Risk</span>
                <div className="text-base font-bold text-purple-400 mt-0.5">{simulationResult.risk.network_risk_score} / 100</div>
              </div>
            </div>
          </div>

          {/* 6-Agent Execution Pipeline Trace */}
          <div className="soc-panel p-4 space-y-2.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-1.5 font-mono">
              <Bot size={14} className="text-amber-400" />
              COLLABORATIVE 6-AGENT SIMULATION TRACE
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-1">
              {simulationResult.agent_trace.map((step) => (
                <div key={step.agent_name} className="p-2.5 bg-soc-surface border border-soc-border rounded space-y-1 text-xs font-mono">
                  <div className="flex justify-between items-center text-[9px] text-slate-400">
                    <span>{step.agent_name}</span>
                    <span className="text-emerald-400 font-bold">✓ {step.duration_ms}ms</span>
                  </div>
                  <div className="text-[11px] font-bold text-slate-200">{step.signals_found} Signals</div>
                </div>
              ))}
            </div>
          </div>

          {/* Evidence Package Discovered */}
          <div className="soc-panel p-4 space-y-2.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
              CORROBORATED MULTI-AGENT EVIDENCE PACKAGE
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
              {simulationResult.investigation.evidence_items.map((ev, idx) => (
                <div key={idx} className="p-3 bg-soc-surface border border-soc-border rounded space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] font-bold font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
                      {ev.source_agent}
                    </span>
                    <RiskBadge level={ev.severity} size="sm" />
                  </div>
                  <div className="font-mono font-bold text-slate-200">{ev.signal.replace(/_/g, ' ')}</div>
                  <p className="text-slate-400 text-[11px] font-sans leading-relaxed">{ev.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SimulationPage;
