import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Network,
  Smartphone,
  CreditCard,
  Globe,
  Store,
  Users,
  AlertTriangle,
  ArrowUpRight,
  ShieldAlert,
  ChevronRight,
  CheckCircle2,
} from 'lucide-react';
import apiService from '../services/api';
import RiskBadge from '../components/RiskBadge';
import CytoscapeGraph from '../components/CytoscapeGraph';
import EvidenceTable from '../components/EvidenceTable';

export function FraudRingDetailPage() {
  const { ringId } = useParams();
  const navigate = useNavigate();

  const [ring, setRing] = useState(null);
  const [networkGraph, setNetworkGraph] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadRingData() {
      try {
        setLoading(true);
        setError(null);
        const [ringRes, netRes] = await Promise.all([
          apiService.getFraudRing(ringId),
          apiService.getNetwork('ring', ringId),
        ]);
        setRing(ringRes);
        setNetworkGraph(netRes);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadRingData();
  }, [ringId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 text-purple-400">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-purple-400 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs font-mono text-slate-400">Loading Syndicate Topology for {ringId}...</p>
        </div>
      </div>
    );
  }

  if (error || !ring) {
    return (
      <div className="space-y-4 p-4">
        <button
          onClick={() => navigate('/fraud-rings')}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 font-mono"
        >
          <ArrowLeft size={14} /> Back to Fraud Rings Directory
        </button>
        <div className="soc-panel p-8 text-center text-xs text-red-400 space-y-2 border-red-500/30">
          <AlertTriangle className="mx-auto text-red-400" size={30} />
          <h3 className="text-sm font-bold text-red-300 font-mono">Fraud Ring Dossier Error</h3>
          <p className="font-mono">{error || `Fraud ring '${ringId}' not found.`}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5 pb-16">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
        <Link to="/fraud-rings" className="hover:text-slate-200 transition-colors">Fraud Rings</Link>
        <ChevronRight size={13} />
        <span className="text-slate-200 font-bold">{ring.ring_id}</span>
      </div>

      {/* Syndicate Hero Dossier */}
      <div className="soc-panel p-5 relative overflow-hidden bg-gradient-to-r from-[#0D131F] via-[#0D131F] to-[#17112A] border-soc-border">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-3">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500 animate-soc-pulse"></span>
              <h1 className="text-2xl font-extrabold text-slate-100 font-mono tracking-tight">{ring.ring_id}</h1>
              <RiskBadge level={ring.risk_level} score={ring.risk_score} size="lg" />
            </div>
            <p className="text-xs text-slate-300 font-sans leading-relaxed">
              Coordinated multi-entity fraud syndicate funneled through shared hardware endpoints and mule payment instruments detected via Louvain community partition.
            </p>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 pt-1 font-mono">
              <span className="flex items-center gap-1.5 text-blue-400">
                <Smartphone size={13} />
                {ring.shared_devices_count} Shared Devices
              </span>
              <span className="flex items-center gap-1.5 text-amber-400">
                <CreditCard size={13} />
                {ring.shared_payments_count} Shared Cards/VPAs
              </span>
              <span className="flex items-center gap-1.5 text-purple-400">
                <Globe size={13} />
                {ring.shared_ips_count} Proxy IPs
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-soc-panel border border-soc-border rounded text-right font-mono">
              <span className="text-[9px] uppercase font-bold text-slate-400">Syndicate Scale</span>
              <div className="text-lg font-bold text-slate-100 mt-0.5">
                {ring.customer_count} Member Accounts
              </div>
              <span className="text-[10px] text-purple-400">
                ₹{ring.transaction_volume.toLocaleString('en-IN', { minimumFractionDigits: 2 })} Volume
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Syndicate Graph Canvas */}
      {networkGraph && (
        <CytoscapeGraph
          graphData={networkGraph}
          height="500px"
          title={`Syndicate Network Topology (${ring.ring_id})`}
        />
      )}

      {/* Forensic Evidence & Disruption Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left 2 Cols: Evidence & Members Table */}
        <div className="lg:col-span-2 space-y-4">
          <EvidenceTable evidence={ring.evidence} />

          {/* Member Accounts Roster */}
          <div className="soc-panel p-4 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-soc-border">
              <div className="flex items-center gap-2">
                <Users className="text-cyan-400" size={16} />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
                  SYNDICATE MEMBER ACCOUNTS ({ring.members.length})
                </h3>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">Click row to inspect</span>
            </div>

            <div className="overflow-x-auto max-h-80 overflow-y-auto">
              <table className="w-full text-left border-collapse">
                <thead className="sticky top-0 bg-[#0D131F] border-b border-soc-border text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono">
                  <tr>
                    <th className="py-2 px-3">Customer ID</th>
                    <th className="py-2 px-3">Role In Syndicate</th>
                    <th className="py-2 px-3">Individual Risk</th>
                    <th className="py-2 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-soc-border/60 text-xs font-mono">
                  {ring.members.map((m) => (
                    <tr
                      key={m.customer_id}
                      onClick={() => navigate(`/customers/${m.customer_id}`)}
                      className="hover:bg-soc-surface-hover cursor-pointer transition-colors"
                    >
                      <td className="py-2.5 px-3 font-bold text-cyan-400">{m.customer_id}</td>
                      <td className="py-2.5 px-3">
                        {m.is_core_member ? (
                          <span className="px-1.5 py-0.5 rounded bg-red-500/15 text-red-400 border border-red-500/30 text-[9px] font-bold">
                            CORE ORGANIZER
                          </span>
                        ) : (
                          <span className="text-slate-400 text-[10px]">Member Account</span>
                        )}
                      </td>
                      <td className="py-2.5 px-3 text-slate-200">
                        {m.individual_risk_score.toFixed(1)} / 100
                      </td>
                      <td className="py-2.5 px-3 text-right text-cyan-400">
                        <ArrowUpRight size={13} className="inline" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right 1 Col: Disruption Action Plan */}
        <div className="space-y-4">
          <div className="soc-panel p-4 space-y-3 border-purple-500/30 bg-purple-950/10">
            <div className="flex items-center gap-2 pb-2 border-b border-purple-900/40">
              <ShieldAlert className="text-purple-400" size={16} />
              <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 font-mono">
                SYNDICATE DISRUPTION ACTION PLAN
              </h3>
            </div>
            <div className="space-y-2 text-xs text-slate-200">
              {ring.recommendations.map((rec, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <span className="font-mono text-purple-400 font-bold">{idx + 1}.</span>
                  <span className="leading-relaxed">{rec}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FraudRingDetailPage;
