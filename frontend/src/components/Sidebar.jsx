import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Network, Bot, Zap, Activity } from 'lucide-react';

export function Sidebar() {
  const navItems = [
    { to: '/', label: 'Investigation Dashboard', icon: LayoutDashboard, exact: true },
    { to: '/customers', label: 'Suspicious Customers', icon: Users },
    { to: '/fraud-rings', label: 'Fraud Rings & Syndicates', icon: Network },
    { to: '/agents', label: 'Agent Investigation', icon: Bot },
    { to: '/simulation', label: 'Live Risk Simulator', icon: Zap },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-[#0B0F19] p-4 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div className="space-y-1">
          <p className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2">
            Forensic Intelligence
          </p>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.exact}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80'
                  }`
                }
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </div>

        {/* Phase Architecture Status */}
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between text-xs font-bold text-slate-300">
            <span className="flex items-center gap-1.5 text-cyan-400">
              <Activity size={14} />
              Pipeline Matrix
            </span>
            <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-500/20 font-mono">
              Phases 1-6
            </span>
          </div>
          <div className="space-y-1 text-[11px] text-slate-400">
            <div className="flex justify-between items-center py-0.5">
              <span>Phase 1 Dataset</span>
              <span className="text-emerald-400 font-mono font-medium">10k Txns</span>
            </div>
            <div className="flex justify-between items-center py-0.5">
              <span>Phase 2 Graph</span>
              <span className="text-emerald-400 font-mono font-medium">14.1k Nodes</span>
            </div>
            <div className="flex justify-between items-center py-0.5">
              <span>Phase 3 ML Scorer</span>
              <span className="text-emerald-400 font-mono font-medium">99.8% AUC</span>
            </div>
            <div className="flex justify-between items-center py-0.5">
              <span>Phase 4 Explainability</span>
              <span className="text-emerald-400 font-mono font-medium">Deterministic</span>
            </div>
            <div className="flex justify-between items-center py-0.5">
              <span>Phase 5 REST & UI</span>
              <span className="text-emerald-400 font-mono font-medium">FastAPI + React</span>
            </div>
            <div className="flex justify-between items-center py-0.5">
              <span>Phase 6 Multi-Agent</span>
              <span className="text-emerald-400 font-mono font-medium">6 Agents + Sim</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="pt-4 border-t border-slate-800/80 text-[11px] text-slate-400 space-y-1">
        <p className="font-semibold text-slate-300">FraudGraph Hackathon Edition</p>
        <p>Built with FastAPI & Cytoscape.js</p>
      </div>
    </aside>
  );
}

export default Sidebar;
