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
  Copy,
  Check,
  Zap,
  Layers,
  ArrowUpRight,
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
  const [activeTab, setActiveTab] = useState('overview');
  const [copiedReport, setCopiedReport] = useState(false);

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

  const handleCopyReport = () => {
    if (!customer?.investigation_report_markdown) return;
    navigator.clipboard.writeText(customer.investigation_report_markdown);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2000);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 text-cyan-400">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs font-mono text-slate-400">Compiling Forensic Case Dossier for {customerId}...</p>
        </div>
      </div>
    );
  }

  if (error || !customer) {
    return (
      <div className="space-y-4 p-4">
        <button
          onClick={() => navigate('/customers')}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 font-mono"
        >
          <ArrowLeft size={14} /> Back to Customer Registry
        </button>
        <div className="soc-panel p-8 text-center text-xs text-red-400 space-y-2 border-red-500/30">
          <AlertTriangle className="mx-auto text-red-400" size={30} />
          <h3 className="text-sm font-bold text-red-300 font-mono">Customer Investigation Profile Error</h3>
          <p className="font-mono">{error || `Customer '${customerId}' not found in registry.`}</p>
        </div>
      </div>
    );
  }

  const hasRing = customer.associated_ring_id && customer.associated_ring_id !== 'None (Isolated Node)';

  return (
    <div className="space-y-5 pb-16">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
        <Link to="/customers" className="hover:text-slate-200 transition-colors">Customers</Link>
        <ChevronRight size={13} />
        <span className="text-slate-200 font-bold">{customer.customer_id}</span>
      </div>

      {/* Hero Dossier Header */}
      <div className="soc-panel p-5 relative overflow-hidden bg-gradient-to-r from-[#0D131F] via-[#0D131F] to-[#141A28] border-soc-border">
        <div className="flex flex-wrap items-start justify-between gap-6">
          {/* Left: Customer Demographics */}
          <div className="space-y-2.5 max-w-2xl">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-extrabold text-slate-100 font-mono tracking-tight">
                {customer.customer_id}
              </h1>
              <RiskBadge level={customer.risk_level} score={customer.risk_score} size="lg" />
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-soc-surface text-slate-300 border border-soc-border">
                Confidence: <strong className="text-cyan-400 font-bold">{customer.explanation_confidence}</strong>
              </span>
            </div>

            <p className="text-sm font-semibold text-slate-200">{customer.name}</p>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 font-mono pt-1">
              <span className="flex items-center gap-1.5">
                <MapPin size={13} className="text-cyan-400" />
                {customer.home_city}
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar size={13} className="text-amber-400" />
                {customer.account_age_days} Days Tenure
              </span>
              <span className="flex items-center gap-1.5">
                <ShieldCheck size={13} className="text-emerald-400" />
                {customer.kyc_verified ? 'KYC Verified' : 'KYC Pending'}
              </span>
              {hasRing && (
                <Link
                  to={`/fraud-rings/${customer.associated_ring_id}`}
                  className="flex items-center gap-1.5 text-purple-400 hover:text-purple-300 hover:underline font-bold"
                >
                  <Network size={13} />
                  Syndicate {customer.associated_ring_id} ({customer.member_role || 'MEMBER'})
                </Link>
              )}
            </div>
          </div>

          {/* Right: Spend Metrics & Circular Risk Meter */}
          <div className="flex items-center gap-4">
            <div className="p-3 bg-soc-panel border border-soc-border rounded text-right font-mono">
              <span className="text-[9px] uppercase font-bold text-slate-400">Historical Volume</span>
              <div className="text-base font-bold text-slate-100 mt-0.5">
                ₹{customer.total_spend.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
              <span className="text-[10px] text-slate-400">{customer.total_transactions} Transactions</span>
            </div>
            <RiskMeter score={customer.risk_score} level={customer.risk_level} />
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 mt-5 pt-3 border-t border-soc-border text-xs font-mono font-semibold">
          {[
            { id: 'overview', label: 'Forensic Overview' },
            { id: 'network', label: 'Network Visualizer' },
            { id: 'timeline', label: `Timeline (${customer.timeline.length})` },
            { id: 'report', label: 'XAI Markdown Report' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded transition-colors ${
                activeTab === tab.id
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                  : 'bg-soc-surface border border-soc-border text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Contents */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          {/* Top Section: Evidence Table & Connected Infrastructure */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2">
              <EvidenceTable
                evidence={customer.evidence}
                protectiveFactors={customer.protective_factors}
                contributingSignals={customer.contributing_signals}
              />
            </div>

            {/* Right Column: Investigator Recommendations & Infrastructure */}
            <div className="space-y-4">
              {/* Action Plan */}
              <div className="soc-panel p-4 space-y-2.5 border-amber-500/25 bg-amber-950/10">
                <div className="flex items-center gap-2 pb-2 border-b border-amber-900/30">
                  <AlertTriangle className="text-amber-400" size={15} />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 font-mono">
                    RECOMMENDED DISPOSITION PLAN
                  </h3>
                </div>
                <div className="space-y-2">
                  {customer.recommendations.map((rec, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-xs text-slate-200">
                      <span className="font-mono text-amber-400 font-bold">{idx + 1}.</span>
                      <span className="leading-relaxed">{rec}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Connected Devices */}
              <div className="soc-panel p-4 space-y-2.5">
                <div className="flex items-center justify-between pb-2 border-b border-soc-border">
                  <div className="flex items-center gap-1.5">
                    <Smartphone className="text-blue-400" size={15} />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
                      SHARED HARDWARE DEVICES
                    </h4>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">
                    {customer.shared_devices.length} Devices
                  </span>
                </div>

                {customer.shared_devices.length === 0 ? (
                  <p className="text-xs text-slate-400 font-mono italic">No shared devices detected.</p>
                ) : (
                  <div className="space-y-2">
                    {customer.shared_devices.map((dev, idx) => (
                      <div key={idx} className="p-2.5 bg-soc-surface border border-soc-border rounded text-xs space-y-1">
                        <div className="flex justify-between font-mono font-bold text-blue-400">
                          <span>{dev.resource_id}</span>
                          <span className="text-slate-400 font-normal">{dev.shared_with_count} accounts</span>
                        </div>
                        <div className="text-[10px] text-slate-400 font-mono truncate">
                          Linked: {dev.connected_customers.join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Connected Payment Instruments */}
              <div className="soc-panel p-4 space-y-2.5">
                <div className="flex items-center justify-between pb-2 border-b border-soc-border">
                  <div className="flex items-center gap-1.5">
                    <CreditCard className="text-amber-400" size={15} />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
                      SHARED PAYMENT INSTRUMENTS
                    </h4>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">
                    {customer.shared_payments.length} Instruments
                  </span>
                </div>

                {customer.shared_payments.length === 0 ? (
                  <p className="text-xs text-slate-400 font-mono italic">No shared payment instruments detected.</p>
                ) : (
                  <div className="space-y-2">
                    {customer.shared_payments.map((pm, idx) => (
                      <div key={idx} className="p-2.5 bg-soc-surface border border-soc-border rounded text-xs space-y-1">
                        <div className="flex justify-between font-mono font-bold text-amber-400">
                          <span>{pm.resource_id}</span>
                          <span className="text-slate-400 font-normal">{pm.shared_with_count} accounts</span>
                        </div>
                        <div className="text-[10px] text-slate-400 font-mono truncate">
                          Linked: {pm.connected_customers.join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Localized Network Neighborhood Canvas Preview */}
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
              height="620px"
              title={`Full Forensic Network Neighborhood for ${customer.customer_id}`}
            />
          ) : (
            <div className="soc-panel p-12 text-center text-xs text-slate-400 font-mono">No graph data found.</div>
          )}
        </div>
      )}

      {activeTab === 'timeline' && (
        <TimelineView timeline={customer.timeline} />
      )}

      {activeTab === 'report' && (
        <div className="soc-panel p-5 space-y-3 font-mono text-xs text-slate-300 leading-relaxed bg-[#080B11]">
          <div className="flex items-center justify-between pb-2.5 border-b border-soc-border">
            <div className="flex items-center gap-2">
              <FileText size={15} className="text-cyan-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
                XAI DETERMINISTIC FORENSIC REPORT ARTIFACT
              </h3>
            </div>
            <button
              onClick={handleCopyReport}
              className="px-3 py-1 rounded bg-soc-surface hover:bg-slate-800 text-slate-200 border border-soc-border flex items-center gap-1.5 transition-colors font-mono text-xs"
            >
              {copiedReport ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
              <span>{copiedReport ? 'Copied to Clipboard' : 'Copy Report Markdown'}</span>
            </button>
          </div>

          <pre className="whitespace-pre-wrap font-mono text-xs text-slate-300 bg-[#0A0E18] p-4 rounded border border-soc-border overflow-x-auto leading-relaxed">
            {customer.investigation_report_markdown || 'No markdown report artifact generated.'}
          </pre>
        </div>
      )}
    </div>
  );
}

export default CustomerDetailPage;
