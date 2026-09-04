import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  ShieldAlert,
  Search,
  Network,
  Activity,
  Zap,
  Bot,
  UserCheck,
  ChevronDown,
  ArrowUpRight,
  Command,
  X,
  Terminal,
} from 'lucide-react';

export function Navbar() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFocused, setSearchFocused] = useState(false);
  const searchInputRef = useRef(null);
  const navigate = useNavigate();

  // Keyboard shortcut listener: Press '/' or 'Ctrl+K' to focus search command palette
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.key === '/' || (e.ctrlKey && e.key === 'k')) && document.activeElement !== searchInputRef.current) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
      if (e.key === 'Escape' && document.activeElement === searchInputRef.current) {
        searchInputRef.current?.blur();
        setSearchFocused(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSearch = (e) => {
    e?.preventDefault();
    const q = searchQuery.trim().toUpperCase();
    if (!q) return;
    setSearchFocused(false);

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

  const handleSelectQuickTarget = (targetPath) => {
    setSearchFocused(false);
    navigate(targetPath);
  };

  return (
    <header className="h-14 border-b border-soc-border bg-[#090D16] sticky top-0 z-50 px-4 md:px-6 flex items-center justify-between select-none">
      {/* Brand & Identity */}
      <div className="flex items-center gap-4">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-cyan-600 to-blue-700 flex items-center justify-center text-white shadow-sm border border-cyan-400/30 group-hover:border-cyan-400 transition-colors">
            <Network size={18} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-sm tracking-tight text-slate-100 font-mono">
                FRAUDGRAPH
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
                SOC L3
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono hidden sm:block">
              Network Intelligence & Autonomous Investigation
            </p>
          </div>
        </Link>
      </div>

      {/* Center Command Palette Search */}
      <div className="relative max-w-lg w-full mx-4 hidden md:block">
        <form onSubmit={handleSearch}>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Command search (e.g. CUST_00028, FR_017, TXN_00001)... [Ctrl+K or /]"
              value={searchQuery}
              onFocus={() => setSearchFocused(true)}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-14 py-1.5 text-xs bg-[#0D131F] border border-soc-border rounded text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500 font-mono transition-colors shadow-inner"
            />
            <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1">
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery('')}
                  className="text-slate-400 hover:text-slate-200 mr-1"
                >
                  <X size={12} />
                </button>
              )}
              <kbd className="text-[9px] font-mono text-slate-400 bg-slate-800 px-1 py-0.5 rounded border border-slate-700">
                ⌘K
              </kbd>
            </div>
          </div>
        </form>

        {/* Command Palette Dropdown */}
        {searchFocused && (
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setSearchFocused(false)}
            />
            <div className="absolute left-0 right-0 top-full mt-1.5 bg-[#0D131F] border border-soc-border rounded shadow-2xl z-50 p-2 text-xs font-mono animate-in fade-in zoom-in-95 duration-150">
              <div className="px-2 py-1 text-[10px] text-slate-400 uppercase font-bold border-b border-soc-border mb-1 flex justify-between items-center">
                <span>QUICK INVESTIGATION TARGETS</span>
                <span>ESC TO CLOSE</span>
              </div>
              <div className="space-y-1">
                <button
                  onClick={() => handleSelectQuickTarget('/customers/CUST_00028')}
                  className="w-full text-left px-2.5 py-1.5 rounded hover:bg-soc-surface transition-colors flex items-center justify-between text-slate-300 hover:text-white group"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
                    <span className="font-bold text-red-400 group-hover:text-red-300">CUST_00028</span>
                    <span className="text-[10px] text-slate-400 truncate max-w-[200px]">Highest Risk Customer (Score: 99.1)</span>
                  </div>
                  <span className="text-[9px] px-1 py-0.2 rounded bg-red-500/20 text-red-300 border border-red-500/30 font-bold">
                    CRITICAL
                  </span>
                </button>

                <button
                  onClick={() => handleSelectQuickTarget('/fraud-rings/FR_017')}
                  className="w-full text-left px-2.5 py-1.5 rounded hover:bg-soc-surface transition-colors flex items-center justify-between text-slate-300 hover:text-white group"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse"></span>
                    <span className="font-bold text-purple-400 group-hover:text-purple-300">FR_017</span>
                    <span className="text-[10px] text-slate-400 truncate max-w-[200px]">Largest Syndicate (161 Accounts · 45 Devices)</span>
                  </div>
                  <span className="text-[9px] px-1 py-0.2 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold">
                    SYNDICATE
                  </span>
                </button>

                <button
                  onClick={() => handleSelectQuickTarget('/transactions/TXN_00001')}
                  className="w-full text-left px-2.5 py-1.5 rounded hover:bg-soc-surface transition-colors flex items-center justify-between text-slate-300 hover:text-white group"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                    <span className="font-bold text-cyan-400 group-hover:text-cyan-300">TXN_00001</span>
                    <span className="text-[10px] text-slate-400 truncate max-w-[200px]">Ingress Transaction Log & Audit Trace</span>
                  </div>
                  <span className="text-[9px] px-1 py-0.2 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-bold">
                    RECORD
                  </span>
                </button>

                <button
                  onClick={() => handleSelectQuickTarget('/simulation')}
                  className="w-full text-left px-2.5 py-1.5 rounded hover:bg-soc-surface transition-colors flex items-center justify-between text-slate-300 hover:text-white border-t border-soc-border/50 pt-1.5"
                >
                  <div className="flex items-center gap-2">
                    <Zap size={13} className="text-amber-400" />
                    <span className="font-bold text-amber-300">Live Attack Simulator</span>
                    <span className="text-[10px] text-slate-400">Test Ingress & Ring Scenarios</span>
                  </div>
                  <ArrowUpRight size={12} className="text-slate-400" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Right Telemetry, Target Chips & Operator Pill */}
      <div className="flex items-center gap-3">
        {/* Quick Focus Targets */}
        <div className="hidden xl:flex items-center gap-2">
          <button
            onClick={() => navigate('/customers/CUST_00028')}
            className="px-2.5 py-1 text-[11px] font-mono font-bold rounded bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20 transition-all flex items-center gap-1.5 group"
            title="Focus Target: CUST_00028"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span>
            <span>Target: CUST_00028</span>
            <span className="text-[9px] px-1 rounded bg-red-500/20 text-red-300">99.1</span>
          </button>
          <button
            onClick={() => navigate('/fraud-rings/FR_017')}
            className="px-2.5 py-1 text-[11px] font-mono font-bold rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 hover:bg-purple-500/20 transition-all flex items-center gap-1.5 group"
            title="Focus Syndicate: FR_017"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></span>
            <span>Syndicate: FR_017 (161)</span>
          </button>
        </div>

        {/* Engine Telemetry Status */}
        <div className="flex items-center gap-3 pl-3 border-l border-soc-border text-xs font-mono">
          <div className="flex items-center gap-1.5" title="Engine Status: Active L3 Defense">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-soc-pulse"></span>
            <span className="text-[11px] text-slate-200 font-bold hidden sm:inline">L3 ACTIVE</span>
          </div>
          <div className="hidden lg:flex items-center gap-1 text-[11px] text-slate-400 border-l border-soc-border pl-3" title="Random Forest Classifier AUC">
            <span className="text-slate-400">AUC:</span>
            <span className="text-emerald-400 font-bold">99.8%</span>
          </div>
        </div>

        {/* Analyst / Operator Profile Pill */}
        <div className="flex items-center gap-2 pl-3 border-l border-soc-border">
          <div className="w-7 h-7 rounded bg-gradient-to-br from-slate-700 to-slate-800 border border-slate-600 flex items-center justify-center text-cyan-300 text-xs font-bold font-mono shadow-sm">
            OP
          </div>
          <div className="hidden md:block text-left">
            <div className="text-[11px] font-bold text-slate-200 leading-tight">Fraud Lead</div>
            <div className="text-[9px] text-cyan-400 font-mono uppercase tracking-wider">Station 04 · A1</div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
