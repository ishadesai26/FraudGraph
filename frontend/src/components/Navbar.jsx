import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldAlert, Search, Network, Sparkles, Activity } from 'lucide-react';

export function Navbar() {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    const q = searchQuery.trim().toUpperCase();
    if (!q) return;

    if (q.startsWith('CUST_') || q.startsWith('C') || (!isNaN(q) && q.length <= 5)) {
      const custId = q.startsWith('CUST_') ? q : `CUST_${q.replace(/\D/g, '').padStart(5, '0')}`;
      navigate(`/customers/${custId}`);
    } else if (q.startsWith('TXN_') || q.startsWith('T')) {
      const txnId = q.startsWith('TXN_') ? q : `TXN_${q.replace(/\D/g, '').padStart(5, '0')}`;
      navigate(`/transactions/${txnId}`);
    } else if (q.startsWith('FR_') || q.startsWith('RING_') || q.startsWith('F')) {
      const ringId = q.startsWith('FR_') ? q : `FR_${q.replace(/\D/g, '').padStart(3, '0')}`;
      navigate(`/fraud-rings/${ringId}`);
    } else {
      navigate(`/customers?search=${encodeURIComponent(q)}`);
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-[#0B0F19]/90 backdrop-blur-md sticky top-0 z-50 px-6 flex items-center justify-between">
      {/* Brand */}
      <div className="flex items-center gap-4">
        <Link to="/" className="flex items-center gap-2.5 text-slate-100 hover:opacity-90 transition-opacity">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20">
            <Network size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-slate-100 via-cyan-200 to-cyan-400 bg-clip-text text-transparent">
                FraudGraph
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                Phase 5
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-medium hidden sm:block">
              Network Intelligence for Coordinated Fraud Detection
            </p>
          </div>
        </Link>
      </div>

      {/* Center Search */}
      <form onSubmit={handleSearch} className="max-w-md w-full mx-4 hidden md:block">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input
            type="text"
            placeholder="Search Customer (CUST_00028), Transaction (TXN_00001), or Ring (FR_017)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-900 border border-slate-700/80 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 font-mono transition-colors"
          />
        </div>
      </form>

      {/* Quick Demo Shortcuts & Status */}
      <div className="flex items-center gap-3">
        <div className="hidden lg:flex items-center gap-2">
          <button
            onClick={() => navigate('/customers/CUST_00028')}
            className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20 transition-colors flex items-center gap-1.5"
          >
            <ShieldAlert size={14} />
            <span>Demo Customer (99.1 Risk)</span>
          </button>
          <button
            onClick={() => navigate('/fraud-rings/FR_017')}
            className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/30 hover:bg-purple-500/20 transition-colors flex items-center gap-1.5"
          >
            <Network size={14} />
            <span>Demo Syndicate Ring (100.0)</span>
          </button>
        </div>

        {/* Live Status Pill */}
        <div className="flex items-center gap-2 pl-3 border-l border-slate-800 text-xs font-medium text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="hidden sm:inline">Engine Live</span>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
