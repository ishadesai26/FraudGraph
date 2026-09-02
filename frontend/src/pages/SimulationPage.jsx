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
    <div className="space-y-6 pb-16">
      {/* Header Banner */}
      <div className="glass-panel p-6 relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-900 to-amber-950/30 border-amber-500/30">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
            <span className="text-[11px] font-bold text-amber-400 uppercase tracking-widest font-mono">
              Live Real-Time Risk Simulation
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2.5">
            <Zap className="text-amber-400" size={26} />
            Real-Time Transaction Risk Simulator
          </h1>
          <p className="text-xs text-slate-400 max-w-3xl">
            Simulate incoming live transactions through the live feature extraction, machine-learning inference models, and collaborative 6-agent forensic investigation pipeline in real-time.
          </p>
        </div>
      </div>

      {/* Scenario Selection Grid */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
          Select Fraud Simulation Scenario
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {scenarios.map((sc) => {
            const isSelected = selectedScenario === sc.scenario_id;
            return (
              <div
                key={sc.scenario_id}
                onClick={() => handleScenarioSelect(sc)}
                className={`p-4 rounded-xl border cursor-pointer transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-amber-500/10 border-amber-500/60 shadow-lg shadow-amber-500/10'
                    : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold uppercase text-amber-400">
                      {sc.scenario_id}
                    </span>
                    <RiskBadge level={sc.expected_risk_tier} size="sm" />
                  </div>
                  <h4 className="text-xs font-bold text-slate-100">{sc.title}</h4>
                  <p className="text-[11px] text-slate-400 leading-relaxed">{sc.description}</p>
                </div>
                <div className="pt-3 mt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] font-mono text-slate-400">
                  <span>₹{sc.sample_payload.amount.toLocaleString()}</span>
                  <span>{sc.sample_payload.customer_id}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Payload Editor & Execution Trigger */}
      <div className="glass-panel p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Simulated Transaction Ingress Payload
          </h4>
          <span className="text-[11px] text-slate-400 font-mono">Live Gateway Payload</span>
        </div>

        {/* Form Inputs Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-400 mb-1">Customer ID</label>
            <input
              type="text"
              value={transactionPayload.customer_id}
              onChange={(e) => setTransactionPayload({ ...transactionPayload, customer_id: e.target.value })}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 font-mono text-slate-100 focus:outline-none focus:border-amber-500"
            />
          </div>
          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-400 mb-1">Amount (₹)</label>
            <input
              type="number"
              value={transactionPayload.amount}
              onChange={(e) => setTransactionPayload({ ...transactionPayload, amount: parseFloat(e.target.value) || 0 })}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 font-mono text-slate-100 focus:outline-none focus:border-amber-500"
            />
          </div>
          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-400 mb-1">Payment Type</label>
            <select
              value={transactionPayload.payment_type}
              onChange={(e) => setTransactionPayload({ ...transactionPayload, payment_type: e.target.value })}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 font-mono text-slate-100 focus:outline-none focus:border-amber-500"
            >
              <option value="UPI">UPI</option>
              <option value="CREDIT_CARD">CREDIT_CARD</option>
              <option value="DEBIT_CARD">DEBIT_CARD</option>
              <option value="NET_BANKING">NET_BANKING</option>
            </select>
          </div>
          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-400 mb-1">Velocity Interval (s)</label>
            <input
              type="number"
              value={transactionPayload.seconds_since_previous || 0}
              onChange={(e) => setTransactionPayload({ ...transactionPayload, seconds_since_previous: parseInt(e.target.value, 10) || 0 })}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 font-mono text-slate-100 focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        {/* Action Trigger Button */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={handleSimulate}
            disabled={loading}
            className="px-6 py-2.5 text-xs font-bold rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/25 transition-all flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                <span>Executing Live Pipeline & Agents...</span>
              </>
            ) : (
              <>
                <Play size={15} className="fill-current" />
                <span>Simulate & Investigate Transaction</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="glass-panel p-6 border-red-500/30 bg-red-950/20 text-center space-y-2">
          <AlertTriangle className="mx-auto text-red-400" size={28} />
          <h4 className="text-xs font-bold text-red-300">Simulation Execution Failed</h4>
          <p className="text-xs text-slate-400">{error}</p>
        </div>
      )}

      {/* Simulation Response & Live Multi-Agent Verdict */}
      {simulationResult && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-3 duration-500">
          {/* Live Risk Breakdown Banner */}
          <div className="glass-panel p-6 border-amber-500/30 bg-gradient-to-r from-slate-900 via-slate-900 to-amber-950/30 space-y-4">
            <div className="flex flex-wrap items-start justify-between gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
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
                <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
                  {simulationResult.decision.reasoning}
                </p>
              </div>

              <RiskMeter score={simulationResult.risk.composite_risk_score} level={simulationResult.decision.status} />
            </div>

            {/* Model Scoring Signals Matrix */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-slate-800 font-mono text-xs">
              <div className="p-2.5 bg-slate-900/90 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-sans font-bold">Composite Risk</span>
                <div className="text-base font-bold text-slate-100 mt-0.5">{simulationResult.risk.composite_risk_score} / 100</div>
              </div>
              <div className="p-2.5 bg-slate-900/90 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-sans font-bold">Supervised ML Prob</span>
                <div className="text-base font-bold text-cyan-400 mt-0.5">{(simulationResult.risk.supervised_ml_probability * 100).toFixed(1)}%</div>
              </div>
              <div className="p-2.5 bg-slate-900/90 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-sans font-bold">Anomaly Score</span>
                <div className="text-base font-bold text-amber-400 mt-0.5">{simulationResult.risk.unsupervised_anomaly_score} / 100</div>
              </div>
              <div className="p-2.5 bg-slate-900/90 rounded-lg border border-slate-800">
                <span className="text-[10px] text-slate-400 uppercase font-sans font-bold">Network Risk</span>
                <div className="text-base font-bold text-purple-400 mt-0.5">{simulationResult.risk.network_risk_score} / 100</div>
              </div>
            </div>
          </div>

          {/* 6-Agent Execution Pipeline Trace */}
          <div className="glass-panel p-5 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 flex items-center gap-1.5">
              <Bot size={15} className="text-amber-400" />
              Collaborative 6-Agent Live Investigation Trace
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-1">
              {simulationResult.agent_trace.map((step) => (
                <div key={step.agent_name} className="p-3 bg-slate-900/90 border border-slate-800 rounded-xl space-y-1 text-xs">
                  <div className="flex justify-between items-center text-[10px] text-slate-400 font-mono">
                    <span>{step.agent_name}</span>
                    <span className="text-emerald-400 font-bold">✓ {step.duration_ms}ms</span>
                  </div>
                  <div className="text-[11px] font-bold text-slate-200">{step.signals_found} Signals Found</div>
                </div>
              ))}
            </div>
          </div>

          {/* Evidence Package Discovered */}
          <div className="glass-panel p-5 space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Corroborated Multi-Agent Evidence Package
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {simulationResult.investigation.evidence_items.map((ev, idx) => (
                <div key={idx} className="p-3.5 bg-slate-900/80 border border-slate-800 rounded-xl space-y-1.5 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
                      {ev.source_agent}
                    </span>
                    <RiskBadge level={ev.severity} size="sm" />
                  </div>
                  <div className="font-mono font-bold text-slate-200">{ev.signal.replace(/_/g, ' ')}</div>
                  <p className="text-slate-400 text-[11px] leading-relaxed">{ev.description}</p>
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
