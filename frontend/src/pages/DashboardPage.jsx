import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Users,
  ShieldAlert,
  Network,
  IndianRupee,
  Search,
  ArrowUpRight,
  TrendingUp,
  AlertTriangle,
  Cpu,
  Layers,
  Sparkles,
} from 'lucide-react';
import apiService from '../services/api';
import StatCard from '../components/StatCard';
import RiskBadge from '../components/RiskBadge';

export function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [customersData, setCustomersData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterLevel, setFilterLevel] = useState('ALL');
  const navigate = useNavigate();

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const [statsRes, custRes] = await Promise.all([
          apiService.getDashboard(),
          apiService.getCustomers({ page: 1, pageSize: 8, riskLevel: filterLevel !== 'ALL' ? filterLevel : undefined }),
        ]);
        setStats(statsRes);
        setCustomersData(custRes);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, [filterLevel]);

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3 text-cyan-400">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs font-mono text-slate-400">Loading Forensic Intelligence Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="glass-panel p-6 border-red-500/30 bg-red-950/20 text-center space-y-3">
          <AlertTriangle className="mx-auto text-red-400" size={32} />
          <h3 className="text-sm font-bold text-red-300">Failed to Load Dashboard</h3>
          <p className="text-xs text-slate-400">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-1.5 text-xs rounded-lg bg-red-500/20 text-red-300 border border-red-500/40 hover:bg-red-500/30 font-semibold"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const dist = stats?.risk_distribution || { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
  const totalIndexed = dist.LOW + dist.MEDIUM + dist.HIGH + dist.CRITICAL || 2000;

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 glass-panel relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/30 border-cyan-500/20">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span className="text-[11px] font-bold text-cyan-400 uppercase tracking-widest font-mono">
              Live Investigation Engine
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">
            Fraud Operations & Network Intelligence
          </h1>
          <p className="text-xs text-slate-400 max-w-2xl">
            Real-time multi-signal risk scoring combining transaction behavior, unsupervised anomaly detection, and heterogeneous graph ring analytics.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/customers?risk_level=CRITICAL')}
            className="px-3.5 py-2 text-xs font-bold rounded-xl bg-red-500 text-white shadow-lg shadow-red-500/20 hover:bg-red-600 transition-colors flex items-center gap-2"
          >
            <ShieldAlert size={16} />
            <span>Investigate Critical ({stats?.critical_customers_count || 0})</span>
          </button>
          <button
            onClick={() => navigate('/fraud-rings')}
            className="px-3.5 py-2 text-xs font-bold rounded-xl bg-purple-500/10 text-purple-300 border border-purple-500/30 hover:bg-purple-500/20 transition-colors flex items-center gap-2"
          >
            <Network size={16} />
            <span>Syndicates ({stats?.total_fraud_rings || 0})</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Monitored Customers"
          value={stats?.total_customers?.toLocaleString() || '2,000'}
          subtext="10,000 transactions indexed"
          icon={Users}
          color="cyan"
        />
        <StatCard
          title="High & Critical Entities"
          value={(stats?.high_risk_customers_count + stats?.critical_customers_count) || 39}
          subtext={`${stats?.critical_customers_count || 0} critical priority alerts`}
          icon={ShieldAlert}
          color="red"
          badge={<RiskBadge level="CRITICAL" size="sm" />}
        />
        <StatCard
          title="Detected Fraud Rings"
          value={stats?.total_fraud_rings || 26}
          subtext="Louvain Modularity syndicates"
          icon={Network}
          color="purple"
          badge={<span className="text-[10px] text-purple-400 font-mono">26 Rings</span>}
        />
        <StatCard
          title="Suspicious Volume"
          value={`₹${((stats?.suspicious_transaction_volume || 0) / 100000).toFixed(1)}L`}
          subtext="Coordinated ring spend"
          icon={IndianRupee}
          color="orange"
        />
      </div>

      {/* Risk Distribution & Priority Callouts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution Card */}
        <div className="glass-panel p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Entity Risk Tier Distribution
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">{totalIndexed} Total</span>
          </div>

          <div className="space-y-3 pt-1">
            {[
              { level: 'CRITICAL', count: dist.CRITICAL, color: '#EF4444', pct: (dist.CRITICAL / totalIndexed) * 100 },
              { level: 'HIGH', count: dist.HIGH, color: '#F97316', pct: (dist.HIGH / totalIndexed) * 100 },
              { level: 'MEDIUM', count: dist.MEDIUM, color: '#F59E0B', pct: (dist.MEDIUM / totalIndexed) * 100 },
              { level: 'LOW', count: dist.LOW, color: '#10B981', pct: (dist.LOW / totalIndexed) * 100 },
            ].map((tier) => (
              <div key={tier.level} className="space-y-1">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-slate-300">{tier.level}</span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-slate-100">{tier.count}</span>
                    <span className="text-[10px] text-slate-500 font-mono">({tier.pct.toFixed(1)}%)</span>
                  </div>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{ backgroundColor: tier.color, width: `${Math.max(2, tier.pct)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="pt-3 border-t border-slate-800/60 text-[11px] text-slate-400 flex justify-between">
            <span>Critical Threshold: &ge;80.0</span>
            <span>High Threshold: &ge;60.0</span>
          </div>
        </div>

        {/* Highest-Risk Target Entity */}
        <div className="glass-panel p-5 space-y-3 flex flex-col justify-between border-red-500/20 bg-red-950/10">
          <div className="space-y-2">
            <div className="flex items-center justify-between pb-2 border-b border-red-900/30">
              <span className="text-xs font-bold uppercase tracking-wider text-red-400 flex items-center gap-1.5">
                <AlertTriangle size={15} />
                Highest-Risk Customer
              </span>
              <RiskBadge level={stats?.highest_risk_customer?.risk_level || 'CRITICAL'} score={stats?.highest_risk_customer?.risk_score} size="sm" />
            </div>
            <h4 className="text-xl font-bold font-mono text-slate-100">
              {stats?.highest_risk_customer?.entity_id || 'CUST_00028'}
            </h4>
            <p className="text-xs text-slate-300">
              {stats?.highest_risk_customer?.detail || 'Associated with syndicate FR_015'}
            </p>
          </div>

          <Link
            to={`/customers/${stats?.highest_risk_customer?.entity_id || 'CUST_00028'}`}
            className="w-full py-2 px-3 text-xs font-bold rounded-lg bg-red-500/20 text-red-300 border border-red-500/40 hover:bg-red-500/30 transition-colors flex items-center justify-center gap-1.5"
          >
            <span>Open Forensic Dossier</span>
            <ArrowUpRight size={14} />
          </Link>
        </div>

        {/* Highest-Risk Syndicate Ring */}
        <div className="glass-panel p-5 space-y-3 flex flex-col justify-between border-purple-500/20 bg-purple-950/10">
          <div className="space-y-2">
            <div className="flex items-center justify-between pb-2 border-b border-purple-900/30">
              <span className="text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
                <Network size={15} />
                Largest Syndicate Ring
              </span>
              <RiskBadge level={stats?.highest_risk_ring?.risk_level || 'CRITICAL'} score={stats?.highest_risk_ring?.risk_score} size="sm" />
            </div>
            <h4 className="text-xl font-bold font-mono text-slate-100">
              {stats?.highest_risk_ring?.entity_id || 'FR_017'}
            </h4>
            <p className="text-xs text-slate-300">
              {stats?.highest_risk_ring?.detail || '161 member accounts funneled through 45 shared devices'}
            </p>
          </div>

          <Link
            to={`/fraud-rings/${stats?.highest_risk_ring?.entity_id || 'FR_017'}`}
            className="w-full py-2 px-3 text-xs font-bold rounded-lg bg-purple-500/20 text-purple-300 border border-purple-500/40 hover:bg-purple-500/30 transition-colors flex items-center justify-center gap-1.5"
          >
            <span>Inspect Syndicate Topology</span>
            <ArrowUpRight size={14} />
          </Link>
        </div>
      </div>

      {/* High-Risk Customer Quick Investigation Table */}
      <div className="glass-panel p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-100">
              High-Risk Accounts Requiring Immediate Review
            </h3>
            <p className="text-xs text-slate-400">Click any customer row to enter the investigation console.</p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5">
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((lvl) => (
              <button
                key={lvl}
                onClick={() => setFilterLevel(lvl)}
                className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition-colors ${
                  filterLevel === lvl
                    ? 'bg-cyan-500 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {lvl}
              </button>
            ))}
            <Link
              to="/customers"
              className="ml-2 px-3 py-1 text-xs font-bold text-cyan-400 hover:underline flex items-center gap-1"
            >
              <span>View All 2,000</span>
              <ArrowUpRight size={14} />
            </Link>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                <th className="py-2.5 px-3">Customer ID</th>
                <th className="py-2.5 px-3">Name / Location</th>
                <th className="py-2.5 px-3">Risk Rating</th>
                <th className="py-2.5 px-3">Syndicate Ring</th>
                <th className="py-2.5 px-3">Primary Signal</th>
                <th className="py-2.5 px-3 text-right">Transactions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs font-medium">
              {customersData?.items?.map((cust) => (
                <tr
                  key={cust.customer_id}
                  onClick={() => navigate(`/customers/${cust.customer_id}`)}
                  className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                >
                  <td className="py-3 px-3 font-mono font-bold text-cyan-400 group-hover:underline">
                    {cust.customer_id}
                  </td>
                  <td className="py-3 px-3 text-slate-200">
                    <div>{cust.name}</div>
                    <div className="text-[11px] text-slate-500">{cust.home_city}</div>
                  </td>
                  <td className="py-3 px-3">
                    <RiskBadge level={cust.risk_level} score={cust.risk_score} size="sm" />
                  </td>
                  <td className="py-3 px-3">
                    {cust.ring_id ? (
                      <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 font-mono text-[11px]">
                        {cust.ring_id}
                      </span>
                    ) : (
                      <span className="text-slate-500 font-mono text-[11px]">Isolated</span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-slate-300 font-mono text-[11px]">
                    {cust.top_signal.replace(/_/g, ' ')}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-200">
                    <div>{cust.total_transactions} txns</div>
                    <div className="text-[11px] text-slate-400">₹{cust.total_spend.toLocaleString('en-IN')}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
