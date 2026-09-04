import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Network, Smartphone, CreditCard, ArrowUpRight, ShieldAlert, Layers, Globe } from 'lucide-react';
import apiService from '../services/api';
import RiskBadge from '../components/RiskBadge';

export function FraudRingsPage() {
  const [rings, setRings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchRings() {
      try {
        setLoading(true);
        const data = await apiService.getFraudRings({ page: 1, pageSize: 50 });
        setRings(data.items || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchRings();
  }, []);

  return (
    <div className="space-y-4 pb-12">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-3 border-b border-soc-border">
        <div>
          <h1 className="text-xl font-extrabold text-slate-100 flex items-center gap-2 font-mono">
            <Network className="text-purple-400" size={20} />
            DETECTED FRAUD RINGS & SYNDICATES
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            26 coordinated syndicates isolated via Louvain Community Detection on shared hardware, payment instruments, and proxy IPs.
          </p>
        </div>
        <span className="text-xs text-purple-400 font-mono px-3 py-1 bg-purple-500/10 border border-purple-500/30 rounded font-bold">
          {rings.length} Active Syndicates
        </span>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64 text-purple-400">
          <div className="w-8 h-8 border-2 border-purple-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : error ? (
        <div className="soc-panel p-8 text-center text-xs text-red-400 font-mono">{error}</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {rings.map((ring) => (
            <div
              key={ring.ring_id}
              onClick={() => navigate(`/fraud-rings/${ring.ring_id}`)}
              className="soc-card p-4 cursor-pointer flex flex-col justify-between hover:border-purple-500/50 hover:bg-[#131A29] transition-all group relative overflow-hidden"
            >
              {/* Subtle top accent */}
              <div className="absolute top-0 left-0 right-0 h-[2px] bg-purple-500/40 group-hover:bg-purple-500 transition-colors" />

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-purple-500 group-hover:animate-soc-pulse"></span>
                    <h3 className="text-base font-bold font-mono text-slate-100 group-hover:text-purple-300">
                      {ring.ring_id}
                    </h3>
                  </div>
                  <RiskBadge level={ring.risk_level} score={ring.risk_score} size="sm" />
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-soc-border/80 text-xs font-mono">
                  <div>
                    <span className="text-[9px] uppercase font-bold text-slate-400">Scale</span>
                    <div className="font-bold text-slate-200 mt-0.5">
                      {ring.customer_count} Accounts
                    </div>
                  </div>
                  <div>
                    <span className="text-[9px] uppercase font-bold text-slate-400">Spend Volume</span>
                    <div className="font-bold text-slate-200 mt-0.5">
                      ₹{(ring.transaction_volume / 100000).toFixed(2)}L
                    </div>
                  </div>
                </div>

                {/* Infrastructure Highlights */}
                <div className="flex items-center gap-3 pt-2 text-[10px] text-slate-400 font-mono border-t border-soc-border/60">
                  <span className="flex items-center gap-1">
                    <Smartphone size={12} className="text-blue-400" />
                    {ring.shared_devices_count} Devices
                  </span>
                  <span className="flex items-center gap-1">
                    <CreditCard size={12} className="text-amber-400" />
                    {ring.shared_payments_count} Cards/VPAs
                  </span>
                </div>
              </div>

              {/* Action Jump */}
              <div className="mt-3 pt-2.5 border-t border-soc-border/70 flex items-center justify-between text-xs font-mono font-semibold text-purple-400 group-hover:text-purple-300">
                <span>Inspect Syndicate Graph</span>
                <ArrowUpRight size={13} className="group-hover:translate-x-0.5 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FraudRingsPage;
