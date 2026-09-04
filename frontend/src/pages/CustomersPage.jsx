import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Search,
  Filter,
  Users,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ShieldAlert,
  ArrowUpRight,
} from 'lucide-react';
import apiService from '../services/api';
import RiskBadge from '../components/RiskBadge';

export function CustomersPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const page = parseInt(searchParams.get('page') || '1', 10);
  const pageSize = 25;
  const riskLevel = searchParams.get('risk_level') || 'ALL';
  const searchQuery = searchParams.get('search') || '';
  const minRiskScore = searchParams.get('min_score') || '';

  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [searchInput, setSearchInput] = useState(searchQuery);

  useEffect(() => {
    async function fetchCustomers() {
      try {
        setLoading(true);
        const data = await apiService.getCustomers({
          page,
          pageSize,
          riskLevel: riskLevel !== 'ALL' ? riskLevel : undefined,
          search: searchQuery || undefined,
          minRiskScore: minRiskScore ? parseFloat(minRiskScore) : undefined,
        });
        setCustomers(data.items || []);
        setTotal(data.total || 0);
        setTotalPages(data.total_pages || 1);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchCustomers();
  }, [page, riskLevel, searchQuery, minRiskScore]);

  const updateParam = (key, value) => {
    const params = new URLSearchParams(searchParams);
    if (value && value !== 'ALL') {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    params.set('page', '1');
    setSearchParams(params);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    updateParam('search', searchInput.trim());
  };

  return (
    <div className="space-y-4 pb-12">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-3 border-b border-soc-border">
        <div>
          <h1 className="text-xl font-extrabold text-slate-100 flex items-center gap-2 font-mono">
            <Users className="text-cyan-400" size={20} />
            MONITORED CUSTOMER REGISTRY
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time entity surveillance index correlating 2,000 accounts across multi-entity relational graphs and behavioral models.
          </p>
        </div>
        <span className="text-xs text-slate-300 font-mono px-3 py-1 bg-soc-panel border border-soc-border rounded font-bold">
          {total.toLocaleString()} Records Indexed
        </span>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="soc-panel p-3.5 flex flex-wrap items-center justify-between gap-3">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="flex-1 min-w-[260px] max-w-md relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
          <input
            type="text"
            placeholder="Filter by Customer ID, City, or Signal..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-soc-surface border border-soc-border rounded text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </form>

        {/* Risk Level Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((lvl) => (
            <button
              key={lvl}
              onClick={() => updateParam('risk_level', lvl)}
              className={`px-3 py-1 text-xs font-mono font-semibold rounded transition-colors ${
                riskLevel === lvl
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                  : 'bg-soc-surface border border-soc-border text-slate-400 hover:text-slate-200'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {/* Main Table */}
      <div className="soc-panel overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64 text-cyan-400">
            <div className="w-7 h-7 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-xs text-red-400 font-mono">{error}</div>
        ) : customers.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400 font-mono italic">
            No customers match the current filter criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-soc-border text-[10px] font-bold text-slate-400 uppercase tracking-wider bg-soc-panel font-mono">
                  <th className="py-2.5 px-4">Customer ID</th>
                  <th className="py-2.5 px-4">Name & City</th>
                  <th className="py-2.5 px-4">Composite Risk</th>
                  <th className="py-2.5 px-4">Syndicate Ring</th>
                  <th className="py-2.5 px-4">Top Risk Signal</th>
                  <th className="py-2.5 px-4 text-right">Transactions & Spend</th>
                  <th className="py-2.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-soc-border/60 text-xs">
                {customers.map((cust) => (
                  <tr
                    key={cust.customer_id}
                    onClick={() => navigate(`/customers/${cust.customer_id}`)}
                    className="hover:bg-soc-surface-hover cursor-pointer transition-colors group"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-cyan-400 group-hover:underline">
                      {cust.customer_id}
                    </td>
                    <td className="py-3 px-4 text-slate-200">
                      <div className="font-medium text-slate-100">{cust.name}</div>
                      <div className="text-[10px] text-slate-400 font-mono">{cust.home_city}</div>
                    </td>
                    <td className="py-3 px-4">
                      <RiskBadge level={cust.risk_level} score={cust.risk_score} size="sm" />
                    </td>
                    <td className="py-3 px-4">
                      {cust.ring_id ? (
                        <span className="px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 font-mono text-[10px]">
                          {cust.ring_id}
                        </span>
                      ) : (
                        <span className="text-slate-400 font-mono text-[10px]">Isolated</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-mono text-[11px]">
                      {cust.top_signal.replace(/_/g, ' ')}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-200">
                      <div>{cust.total_transactions} txns</div>
                      <div className="text-[10px] text-slate-400">₹{cust.total_spend.toLocaleString('en-IN')}</div>
                    </td>
                    <td className="py-3 px-4 text-right text-cyan-400">
                      <span className="text-[11px] font-mono font-bold inline-flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                        Inspect <ArrowUpRight size={13} />
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls */}
        <div className="p-3 border-t border-soc-border flex items-center justify-between text-xs text-slate-400 bg-soc-panel font-mono">
          <span>
            Page <strong className="text-slate-200">{page}</strong> of <strong className="text-slate-200">{totalPages}</strong>
          </span>
          <div className="flex items-center gap-1.5">
            <button
              disabled={page <= 1}
              onClick={() => {
                const params = new URLSearchParams(searchParams);
                params.set('page', String(page - 1));
                setSearchParams(params);
              }}
              className="p-1 rounded border border-soc-border bg-soc-surface text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-800"
            >
              <ChevronLeft size={15} />
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => {
                const params = new URLSearchParams(searchParams);
                params.set('page', String(page + 1));
                setSearchParams(params);
              }}
              className="p-1 rounded border border-soc-border bg-soc-surface text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-800"
            >
              <ChevronRight size={15} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CustomersPage;
