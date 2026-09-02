import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  User,
  MapPin,
  Calendar,
  ShieldCheck,
  Network,
  AlertTriangle,
  FileText,
  Smartphone,
  CreditCard,
  Users,
  CheckCircle2,
  ChevronRight,
} from 'lucide-react';
import apiService from '../services/api';
import RiskBadge from '../components/RiskBadge';
import RiskMeter from '../components/RiskMeter';
import CytoscapeGraph from '../components/CytoscapeGraph';
import EvidenceTable from '../components/EvidenceTable';
import TimelineView from '../components/TimelineView';

export function CustomerDetailPage() {
  const { customerId } = useParams();
  const navigate = useNavigate();

  const [customer, setCustomer] = useState(null);
  const [networkGraph, setNetworkGraph] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // overview, network, timeline, report

  useEffect(() => {
    async function loadCustomerData() {
      try {
        setLoading(true);
        setError(null);
        const [custRes, netRes] = await Promise.all([
          apiService.getCustomer(customerId),
          apiService.getNetwork('customer', customerId),
        ]);
        setCustomer(custRes);
        setNetworkGraph(netRes);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadCustomerData();
  }, [customerId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 text-cyan-400">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs font-mono text-slate-400">Loading Forensic Case Dossier for {customerId}...</p>
        </div>
      </div>
    );
  }

  if (error || !customer) {
    return (
      <div className="space-y-4 p-6">
        <button
          onClick={() => navigate('/customers')}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200"
        >
          <ArrowLeft size={14} /> Back to Customer Registry
        </button>
        <div className="glass-panel p-8 text-center text-xs text-red-400 space-y-2 border-red-500/30">
          <AlertTriangle className="mx-auto text-red-400" size={32} />
          <h3 className="text-sm font-bold text-red-300">Customer Investigation Profile Error</h3>
          <p>{error || `Customer '${customerId}' not found.`}</p>
        </div>
      </div>
    );
  }

  const hasRing = customer.associated_ring_id && customer.associated_ring_id !== 'None (Isolated Node)';

  return (
    <div className="space-y-6 pb-16">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link to="/customers" className="hover:text-slate-200">Customers</Link>
        <ChevronRight size={14} />
        <span className="text-slate-200 font-mono font-semibold">{customer.customer_id}</span>
      </div>

      {/* Hero Dossier Header */}
      <div className="glass-panel p-6 relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border-slate-800">
        <div className="flex flex-wrap items-start justify-between gap-6">
          {/* Left: Customer Demographics */}
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-extrabold text-slate-100 font-mono">{customer.customer_id}</h1>
              <RiskBadge level={customer.risk_level} score={customer.risk_score} size="lg" />
              <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
                Confidence: <strong className="text-cyan-400">{customer.explanation_confidence}</strong>
              </span>
            </div>

            <p className="text-sm font-medium text-slate-300">{customer.name}</p>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <MapPin size={14} className="text-cyan-400" />
                {customer.home_city}
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar size={14} className="text-amber-400" />
                {customer.account_age_days} Days Account Tenure
              </span>
              <span className="flex items-center gap-1.5">
                <ShieldCheck size={14} className="text-emerald-400" />
                {customer.kyc_verified ? 'KYC Verified' : 'KYC Pending'}
              </span>
              {hasRing && (
                <Link
                  to={`/fraud-rings/${customer.associated_ring_id}`}
                  className="flex items-center gap-1.5 text-purple-400 hover:underline font-mono font-semibold"
                >
                  <Network size={14} />
                  Syndicate {customer.associated_ring_id} ({customer.member_role || 'MEMBER'})
                </Link>
              )}
            </div>
          </div>

          {/* Right: Risk Gauge & Spend Card */}
          <div className="flex items-center gap-4">
            <div className="p-3.5 bg-slate-900/80 border border-slate-800 rounded-xl text-right">
              <span className="text-[10px] uppercase font-bold text-slate-400">Historical Volume</span>
              <div className="text-lg font-bold font-mono text-slate-100 mt-0.5">
                ₹{customer.total_spend.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
              <span className="text-[11px] text-slate-400">{customer.total_transactions} Transactions</span>
            </div>
            <RiskMeter score={customer.risk_score} level={customer.risk_level} />
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 mt-6 pt-4 border-t border-slate-800 text-xs font-semibold">
          {[
            { id: 'overview', label: 'Forensic Overview' },
            { id: 'network', label: 'Network Graph Visualizer' },
            { id: 'timeline', label: `Transaction Timeline (${customer.timeline.length})` },
            { id: 'report', label: 'Forensic Markdown Report' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-1.5 rounded-lg transition-colors ${
                activeTab === tab.id
                  ? 'bg-cyan-500 text-white shadow-sm'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Contents */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Top Section: Evidence Table & Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <EvidenceTable
                evidence={customer.evidence}
                protectiveFactors={customer.protective_factors}
                contributingSignals={customer.contributing_signals}
              />
            </div>

            {/* Right Panel: Investigator Actions & Shared Infrastructure */}
            <div className="space-y-6">
              {/* Investigator Action Plan */}
              <div className="glass-panel p-5 space-y-3 border-amber-500/20 bg-amber-950/10">
                <div className="flex items-center gap-2 pb-2 border-b border-amber-900/30">
                  <AlertTriangle className="text-amber-400" size={18} />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400">
                    Recommended Action Plan
                  </h3>
                </div>
                <div className="space-y-2">
                  {customer.recommendations.map((rec, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-xs text-slate-200">
                      <span className="font-mono text-amber-400 font-bold">{idx + 1}.</span>
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Shared Hardware Devices */}
              <div className="glass-panel p-5 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <Smartphone className="text-blue-400" size={16} />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                      Shared Hardware Devices
                    </h4>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">
                    {customer.shared_devices.length} Devices
                  </span>
                </div>

                {customer.shared_devices.length === 0 ? (
                  <p className="text-xs text-slate-400 italic">No shared devices detected for this endpoint.</p>
                ) : (
                  <div className="space-y-2.5">
                    {customer.shared_devices.map((dev, idx) => (
                      <div key={idx} className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-xs space-y-1">
                        <div className="flex justify-between font-mono font-bold text-blue-400">
                          <span>{dev.resource_id}</span>
                          <span className="text-slate-400 font-normal">{dev.shared_with_count} accounts</span>
                        </div>
                        <div className="text-[11px] text-slate-400 truncate">
                          Linked: {dev.connected_customers.join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Shared Payment Instruments */}
              <div className="glass-panel p-5 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <CreditCard className="text-amber-400" size={16} />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                      Shared Payment Instruments
                    </h4>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">
                    {customer.shared_payments.length} Cards/VPAs
                  </span>
                </div>

                {customer.shared_payments.length === 0 ? (
                  <p className="text-xs text-slate-400 italic">No shared payment methods detected.</p>
                ) : (
                  <div className="space-y-2.5">
                    {customer.shared_payments.map((pm, idx) => (
                      <div key={idx} className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-xs space-y-1">
                        <div className="flex justify-between font-mono font-bold text-amber-400">
                          <span>{pm.resource_id}</span>
                          <span className="text-slate-400 font-normal">{pm.shared_with_count} accounts</span>
                        </div>
                        <div className="text-[11px] text-slate-400 truncate">
                          Linked: {pm.connected_customers.join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Localized Network Canvas Preview */}
          {networkGraph && (
            <CytoscapeGraph
              graphData={networkGraph}
              height="400px"
              title={`Network Neighborhood (${customer.customer_id})`}
            />
          )}
        </div>
      )}

      {activeTab === 'network' && (
        <div className="space-y-4">
          {networkGraph ? (
            <CytoscapeGraph
              graphData={networkGraph}
              height="600px"
              title={`Full Forensic Network Neighborhood for ${customer.customer_id}`}
            />
          ) : (
            <div className="glass-panel p-12 text-center text-xs text-slate-400">No graph data found.</div>
          )}
        </div>
      )}

      {activeTab === 'timeline' && (
        <TimelineView timeline={customer.timeline} />
      )}

      {activeTab === 'report' && (
        <div className="glass-panel p-6 space-y-4 font-mono text-xs text-slate-300 leading-relaxed bg-[#070A11]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Deterministic Layer 1 & 2 Report Artifact
            </h3>
            <span className="text-[10px] text-cyan-400">Generated from Phase 4 Engine</span>
          </div>
          <pre className="whitespace-pre-wrap font-mono text-xs text-slate-300 bg-slate-950 p-4 rounded-xl border border-slate-800 overflow-x-auto">
            {customer.investigation_report_markdown || 'No markdown report artifact generated.'}
          </pre>
        </div>
      )}
    </div>
  );
}

export default CustomerDetailPage;
