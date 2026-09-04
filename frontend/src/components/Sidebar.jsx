import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Network,
  Bot,
  Zap,
  Activity,
  Server,
  ChevronLeft,
  ChevronRight,
  Cpu,
  ShieldAlert,
  GitBranch,
  Radio,
  CheckCircle2,
} from 'lucide-react';

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    {
      to: '/',
      label: 'Investigation Dashboard',
      shortLabel: 'Dashboard',
      icon: LayoutDashboard,
      exact: true,
      badge: null,
      pulseColor: 'bg-cyan-400',
    },
    {
      to: '/customers',
      label: 'Suspicious Customers',
      shortLabel: 'Customers',
      icon: Users,
      badge: { text: '24', color: 'bg-red-500/20 text-red-400 border border-red-500/40' },
      pulseColor: 'bg-red-500',
    },
    {
      to: '/fraud-rings',
      label: 'Fraud Rings & Syndicates',
      shortLabel: 'Syndicates',
      icon: Network,
      badge: { text: '26', color: 'bg-purple-500/20 text-purple-400 border border-purple-500/40' },
      pulseColor: 'bg-purple-400',
    },
    {
      to: '/agents',
      label: 'Agent Investigation',
      shortLabel: 'Agents',
      icon: Bot,
      badge: { text: '6 Active', color: 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40' },
      pulseColor: 'bg-cyan-400',
    },
    {
      to: '/simulation',
      label: 'Live Risk Simulator',
      shortLabel: 'Simulator',
      icon: Zap,
      badge: { text: 'LIVE', color: 'bg-amber-500/20 text-amber-400 border border-amber-500/40 animate-pulse' },
      pulseColor: 'bg-amber-400',
    },
  ];

  const pipelinePhases = [
    { id: 'L1', name: 'Ingress Stream', metric: '10k Txns', status: 'ONLINE', pct: 100, color: '#06B6D4' },
    { id: 'L2', name: 'Graph Topology', metric: '14.1k Nodes', status: 'SYNCED', pct: 100, color: '#8B5CF6' },
    { id: 'L3', name: 'Risk ML Scorer', metric: '99.8% AUC', status: 'ONLINE', pct: 99.8, color: '#10B981' },
    { id: 'L4', name: 'XAI Attribution', metric: 'Resolved', status: 'ACTIVE', pct: 96, color: '#06B6D4' },
    { id: 'L5', name: 'REST Gateway', metric: 'FastAPI', status: 'HEALTHY', pct: 100, color: '#94A3B8' },
    { id: 'L6', name: 'Agent Consensus', metric: '6 Swarm', status: 'CONSENSUS', pct: 100, color: '#F59E0B' },
  ];

  return (
    <aside
      className={`border-r border-soc-border bg-[#090D16] flex flex-col justify-between hidden md:flex min-h-[calc(100vh-3.5rem)] select-none transition-all duration-300 ease-in-out z-40 ${
        collapsed ? 'w-16 p-2' : 'w-64 p-3'
      }`}
    >
      <div className="space-y-4">
        {/* Header / Collapse Toggle */}
        <div className="flex items-center justify-between px-1 py-1">
          {!collapsed && (
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-soc-pulse"></span>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                INTELLIGENCE CONSOLE
              </p>
            </div>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1 rounded bg-soc-surface border border-soc-border text-slate-400 hover:text-slate-200 hover:border-slate-600 transition-colors mx-auto"
            title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.exact}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded text-xs font-semibold transition-all relative group ${
                    isActive
                      ? 'bg-soc-surface border-l-2 border-cyan-400 text-cyan-300 shadow-[inset_0_0_12px_rgba(6,182,212,0.1)]'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-soc-surface/60 border-l-2 border-transparent'
                  } ${collapsed ? 'justify-center px-0' : ''}`
                }
              >
                <div className="relative">
                  <Icon size={16} className="flex-shrink-0" />
                  {item.pulseColor && (
                    <span className={`absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full ${item.pulseColor} opacity-70`} />
                  )}
                </div>
                {!collapsed && (
                  <>
                    <span className="truncate flex-1">{item.label}</span>
                    {item.badge && (
                      <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${item.badge.color}`}>
                        {item.badge.text}
                      </span>
                    )}
                  </>
                )}

                {/* Collapsed Hover Tooltip */}
                {collapsed && (
                  <div className="absolute left-full ml-2 px-2.5 py-1 bg-[#0D131F] border border-soc-border text-slate-200 text-xs font-mono rounded shadow-xl whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-opacity z-50 flex items-center gap-2">
                    <span>{item.shortLabel}</span>
                    {item.badge && (
                      <span className={`text-[8px] font-bold px-1 py-0.2 rounded ${item.badge.color}`}>
                        {item.badge.text}
                      </span>
                    )}
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* System Status: Visual Pipeline Matrix (Circuit Timeline) */}
        {!collapsed ? (
          <div className="space-y-3 pt-2">
            <div className="p-3 rounded bg-soc-panel border border-soc-border space-y-2.5">
              <div className="flex items-center justify-between pb-1.5 border-b border-soc-border/80">
                <span className="flex items-center gap-1.5 text-xs font-bold text-slate-200 font-mono">
                  <Activity size={13} className="text-cyan-400" />
                  PIPELINE MATRIX
                </span>
                <span className="flex items-center gap-1 text-[9px] text-emerald-400 font-mono font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-soc-pulse"></span>
                  L1→L6 ACTIVE
                </span>
              </div>

              {/* Connected Sequential Circuit Phases */}
              <div className="space-y-2 relative font-mono text-[10px]">
                {pipelinePhases.map((phase, idx) => (
                  <div key={phase.id} className="space-y-1">
                    <div className="flex justify-between items-center text-slate-400">
                      <div className="flex items-center gap-1.5">
                        <span
                          className="w-4 h-4 rounded text-[8px] font-bold flex items-center justify-center text-slate-950"
                          style={{ backgroundColor: phase.color }}
                        >
                          {phase.id}
                        </span>
                        <span className="text-slate-300 font-semibold">{phase.name}</span>
                      </div>
                      <span className="text-slate-400 font-normal">{phase.metric}</span>
                    </div>
                    {/* Visual Progress Bar */}
                    <div className="w-full bg-[#080B11] rounded h-1 overflow-hidden border border-soc-border/40">
                      <div
                        className="h-full rounded transition-all duration-300"
                        style={{ backgroundColor: phase.color, width: `${phase.pct}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Metrics Strip */}
            <div className="p-2.5 rounded bg-soc-surface/60 border border-soc-border text-[9px] font-mono text-slate-400 flex items-center justify-between">
              <span>Louvain: <strong className="text-purple-400">0.812</strong></span>
              <span>IF Contam: <strong className="text-amber-400">2.0%</strong></span>
            </div>
          </div>
        ) : (
          /* Collapsed Rail Status Nodes */
          <div className="pt-2 flex flex-col items-center gap-2">
            <div
              className="w-8 h-8 rounded bg-soc-surface border border-soc-border flex items-center justify-center text-emerald-400 group relative cursor-pointer hover:border-emerald-400 transition-colors"
              title="Pipeline: L1-L6 ACTIVE"
            >
              <Activity size={14} className="animate-soc-pulse" />
              <div className="absolute left-full ml-2 px-2 py-1 bg-[#0D131F] border border-soc-border text-slate-200 text-[10px] font-mono rounded shadow-xl whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50">
                Pipeline: L1-L6 ACTIVE · 99.8% Precision
              </div>
            </div>
            <div
              className="w-8 h-8 rounded bg-soc-surface border border-soc-border flex items-center justify-center text-purple-400 group relative cursor-pointer hover:border-purple-400 transition-colors"
              title="Graph: 14.1k Nodes"
            >
              <Network size={14} />
              <div className="absolute left-full ml-2 px-2 py-1 bg-[#0D131F] border border-soc-border text-slate-200 text-[10px] font-mono rounded shadow-xl whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50">
                Graph: 14,124 Nodes · 26 Rings
              </div>
            </div>
            <div
              className="w-8 h-8 rounded bg-soc-surface border border-soc-border flex items-center justify-center text-cyan-400 group relative cursor-pointer hover:border-cyan-400 transition-colors"
              title="Agents: 6 Active"
            >
              <Bot size={14} />
              <div className="absolute left-full ml-2 px-2 py-1 bg-[#0D131F] border border-soc-border text-slate-200 text-[10px] font-mono rounded shadow-xl whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50">
                6 Autonomous Agents Ready
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer System Status */}
      <div className="pt-3 border-t border-soc-border text-[10px] font-mono text-slate-400">
        {!collapsed ? (
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-slate-300 font-bold">FRAUDGRAPH</span>
              <span className="text-emerald-400 font-bold">v1.2 SOC</span>
            </div>
            <p className="text-[9px] text-slate-400">Financial Crime Intel Platform</p>
          </div>
        ) : (
          <div className="text-center text-[9px] font-bold text-cyan-400">v1.2</div>
        )}
      </div>
    </aside>
  );
}

export default Sidebar;
