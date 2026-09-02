import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Network, Smartphone, CreditCard, ArrowUpRight, ShieldAlert, Layers } from 'lucide-react';
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
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-extrabold text-slate-100 flex items-center gap-2">
            <Network className="text-purple-400" size={22} />
            Detected Fraud Rings & Syndicates
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            26 coordinated syndicates identified via Louvain Community Detection and multi-entity graph linking.
          </p>
        </div>
        <span className="text-xs text-purple-400 font-mono px-3 py-1 bg-purple-500/10 border border-purple-500/30 rounded-lg">
          {rings.length} Syndicates Active
        </span>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64 text-purple-400">
          <div className="w-8 h-8 border-2 border-purple-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : error ? (
        <div className="glass-panel p-8 text-center text-xs text-red-400">{error}</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {rings.map((ring) => (
            <div
              key={ring.ring_id}
              onClick={() => navigate(`/fraud-rings/${ring.ring_id}`)}
              className="glass-card p-5 cursor-pointer flex flex-col justify-between hover:border-purple-500/50 hover:shadow-purple-500/10 transition-all group"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-purple-500 group-hover:animate-pulse"></span>
                    <h3 className="text-base font-bold font-mono text-slate-100 group-hover:text-purple-300">
                      {ring.ring_id}
                    </h3>
                  </div>
                  <RiskBadge level={ring.risk_level} score={ring.risk_score} size="sm" />
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/80 text-xs">
                  <div>
                    <span className="text-[10px] uppercase font-semibold text-slate-500">Scale</span>
                    <div className="font-mono font-bold text-slate-200 mt-0.5">
                      {ring.customer_count} Members
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-semibold text-slate-500">Volume</span>
                    <div className="font-mono font-bold text-slate-200 mt-0.5">
                      ₹{(ring.transaction_volume / 100000).toFixed(2)}L
                    </div>
                  </div>
                </div>

                {/* Shared Infrastructure Highlights */}
                <div className="flex items-center gap-3 pt-2 text-[11px] text-slate-400 font-mono">
                  <span className="flex items-center gap-1">
                    <Smartphone size={13} className="text-blue-400" />
                    {ring.shared_devices_count} Devices
                  </span>
                  <span className="flex items-center gap-1">
                    <CreditCard size={13} className="text-amber-400" />
                    {ring.shared_payments_count} Cards/VPAs
                  </span>
                </div>
              </div>

              {/* Action Link */}
              <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs font-semibold text-purple-400 group-hover:text-purple-300">
                <span>Inspect Syndicate Graph</span>
                <ArrowUpRight size={14} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FraudRingsPage;
