import React, { useEffect, useState, useMemo } from 'react';
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
  Zap,
  CheckCircle2,
  Filter,
  Activity,
  Server,
  ShieldCheck,
  Eye,
  Radar,
  Radio,
  Clock,
  ArrowRight,
  Database,
  GitBranch,
  Bot,
  Binary,
  Maximize2,
  Terminal,
  ChevronDown,
  ArrowUpDown,
  SlidersHorizontal,
  Info,
  ExternalLink,
  Target,
} from 'lucide-react';
import apiService from '../services/api';
import RiskBadge from '../components/RiskBadge';
import CytoscapeGraph from '../components/CytoscapeGraph';
import IntelligenceDrawer from '../components/IntelligenceDrawer';

export function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [customersData, setCustomersData] = useState(null);
  const [ringsData, setRingsData] = useState(null);
  const [networkGraph, setNetworkGraph] = useState(null);
  const [selectedRingId, setSelectedRingId] = useState('FR_017');
  const [loading, setLoading] = useState(true);
  const [graphLoading, setGraphLoading] = useState(false);
  const [error, setError] = useState(null);

  // Threat Queue Sorting & Filtering
  const [activeQueueFilter, setActiveQueueFilter] = useState('ALL');
  const [queueSortBy, setQueueSortBy] = useState('risk_score'); // 'risk_score' | 'spend' | 'customer_id'
  const [queueSortOrder, setQueueSortOrder] = useState('desc');

  // Interactive Pipeline Hover Tooltip State
  const [hoveredStage, setHoveredStage] = useState(null);

  // Intelligence Drawer State
  const [drawerEntity, setDrawerEntity] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // Live Activity Feed simulated timestamp ticks
  const [feedTimestamp, setFeedTimestamp] = useState(new Date().toLocaleTimeString());

  const navigate = useNavigate();

  // Load initial dashboard statistics, customer records, and top fraud rings
  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const [statsRes, custRes, ringsRes] = await Promise.all([
          apiService.getDashboard(),
          apiService.getCustomers({ page: 1, pageSize: 24 }),
          apiService.getFraudRings({ page: 1, pageSize: 8 }),
        ]);
        setStats(statsRes);
        setCustomersData(custRes);
        setRingsData(ringsRes);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  // Hydrate syndicate network graph when selectedRingId changes
  useEffect(() => {
    async function loadRingNetwork() {
      if (!selectedRingId) return;
      try {
        setGraphLoading(true);
        const netRes = await apiService.getNetwork('ring', selectedRingId);
        setNetworkGraph(netRes);
      } catch (err) {
        console.error('Failed to load network graph for', selectedRingId, err);
      } finally {
        setGraphLoading(false);
      }
    }
    loadRingNetwork();
  }, [selectedRingId]);

  // Periodic simulated live pulse
  useEffect(() => {
    const timer = setInterval(() => {
      setFeedTimestamp(new Date().toLocaleTimeString());
    }, 8000);
    return () => clearInterval(timer);
  }, []);

  // Handler to open Intelligence Drawer for any entity
  const handleOpenDrawer = (entity) => {
    setDrawerEntity(entity);
    setIsDrawerOpen(true);
  };

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-[75vh]">
        <div className="flex flex-col items-center gap-3 text-cyan-400 font-mono">
          <div className="w-10 h-10 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-400 tracking-wider">HYDRATING FORENSIC SOC ENVIRONMENT...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="soc-panel p-6 border-red-500/30 bg-red-950/20 text-center space-y-3 font-mono">
          <AlertTriangle className="mx-auto text-red-400" size={32} />
          <h3 className="text-sm font-bold text-red-300">Intelligence Engine Connection Failure</h3>
          <p className="text-xs text-slate-400">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-1.5 text-xs rounded bg-red-500/20 text-red-300 border border-red-500/40 hover:bg-red-500/30 font-semibold"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const dist = stats?.risk_distribution || { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
  const totalIndexed = dist.LOW + dist.MEDIUM + dist.HIGH + dist.CRITICAL || 2000;
  const criticalCount = stats?.critical_customers_count || 0;
  const highCount = stats?.high_risk_customers_count || 0;
  const highestCust = stats?.highest_risk_customer;
  const highestRing = stats?.highest_risk_ring;

  const activeRingObj = ringsData?.items?.find((r) => r.ring_id === selectedRingId) || ringsData?.items?.[0];

  // Processed and sorted active threat queue
  const filteredAndSortedQueue = (customersData?.items || [])
    .filter((c) => {
      if (activeQueueFilter === 'ALL') return true;
      return c.risk_level === activeQueueFilter;
    })
    .sort((a, b) => {
      let comparison = 0;
      if (queueSortBy === 'risk_score') {
        comparison = a.risk_score - b.risk_score;
      } else if (queueSortBy === 'spend') {
        comparison = a.total_spend - b.total_spend;
      } else if (queueSortBy === 'customer_id') {
        comparison = a.customer_id.localeCompare(b.customer_id);
      }
      return queueSortOrder === 'desc' ? -comparison : comparison;
    });

  // 6 Pipeline Stages with Interactive Popovers & Navigation
  const pipelineStages = [
    {
      id: 1,
      title: '10,000 TRANSACTIONS',
      sub: 'Ingress & Velocity Stream',
      color: 'cyan',
      tag: 'STREAM ACTIVE',
      metrics: '10,000 records indexed · 142 tx/s · ₹2.4Cr total volume',
      actionTitle: 'Launch Attack Simulator',
      onClick: () => navigate('/simulation'),
    },
    {
      id: 2,
      title: 'RISK ANALYSIS',
      sub: 'Random Forest 99.8% AUC',
      color: 'orange',
      tag: 'CALIBRATED',
      metrics: 'Isolation Forest 2.0% outlier contamination · 39 high/critical',
      actionTitle: 'Inspect Filtered Customers',
      onClick: () => navigate('/customers'),
    },
    {
      id: 3,
      title: 'GRAPH CORRELATION',
      sub: '14.1k Nodes · Louvain 0.812',
      color: 'purple',
      tag: 'PARTITIONED',
      metrics: '14,124 vertices · 28,490 edges · Multi-relational bipartite',
      actionTitle: 'Center on Fraud Graph',
      onClick: () => {
        document.getElementById('network-centerpiece')?.scrollIntoView({ behavior: 'smooth' });
      },
    },
    {
      id: 4,
      title: '26 FRAUD RINGS',
      sub: 'Isolated Syndicates',
      color: 'red',
      tag: '26 ISOLATED',
      metrics: '₹70.7L suspicious ring outflow · FR_017 largest (161 members)',
      actionTitle: 'Browse All Fraud Rings',
      onClick: () => navigate('/fraud-rings'),
    },
    {
      id: 5,
      title: '6 AI AGENTS',
      sub: 'Autonomous Swarm',
      color: 'cyan',
      tag: 'CONSENSUS',
      metrics: 'Transaction, Anomaly, Graph, Risk, XAI, Coordinator · 15ms latency',
      actionTitle: 'Open Agent Investigation',
      onClick: () => navigate('/agents'),
    },
    {
      id: 6,
      title: 'DISPOSITION ACTION',
      sub: 'Forensic Dossiers',
      color: 'emerald',
      tag: '24 PENDING',
      metrics: '24 critical alerts requiring immediate restriction & sign-off',
      actionTitle: 'Triage Critical Incidents',
      onClick: () => navigate('/customers?risk_level=CRITICAL'),
    },
  ];

  // Quantitative Attack Vectors
  const signalVectors = [
    { name: 'Shared Device Cluster', code: 'DEV_CLUSTER', prevalence: 38, pct: 38, severity: 'CRITICAL', color: '#EF4444' },
    { name: 'Shared Payment Instrument', code: 'PAY_INSTRUMENT', prevalence: 31, pct: 31, severity: 'CRITICAL', color: '#EF4444' },
    { name: 'Temporal Burst Velocity', code: 'BURST_SYNC', prevalence: 24, pct: 24, severity: 'HIGH', color: '#F97316' },
    { name: 'Proxy IP Relay Obfuscation', code: 'IP_PROXY', prevalence: 19, pct: 19, severity: 'HIGH', color: '#F97316' },
    { name: 'Abnormal Spend Outlier', code: 'SPEND_ANOMALY', prevalence: 14, pct: 14, severity: 'MEDIUM', color: '#F59E0B' },
  ];

  // 6-Agent Swarm Status with Progress & Findings
  const agentSwarm = [
    {
      name: 'Transaction Ingress Agent',
      role: 'Velocity & Ingress Telemetry',
      status: 'RUNNING',
      progress: 98,
      latency: '4ms',
      finding: 'Ingested 10,000 transactions without sequence drops',
      color: '#06B6D4',
    },
    {
      name: 'Isolation Forest Anomaly Agent',
      role: 'Feature Vector Outlier Detection',
      status: 'ACTIVE',
      progress: 95,
      latency: '12ms',
      finding: 'Detected 2.0% anomalous outlier density in spend velocity',
      color: '#F97316',
    },
    {
      name: 'Louvain Graph Agent',
      role: 'Topological Community Partitioning',
      status: 'SYNCED',
      progress: 100,
      latency: '18ms',
      finding: 'Resolved 26 dense syndicates with 0.812 modularity index',
      color: '#8B5CF6',
    },
    {
      name: 'Random Forest Risk Agent',
      role: 'Supervised Risk Calibration',
      status: 'ONLINE',
      progress: 99,
      latency: '9ms',
      finding: '99.8% precision score across 2,000 evaluated accounts',
      color: '#EF4444',
    },
    {
      name: 'XAI Attribution Agent',
      role: 'Deterministic Feature Provenance',
      status: 'READY',
      progress: 96,
      latency: '6ms',
      finding: 'Identified shared_device_cluster as primary risk driver',
      color: '#10B981',
    },
    {
      name: 'Investigation Coordinator',
      role: 'Multi-Agent Consensus & Adjudication',
      status: 'CONSENSUS',
      progress: 100,
      latency: '15ms',
      finding: 'Formulated 24 critical restriction recommendations',
      color: '#06B6D4',
    },
  ];

  return (
    <div className="space-y-4 pb-14 text-slate-100 font-sans select-none animate-in fade-in duration-300">
      {/* ============================================================
          INTERACTIVE PIPELINE FUNNEL (CORE ARCHITECTURAL TELEMETRY)
          Hoverable with rich popovers, clickable navigation triggers
          ============================================================ */}
      <div className="p-2.5 rounded-lg bg-[#0A0F1A] border border-soc-border font-mono text-[11px] overflow-x-auto relative shadow-inner">
        <div className="flex items-center justify-between min-w-[940px] gap-2">
          {pipelineStages.map((stg, idx) => (
            <React.Fragment key={stg.id}>
              {/* Stage Card */}
              <div
                onMouseEnter={() => setHoveredStage(stg.id)}
                onMouseLeave={() => setHoveredStage(null)}
                onClick={stg.onClick}
                className={`flex items-center gap-2.5 px-3 py-1.5 rounded-md cursor-pointer transition-all relative ${
                  hoveredStage === stg.id
                    ? 'bg-soc-surface border border-cyan-500/50 shadow-lg scale-[1.02]'
                    : 'hover:bg-soc-surface/60 border border-transparent'
                }`}
              >
                <div
                  className={`w-6 h-6 rounded flex items-center justify-center font-bold text-[10px] shadow-sm ${
                    stg.color === 'cyan'
                      ? 'bg-cyan-500/15 border border-cyan-500/40 text-cyan-400'
                      : stg.color === 'orange'
                      ? 'bg-orange-500/15 border border-orange-500/40 text-orange-400'
                      : stg.color === 'purple'
                      ? 'bg-purple-500/15 border border-purple-500/40 text-purple-400'
                      : stg.color === 'red'
                      ? 'bg-red-500/15 border border-red-500/40 text-red-400'
                      : 'bg-emerald-500/15 border border-emerald-500/40 text-emerald-400'
                  }`}
                >
                  {stg.id}
                </div>
                <div>
                  <div className="font-bold text-slate-200 text-[11px] flex items-center gap-1.5">
                    <span>{stg.title}</span>
                    <span className="text-[8px] px-1 py-0.2 rounded bg-[#0D131F] border border-soc-border text-slate-400">
                      {stg.tag}
                    </span>
                  </div>
                  <div className="text-[9px] text-slate-400 font-normal">{stg.sub}</div>
                </div>

                {/* Interactive Stage Popover */}
                {hoveredStage === stg.id && (
                  <div className="absolute top-full left-0 mt-2 w-72 bg-[#0D131F]/95 backdrop-blur-md border border-cyan-500/40 rounded p-2.5 text-xs font-mono shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-150 pointer-events-none">
                    <div className="flex items-center justify-between pb-1 border-b border-soc-border text-[9px] font-bold text-cyan-400 uppercase">
                      <span>STAGE {stg.id} TELEMETRY</span>
                      <span>CLICK TO DRILL-DOWN</span>
                    </div>
                    <p className="text-[11px] text-slate-300 font-sans mt-1 leading-relaxed">
                      {stg.metrics}
                    </p>
                    <div className="mt-2 pt-1 border-t border-soc-border/60 text-[10px] text-cyan-400 font-bold flex items-center justify-between">
                      <span>{stg.actionTitle}</span>
                      <ArrowRight size={11} />
                    </div>
                  </div>
                )}
              </div>

              {/* Arrow Divider */}
              {idx < pipelineStages.length - 1 && (
                <ArrowRight size={13} className="text-slate-400 flex-shrink-0" />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* ============================================================
          ROW 1 — COMMAND CENTER HERO AREA
          ============================================================ */}
      <div className="p-4 soc-panel relative overflow-hidden bg-gradient-to-r from-[#0D131F] via-[#0E1524] to-[#141C2B] border-soc-border shadow-lg">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-soc-pulse"></span>
              <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest font-mono">
                ENGINE ACTIVE · SOC L3 REAL-TIME DEFENSE
              </span>
            </div>
            <h1 className="text-xl md:text-2xl font-extrabold text-slate-100 tracking-tight font-sans">
              Fraud Intelligence Command Center
            </h1>
            <p className="text-xs text-slate-400 font-sans leading-relaxed">
              Surveillance correlating multi-entity graph topologies, Random Forest risk probabilities, Isolation Forest anomaly scoring, and 6-agent collaborative investigations.
            </p>
          </div>

          {/* Command Status Chips & Primary Actions */}
          <div className="flex flex-wrap items-center gap-2 font-mono">
            {/* Target 1 Chip with 1-Click Drawer Trigger */}
            <div
              onClick={() => handleOpenDrawer({
                id: highestCust?.entity_id || 'CUST_00028',
                type: 'customer',
                risk_score: 99.1,
                risk_level: 'CRITICAL',
                top_signal: 'shared_device_cluster',
                ring_id: 'FR_015',
                home_city: 'Mumbai',
                total_spend: 489200,
                transaction_count: 34,
              })}
              className="p-2 rounded bg-soc-surface border border-soc-border hover:border-red-500/50 cursor-pointer transition-colors text-left group"
              title="Click to open Forensic Drawer for CUST_00028"
            >
              <div className="text-[9px] uppercase font-bold text-slate-400 flex items-center justify-between gap-2">
                <span>Focus Target</span>
                <Eye size={11} className="text-slate-400 group-hover:text-red-400" />
              </div>
              <div className="text-xs font-bold text-red-400 flex items-center gap-1.5 mt-0.5">
                <span>{highestCust?.entity_id || 'CUST_00028'}</span>
                <span className="text-[9px] px-1 py-0.2 bg-red-500/20 text-red-300 rounded border border-red-500/40">99.1</span>
              </div>
            </div>

            <div className="p-2 rounded bg-soc-surface border border-soc-border text-left">
              <div className="text-[9px] uppercase font-bold text-slate-400">Critical Alerts</div>
              <div className="text-xs font-bold text-slate-100 mt-0.5">
                <span className="text-red-400 font-extrabold">{criticalCount}</span> / 39 High Risk
              </div>
            </div>

            <div className="p-2 rounded bg-soc-surface border border-soc-border text-left">
              <div className="text-[9px] uppercase font-bold text-slate-400">Active Syndicates</div>
              <div className="text-xs font-bold text-purple-400 mt-0.5">
                26 Detected Rings
              </div>
            </div>

            <div className="flex items-center gap-1.5 pl-2 border-l border-soc-border">
              <button
                onClick={() => navigate('/customers?risk_level=CRITICAL')}
                className="px-3 py-2 text-xs font-bold rounded bg-red-600 hover:bg-red-500 text-white transition-all flex items-center gap-1.5 shadow-sm active:scale-95"
              >
                <ShieldAlert size={14} />
                <span>Critical Alerts ({criticalCount})</span>
              </button>
              <button
                onClick={() => navigate('/fraud-rings')}
                className="px-3 py-2 text-xs font-bold rounded bg-purple-600 hover:bg-purple-500 text-white transition-all flex items-center gap-1.5 shadow-sm active:scale-95"
              >
                <Network size={14} />
                <span>Syndicates (26)</span>
              </button>
              <button
                onClick={() => navigate('/simulation')}
                className="px-3 py-2 text-xs font-bold rounded bg-amber-500 hover:bg-amber-400 text-slate-950 transition-all flex items-center gap-1.5 shadow-sm active:scale-95"
              >
                <Zap size={14} className="fill-current" />
                <span>Live Simulator</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ============================================================
          RICH INTERACTIVE KPI WIDGETS ROW
          Sparkline progress bars, trend metrics, interactive navigation
          ============================================================ */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* KPI 1: Monitored Customers */}
        <div
          onClick={() => navigate('/customers')}
          className="soc-interactive-card p-3.5 space-y-2 cursor-pointer group relative overflow-hidden"
        >
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 text-[11px] uppercase font-bold">Monitored Accounts</span>
            <Users size={15} className="text-cyan-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="flex items-baseline justify-between font-mono">
            <span className="text-2xl font-black text-slate-100">{totalIndexed.toLocaleString()}</span>
            <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
              100% COVERAGE
            </span>
          </div>
          {/* Mini Distribution Sparkline Bar */}
          <div className="w-full bg-[#080B11] h-1.5 rounded-full overflow-hidden flex border border-soc-border">
            <div style={{ width: `${(dist.LOW / totalIndexed) * 100}%` }} className="h-full bg-emerald-500" title="Low Risk" />
            <div style={{ width: `${(dist.MEDIUM / totalIndexed) * 100}%` }} className="h-full bg-amber-500" title="Medium Risk" />
            <div style={{ width: `${(dist.HIGH / totalIndexed) * 100}%` }} className="h-full bg-orange-500" title="High Risk" />
            <div style={{ width: `${(dist.CRITICAL / totalIndexed) * 100}%` }} className="h-full bg-red-500" title="Critical Risk" />
          </div>
          <div className="text-[9px] text-slate-400 font-mono flex justify-between">
            <span>10,000 txns indexed</span>
            <span className="text-cyan-400 group-hover:underline flex items-center gap-0.5">
              Directory <ArrowUpRight size={10} />
            </span>
          </div>
        </div>

        {/* KPI 2: High & Critical Entities */}
        <div
          onClick={() => navigate('/customers?risk_level=CRITICAL')}
          className="soc-interactive-card soc-interactive-card-critical p-3.5 space-y-2 cursor-pointer group relative overflow-hidden"
        >
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 text-[11px] uppercase font-bold">High & Critical Threats</span>
            <ShieldAlert size={15} className="text-red-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="flex items-baseline justify-between font-mono">
            <span className="text-2xl font-black text-red-400">{criticalCount + highCount}</span>
            <span className="text-[10px] text-red-400 font-bold bg-red-500/10 px-1.5 py-0.5 rounded border border-red-500/30">
              {criticalCount} CRITICAL
            </span>
          </div>
          {/* Pulsing Critical Outflow Meter */}
          <div className="w-full bg-[#080B11] h-1.5 rounded-full overflow-hidden border border-soc-border">
            <div
              style={{ width: `${((criticalCount + highCount) / totalIndexed) * 100 * 20}%` }}
              className="h-full bg-red-500 rounded-full"
            />
          </div>
          <div className="text-[9px] text-slate-400 font-mono flex justify-between">
            <span>24 Critical · 15 High</span>
            <span className="text-red-400 group-hover:underline flex items-center gap-0.5">
              Triage <ArrowUpRight size={10} />
            </span>
          </div>
        </div>

        {/* KPI 3: Detected Fraud Rings */}
        <div
          onClick={() => navigate('/fraud-rings')}
          className="soc-interactive-card soc-interactive-card-purple p-3.5 space-y-2 cursor-pointer group relative overflow-hidden"
        >
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 text-[11px] uppercase font-bold">Detected Syndicates</span>
            <Network size={15} className="text-purple-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="flex items-baseline justify-between font-mono">
            <span className="text-2xl font-black text-purple-400">26</span>
            <span className="text-[10px] text-purple-400 font-bold bg-purple-500/10 px-1.5 py-0.5 rounded border border-purple-500/30">
              MODULARITY 0.812
            </span>
          </div>
          {/* Louvain Cohesion Gauge */}
          <div className="w-full bg-[#080B11] h-1.5 rounded-full overflow-hidden border border-soc-border">
            <div style={{ width: '81.2%' }} className="h-full bg-purple-500 rounded-full" />
          </div>
          <div className="text-[9px] text-slate-400 font-mono flex justify-between">
            <span>Largest: FR_017 (161 Accts)</span>
            <span className="text-purple-400 group-hover:underline flex items-center gap-0.5">
              Syndicates <ArrowUpRight size={10} />
            </span>
          </div>
        </div>

        {/* KPI 4: Suspicious Volume Exposure */}
        <div
          onClick={() => navigate('/customers?risk_level=CRITICAL')}
          className="soc-interactive-card p-3.5 space-y-2 cursor-pointer group relative overflow-hidden"
        >
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 text-[11px] uppercase font-bold">Suspicious Volume</span>
            <IndianRupee size={15} className="text-amber-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="flex items-baseline justify-between font-mono">
            <span className="text-2xl font-black text-slate-100">₹70.7L</span>
            <span className="text-[10px] text-amber-400 font-bold bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/30">
              29.5% OUTFLOW
            </span>
          </div>
          {/* Exposure Ratio Bar */}
          <div className="w-full bg-[#080B11] h-1.5 rounded-full overflow-hidden border border-soc-border">
            <div style={{ width: '29.5%' }} className="h-full bg-amber-500 rounded-full" />
          </div>
          <div className="text-[9px] text-slate-400 font-mono flex justify-between">
            <span>Total Indexed: ~₹2.4Cr</span>
            <span className="text-amber-400 group-hover:underline flex items-center gap-0.5">
              Exposure <ArrowUpRight size={10} />
            </span>
          </div>
        </div>
      </div>

      {/* ============================================================
          ROW 2 — OPERATIONAL OVERVIEW
          Asymmetric Layout: LEFT ~65% Fraud Activity Overview | RIGHT ~35% Risk Snapshot
          ============================================================ */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3.5">
        {/* LEFT ~65%: Fraud Activity Overview (Visual Transaction & Attack Signal Matrix) */}
        <div className="lg:col-span-8 soc-panel p-4 space-y-3.5">
          <div className="flex items-center justify-between pb-2 border-b border-soc-border">
            <div className="flex items-center gap-2">
              <Activity size={16} className="text-cyan-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
                FRAUD ACTIVITY OVERVIEW · TRANSACTION & ATTACK SIGNAL ATTRIBUTION
              </h3>
            </div>
            <span className="text-[10px] text-slate-400 font-mono">10,000 Ingested Records</span>
          </div>

          {/* Volume Exposure Breakdown Bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="text-slate-300 text-[11px] font-semibold">Transaction Volume Exposure by Risk Tier</span>
              <div className="flex items-center gap-3 text-[10px]">
                <span className="text-red-400 font-bold">₹70.7L Suspicious Ring Outflow</span>
                <span className="text-slate-400">Total Indexed Volume: ~₹2.4Cr</span>
              </div>
            </div>

            {/* Stacked Multi-Segment Visual Bar */}
            <div className="w-full h-3 rounded bg-[#080B11] overflow-hidden flex border border-soc-border">
              <div style={{ width: '29.5%' }} className="h-full bg-red-500 hover:opacity-90 transition-opacity cursor-pointer" title="Critical Syndicate Spend: ₹70.7L (29.5%)" />
              <div style={{ width: '8.9%' }} className="h-full bg-orange-500 hover:opacity-90 transition-opacity cursor-pointer" title="High Risk Spend: ₹21.4L (8.9%)" />
              <div style={{ width: '35.1%' }} className="h-full bg-amber-500 hover:opacity-90 transition-opacity cursor-pointer" title="Medium Tier Spend: ₹84.2L (35.1%)" />
              <div style={{ width: '26.5%' }} className="h-full bg-emerald-500 hover:opacity-90 transition-opacity cursor-pointer" title="Low / Baseline Spend: ₹63.7L (26.5%)" />
            </div>

            <div className="flex flex-wrap items-center justify-between text-[9px] font-mono text-slate-400 pt-0.5">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-red-500" />
                <span>Critical: ₹70.7L (29.5%)</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-orange-500" />
                <span>High: ₹21.4L (8.9%)</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                <span>Medium: ₹84.2L (35.1%)</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                <span>Low: ₹63.7L (26.5%)</span>
              </span>
            </div>
          </div>

          {/* Primary Attack Vector Signal Distribution */}
          <div className="pt-2 border-t border-soc-border/70 space-y-2">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
              Identified Fraud Vectors · Relative Attack Frequency
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 font-mono">
              {signalVectors.map((sig) => (
                <div key={sig.code} className="p-2 bg-soc-surface border border-soc-border rounded space-y-1 hover:border-slate-600 transition-colors">
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="font-bold text-slate-200">{sig.code}</span>
                    <span style={{ color: sig.color }} className="font-extrabold">{sig.prevalence}%</span>
                  </div>
                  <div className="w-full bg-[#080B11] rounded h-1 overflow-hidden border border-soc-border/50">
                    <div className="h-full rounded" style={{ backgroundColor: sig.color, width: `${sig.pct}%` }} />
                  </div>
                  <div className="text-[8px] text-slate-400 truncate leading-tight">{sig.name}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT ~35%: Risk Snapshot (Compact Severity Distribution & Cutoff Thresholds) */}
        <div className="lg:col-span-4 soc-panel p-4 space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-2 border-b border-soc-border">
              <div className="flex items-center gap-1.5">
                <Radar size={15} className="text-red-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
                  RISK SNAPSHOT
                </h3>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">{totalIndexed.toLocaleString()} Accounts</span>
            </div>

            {/* Severity Distribution List */}
            <div className="space-y-2 pt-1.5">
              {[
                { level: 'CRITICAL', count: dist.CRITICAL, color: '#EF4444', pct: (dist.CRITICAL / totalIndexed) * 100, cutoff: '≥ 80.0' },
                { level: 'HIGH', count: dist.HIGH, color: '#F97316', pct: (dist.HIGH / totalIndexed) * 100, cutoff: '60.0 – 79.9' },
                { level: 'MEDIUM', count: dist.MEDIUM, color: '#F59E0B', pct: (dist.MEDIUM / totalIndexed) * 100, cutoff: '35.0 – 59.9' },
                { level: 'LOW', count: dist.LOW, color: '#10B981', pct: (dist.LOW / totalIndexed) * 100, cutoff: '< 35.0' },
              ].map((tier) => (
                <div key={tier.level} className="space-y-0.5">
                  <div className="flex justify-between items-center text-xs font-mono">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: tier.color }} />
                      <span className="font-bold text-slate-200 text-[11px]">{tier.level}</span>
                      <span className="text-[9px] text-slate-400 font-normal">({tier.cutoff})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-100">{tier.count}</span>
                      <span className="text-[10px] text-slate-400 font-normal">({tier.pct.toFixed(1)}%)</span>
                    </div>
                  </div>
                  <div className="w-full bg-[#080B11] rounded h-1.5 overflow-hidden border border-soc-border/60">
                    <div
                      className="h-full rounded transition-all duration-500"
                      style={{ backgroundColor: tier.color, width: `${Math.max(1.5, tier.pct)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-2 border-t border-soc-border/80 text-[10px] font-mono text-slate-400 flex justify-between items-center">
            <span>High/Critical Entities: <strong className="text-red-400">{criticalCount + highCount}</strong></span>
            <span className="text-cyan-400">99.8% ML Precision</span>
          </div>
        </div>
      </div>

      {/* ============================================================
          ROW 3 — FRAUD NETWORK INTELLIGENCE (VISUAL CENTERPIECE)
          ============================================================ */}
      <div id="network-centerpiece" className="soc-panel p-4 space-y-3.5 border-purple-500/30 bg-gradient-to-br from-[#0D131F] via-[#0E1524] to-[#151028] shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-purple-900/40">
          <div className="flex items-center gap-2">
            <Network size={18} className="text-purple-400" />
            <div>
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-100 font-mono">
                FRAUD NETWORK INTELLIGENCE · SYNDICATE TOPOLOGY
              </h2>
              <p className="text-[10px] text-slate-400 font-mono">
                Correlating Customers, Shared Devices, Proxy IPs, Payment VPAs, and Louvain Community Clusters
              </p>
            </div>
          </div>

          {/* Interactive Syndicate Ring Selector */}
          <div className="flex items-center gap-1 font-mono text-[10px]">
            <span className="text-slate-400 mr-1 hidden sm:inline">Active Syndicate:</span>
            {ringsData?.items?.slice(0, 6).map((r) => (
              <button
                key={r.ring_id}
                onClick={() => setSelectedRingId(r.ring_id)}
                className={`px-2 py-1 rounded border transition-colors ${
                  selectedRingId === r.ring_id
                    ? 'bg-purple-600 text-white border-purple-400 font-bold shadow-sm'
                    : 'bg-soc-surface border-soc-border text-slate-300 hover:text-white'
                }`}
              >
                {r.ring_id} ({r.customer_count})
              </button>
            ))}
          </div>
        </div>

        {/* Network Layout: Left Graph Canvas | Right Active Ring Dossier */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-3.5">
          {/* Main Cytoscape Graph Canvas with Interactive Drawer Callback */}
          <div className="lg:col-span-9 rounded overflow-hidden border border-soc-border bg-[#080B11]">
            {graphLoading ? (
              <div className="h-[480px] flex items-center justify-center text-purple-400 font-mono">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-8 h-8 border-2 border-purple-400 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-xs text-slate-400">Hydrating {selectedRingId} Relational Graph...</span>
                </div>
              </div>
            ) : networkGraph ? (
              <CytoscapeGraph
                graphData={networkGraph}
                height="480px"
                title={`Syndicate Relational Topology (${selectedRingId})`}
                onNodeSelect={(node) => handleOpenDrawer(node)}
              />
            ) : (
              <div className="h-[480px] flex items-center justify-center text-slate-400 text-xs font-mono">
                No graph payload available for {selectedRingId}.
              </div>
            )}
          </div>

          {/* Active Ring Telemetry Panel */}
          <div className="lg:col-span-3 soc-panel p-3.5 space-y-3 flex flex-col justify-between border-purple-500/25 bg-[#0C1220]">
            <div className="space-y-2.5">
              <div className="flex items-center justify-between pb-1.5 border-b border-soc-border">
                <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400 font-mono">
                  ACTIVE SYNDICATE PROFILE
                </span>
                <RiskBadge
                  level={activeRingObj?.risk_level || 'CRITICAL'}
                  score={activeRingObj?.risk_score || 100.0}
                  size="sm"
                />
              </div>

              <div>
                <div className="text-xl font-bold font-mono text-slate-100">{selectedRingId}</div>
                <div className="text-xs text-purple-300 font-mono font-bold mt-0.5">
                  {activeRingObj?.customer_count || 161} Member Accounts
                </div>
              </div>

              {/* Infrastructure metrics */}
              <div className="space-y-1.5 font-mono text-xs pt-1">
                <div className="p-2 bg-soc-surface border border-soc-border rounded flex justify-between items-center">
                  <span className="text-[10px] text-slate-400">Suspicious Volume</span>
                  <span className="font-bold text-slate-100">₹{((activeRingObj?.transaction_volume || 4245171) / 100000).toFixed(1)}L</span>
                </div>
                <div className="p-2 bg-soc-surface border border-soc-border rounded flex justify-between items-center">
                  <span className="text-[10px] text-slate-400">Shared Hardware</span>
                  <span className="font-bold text-blue-400">{activeRingObj?.shared_devices_count || 45} Devices</span>
                </div>
                <div className="p-2 bg-soc-surface border border-soc-border rounded flex justify-between items-center">
                  <span className="text-[10px] text-slate-400">Shared Instruments</span>
                  <span className="font-bold text-amber-400">{activeRingObj?.shared_payments_count || 41} VPAs/Cards</span>
                </div>
                <div className="p-2 bg-soc-surface border border-soc-border rounded flex justify-between items-center">
                  <span className="text-[10px] text-slate-400">Proxy IP Relay</span>
                  <span className="font-bold text-purple-400">{activeRingObj?.shared_ips_count || 30} IPs</span>
                </div>
              </div>
            </div>

            <div className="space-y-1.5 pt-2 border-t border-soc-border/60">
              <button
                onClick={() => handleOpenDrawer({
                  id: selectedRingId,
                  type: 'ring',
                  risk_score: activeRingObj?.risk_score || 100.0,
                  risk_level: activeRingObj?.risk_level || 'CRITICAL',
                  customer_count: activeRingObj?.customer_count || 161,
                  transaction_volume: activeRingObj?.transaction_volume || 4245171,
                  shared_devices_count: activeRingObj?.shared_devices_count || 45,
                  shared_payments_count: activeRingObj?.shared_payments_count || 41,
                  shared_ips_count: activeRingObj?.shared_ips_count || 30,
                  detail: `${activeRingObj?.customer_count || 161} member accounts funneled through 45 shared devices`,
                })}
                className="w-full py-2 px-3 text-xs font-mono font-bold rounded bg-soc-surface border border-purple-500/40 hover:bg-purple-950/30 text-purple-300 transition-colors flex items-center justify-center gap-1.5"
              >
                <span>Inspect in Drawer</span>
                <Eye size={13} />
              </button>

              <Link
                to={`/fraud-rings/${selectedRingId}`}
                className="w-full py-2 px-3 text-xs font-mono font-bold rounded bg-purple-600 hover:bg-purple-500 text-white transition-colors flex items-center justify-center gap-1.5 shadow-sm"
              >
                <span>Inspect Full Topology</span>
                <ArrowUpRight size={14} />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* ============================================================
          ROW 4 — INVESTIGATION WORKBENCH (3 CONSOLES)
          1. Active Threat Queue (Table with sort & drawer)
          2. Live Investigation Feed
          3. AI / Agent Operations Status
          ============================================================ */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3.5">
        {/* AREA 1 (5 Cols): Active Threat Queue (Interactive Triage Table) */}
        <div className="lg:col-span-5 soc-panel p-3.5 space-y-2.5">
          <div className="flex items-center justify-between pb-2 border-b border-soc-border">
            <div className="flex items-center gap-1.5">
              <ShieldAlert size={15} className="text-red-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-100 font-mono">
                ACTIVE THREAT QUEUE
              </h3>
            </div>
            {/* Filter Pills & Sorting */}
            <div className="flex items-center gap-1 font-mono text-[9px]">
              {['ALL', 'CRITICAL', 'HIGH'].map((f) => (
                <button
                  key={f}
                  onClick={() => setActiveQueueFilter(f)}
                  className={`px-1.5 py-0.5 rounded border transition-colors ${
                    activeQueueFilter === f
                      ? 'bg-red-500/20 text-red-300 border-red-500/40 font-bold'
                      : 'bg-soc-surface border-soc-border text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {f}
                </button>
              ))}
              <button
                onClick={() => setQueueSortOrder(queueSortOrder === 'desc' ? 'asc' : 'desc')}
                className="p-1 rounded bg-soc-surface border border-soc-border text-slate-400 hover:text-slate-200 ml-1"
                title={`Sort Order: ${queueSortOrder.toUpperCase()}`}
              >
                <ArrowUpDown size={11} />
              </button>
            </div>
          </div>

          {/* Interactive Queue Table */}
          <div className="overflow-x-auto max-h-[320px] overflow-y-auto">
            <table className="w-full text-left border-collapse text-xs font-mono">
              <thead className="sticky top-0 bg-[#0D131F] border-b border-soc-border text-[9px] font-bold text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="py-1.5 px-2">Customer</th>
                  <th className="py-1.5 px-2">Risk</th>
                  <th className="py-1.5 px-2">Signal</th>
                  <th className="py-1.5 px-2">Ring</th>
                  <th className="py-1.5 px-2 text-right">Triage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-soc-border/60 text-[11px]">
                {filteredAndSortedQueue.slice(0, 8).map((cust) => (
                  <tr
                    key={cust.customer_id}
                    onClick={() => handleOpenDrawer(cust)}
                    className="hover:bg-soc-surface-hover cursor-pointer transition-colors group"
                  >
                    <td className="py-2 px-2 font-bold text-cyan-400 group-hover:text-cyan-300 flex items-center gap-1">
                      <span>{cust.customer_id}</span>
                      <Eye size={10} className="opacity-0 group-hover:opacity-100 transition-opacity text-slate-400" />
                    </td>
                    <td className="py-2 px-2">
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                        cust.risk_level === 'CRITICAL' ? 'text-red-400 bg-red-500/10' : 'text-orange-400 bg-orange-500/10'
                      }`}>
                        {cust.risk_score.toFixed(1)}
                      </span>
                    </td>
                    <td className="py-2 px-2 text-slate-300 truncate max-w-[110px] text-[10px]">
                      {cust.top_signal.replace(/_/g, ' ')}
                    </td>
                    <td className="py-2 px-2">
                      {cust.ring_id ? (
                        <span className="text-purple-400 text-[10px] font-bold">{cust.ring_id}</span>
                      ) : (
                        <span className="text-slate-400 text-[10px]">Isolated</span>
                      )}
                    </td>
                    <td className="py-2 px-2 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/customers/${cust.customer_id}`);
                        }}
                        className="p-1 rounded hover:bg-cyan-500/20 text-cyan-400 transition-colors"
                        title="Open Full Page Dossier"
                      >
                        <ArrowUpRight size={13} className="inline" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="pt-1.5 border-t border-soc-border text-[9px] font-mono text-slate-400 flex justify-between items-center">
            <span>Showing {Math.min(8, filteredAndSortedQueue.length)} of {filteredAndSortedQueue.length} Threats</span>
            <span className="text-cyan-400">Click row for Instant Drawer</span>
          </div>
        </div>

        {/* AREA 2 (4 Cols): Live Investigation Activity Feed */}
        <div className="lg:col-span-4 soc-panel p-3.5 space-y-2.5">
          <div className="flex items-center justify-between pb-2 border-b border-soc-border">
            <div className="flex items-center gap-1.5">
              <Radio size={15} className="text-cyan-400 animate-soc-pulse" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-100 font-mono">
                LIVE INVESTIGATION FEED
              </h3>
            </div>
            <span className="text-[9px] text-cyan-400 font-mono">STREAM ACTIVE · {feedTimestamp}</span>
          </div>

          <div className="space-y-2 max-h-[320px] overflow-y-auto font-mono text-xs">
            {customersData?.items?.slice(0, 6).map((item, idx) => (
              <div
                key={idx}
                onClick={() => handleOpenDrawer(item)}
                className="p-2 rounded bg-soc-surface border border-soc-border hover:border-cyan-500/50 cursor-pointer transition-colors space-y-1 group"
              >
                <div className="flex items-center justify-between text-[10px]">
                  <div className="flex items-center gap-1.5">
                    <span className={`w-1.5 h-1.5 rounded-full ${item.risk_level === 'CRITICAL' ? 'bg-red-500 animate-pulse' : 'bg-orange-500'}`} />
                    <span className="font-bold text-cyan-400 group-hover:text-cyan-300">{item.customer_id}</span>
                  </div>
                  <span className="text-slate-400">{item.home_city}</span>
                </div>
                <div className="text-[11px] text-slate-200 truncate">
                  {item.top_signal.replace(/_/g, ' ')}
                </div>
                <div className="flex items-center justify-between text-[9px] text-slate-400 pt-0.5 border-t border-soc-border/50">
                  <span className="text-purple-400 font-bold">{item.ring_id || 'Isolated'}</span>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-300">₹{item.total_spend.toLocaleString()}</span>
                    <span className="text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5">
                      Inspect <ArrowRight size={10} />
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AREA 3 (3 Cols): AI Agent Operations (6-Agent Swarm) */}
        <div className="lg:col-span-3 soc-panel p-3.5 space-y-2.5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-2 border-b border-soc-border">
              <div className="flex items-center gap-1.5">
                <Bot size={15} className="text-cyan-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-100 font-mono">
                  AI AGENT SWARM
                </h3>
              </div>
              <span className="text-[9px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-500/20 font-mono font-bold">
                6 ACTIVE
              </span>
            </div>

            {/* 6 Connected Agent Steps */}
            <div className="space-y-2 font-mono text-xs pt-1">
              {agentSwarm.map((ag) => (
                <div
                  key={ag.name}
                  className="p-1.5 rounded bg-soc-surface border border-soc-border hover:border-slate-600 transition-colors space-y-1"
                >
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="font-bold text-slate-200 truncate max-w-[130px]">{ag.name}</span>
                    <span className="text-[9px] px-1 rounded bg-[#0D131F] border border-soc-border font-bold text-emerald-400">
                      {ag.status}
                    </span>
                  </div>
                  {/* Progress Bar */}
                  <div className="w-full bg-[#080B11] rounded h-1 overflow-hidden border border-soc-border/40">
                    <div className="h-full rounded" style={{ backgroundColor: ag.color, width: `${ag.progress}%` }} />
                  </div>
                  <div className="text-[8px] text-slate-400 truncate">{ag.finding}</div>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => navigate('/agents')}
            className="w-full py-2 px-3 mt-2 text-xs font-mono font-bold rounded bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/40 transition-colors flex items-center justify-center gap-1.5"
          >
            <span>Open Multi-Agent Console</span>
            <ArrowUpRight size={13} />
          </button>
        </div>
      </div>

      {/* ============================================================
          ROW 5 — INTELLIGENCE & TOPOLOGY METRICS
          High-density strip of deep structural and ML telemetry
          ============================================================ */}
      <div className="soc-panel p-3.5 space-y-2.5">
        <div className="flex items-center justify-between pb-1.5 border-b border-soc-border">
          <div className="flex items-center gap-1.5">
            <Server size={14} className="text-cyan-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
              INTELLIGENCE & GRAPH ANALYTICS METRICS
            </h3>
          </div>
          <span className="text-[9px] font-mono text-slate-400">Topology Partition State · Fully Synced</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 font-mono text-xs">
          <div className="p-2 bg-soc-surface border border-soc-border rounded space-y-0.5">
            <span className="text-[9px] text-slate-400 uppercase font-bold">Louvain Modularity</span>
            <div className="text-sm font-bold text-purple-400">0.812</div>
            <div className="text-[8px] text-slate-400">Dense Cluster Cohesion</div>
          </div>

          <div className="p-2 bg-soc-surface border border-soc-border rounded space-y-0.5">
            <span className="text-[9px] text-slate-400 uppercase font-bold">IF Contamination</span>
            <div className="text-sm font-bold text-amber-400">2.0%</div>
            <div className="text-[8px] text-slate-400">Anomaly Outlier Rate</div>
          </div>

          <div className="p-2 bg-soc-surface border border-soc-border rounded space-y-0.5">
            <span className="text-[9px] text-slate-400 uppercase font-bold">Graph Nodes</span>
            <div className="text-sm font-bold text-slate-100">14,124</div>
            <div className="text-[8px] text-slate-400">Heterogeneous Vertices</div>
          </div>

          <div className="p-2 bg-soc-surface border border-soc-border rounded space-y-0.5">
            <span className="text-[9px] text-slate-400 uppercase font-bold">Graph Edges</span>
            <div className="text-sm font-bold text-slate-100">28,490</div>
            <div className="text-[8px] text-slate-400">Relational Connections</div>
          </div>

          <div className="p-2 bg-soc-surface border border-soc-border rounded space-y-0.5">
            <span className="text-[9px] text-slate-400 uppercase font-bold">Detected Rings</span>
            <div className="text-sm font-bold text-red-400">26</div>
            <div className="text-[8px] text-slate-400">Isolated Syndicates</div>
          </div>

          <div className="p-2 bg-soc-surface border border-soc-border rounded space-y-0.5">
            <span className="text-[9px] text-slate-400 uppercase font-bold">Monitored Accounts</span>
            <div className="text-sm font-bold text-cyan-400">2,000</div>
            <div className="text-[8px] text-slate-400">100% Surveillance</div>
          </div>

          <div className="p-2 bg-soc-surface border border-soc-border rounded space-y-0.5">
            <span className="text-[9px] text-slate-400 uppercase font-bold">Indexed Txns</span>
            <div className="text-sm font-bold text-emerald-400">10,000</div>
            <div className="text-[8px] text-slate-400">Processed Records</div>
          </div>
        </div>
      </div>

      {/* ============================================================
          ROW 6 — PRIORITY TARGET DOSSIERS
          With Circular Radial Risk Gauge for Primary Target
          ============================================================ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3.5">
        {/* Target 1: Highest-Risk Customer with Circular Radial Meter */}
        <div className="soc-interactive-card soc-interactive-card-critical p-4 space-y-3 border-red-500/30 bg-gradient-to-br from-[#0D131F] via-[#0D131F] to-red-950/20 flex flex-col justify-between">
          <div className="space-y-2.5">
            <div className="flex items-center justify-between pb-1.5 border-b border-red-900/40">
              <span className="text-xs font-bold uppercase tracking-wider text-red-400 flex items-center gap-1.5 font-mono">
                <Target size={14} />
                PRIMARY RISK TARGET
              </span>
              <RiskBadge
                level={highestCust?.risk_level || 'CRITICAL'}
                score={highestCust?.risk_score}
                size="sm"
              />
            </div>

            {/* Entity Header with Radial Meter */}
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-lg font-bold font-mono text-slate-100">{highestCust?.entity_id || 'CUST_00028'}</div>
                <p className="text-xs text-slate-300 font-sans mt-0.5">
                  {highestCust?.detail || 'Associated with syndicate FR_015'}
                </p>
                <div className="text-[10px] text-slate-400 font-mono mt-1">
                  Location: <span className="text-slate-200">Mumbai</span> · Outflow: <span className="text-red-400 font-bold">₹4.89L</span>
                </div>
              </div>

              {/* Radial Risk Gauge (SVG) */}
              <div className="relative w-16 h-16 flex-shrink-0 flex items-center justify-center">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                  <path
                    className="text-slate-800"
                    strokeWidth="3.5"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path
                    className="text-red-500"
                    strokeDasharray="99.1, 100"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center font-mono">
                  <span className="text-xs font-black text-red-400">99.1</span>
                  <span className="text-[7px] text-slate-400">/ 100</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-1">
              <div className="p-2 bg-soc-surface border border-soc-border rounded">
                <span className="text-[9px] text-slate-400 uppercase font-bold">Primary Signal</span>
                <div className="text-cyan-400 font-bold truncate">shared_device_cluster</div>
              </div>
              <div className="p-2 bg-soc-surface border border-soc-border rounded">
                <span className="text-[9px] text-slate-400 uppercase font-bold">Syndicate</span>
                <div className="text-purple-400 font-bold">FR_015</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-soc-border/60">
            <button
              onClick={() => handleOpenDrawer({
                id: highestCust?.entity_id || 'CUST_00028',
                type: 'customer',
                risk_score: 99.1,
                risk_level: 'CRITICAL',
                top_signal: 'shared_device_cluster',
                ring_id: 'FR_015',
                home_city: 'Mumbai',
                total_spend: 489200,
                transaction_count: 34,
              })}
              className="py-2 px-2 text-xs font-mono font-bold rounded bg-soc-surface border border-red-500/40 text-red-300 hover:bg-red-950/30 transition-colors flex items-center justify-center gap-1"
            >
              <span>Inspect</span>
              <Eye size={12} />
            </button>
            <Link
              to={`/customers/${highestCust?.entity_id || 'CUST_00028'}`}
              className="py-2 px-2 text-xs font-mono font-bold rounded bg-red-600 hover:bg-red-500 text-white transition-colors flex items-center justify-center gap-1 shadow-sm"
            >
              <span>Full Dossier</span>
              <ArrowUpRight size={13} />
            </Link>
          </div>
        </div>

        {/* Target 2: Largest Syndicate */}
        <div className="soc-interactive-card soc-interactive-card-purple p-4 space-y-3 border-purple-500/30 bg-gradient-to-br from-[#0D131F] via-[#0D131F] to-purple-950/20 flex flex-col justify-between">
          <div className="space-y-2.5">
            <div className="flex items-center justify-between pb-1.5 border-b border-purple-900/40">
              <span className="text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5 font-mono">
                <Network size={14} />
                LARGEST SYNDICATE RING
              </span>
              <RiskBadge
                level={highestRing?.risk_level || 'CRITICAL'}
                score={highestRing?.risk_score || 100.0}
                size="sm"
              />
            </div>

            <div>
              <div className="text-lg font-bold font-mono text-slate-100">{highestRing?.entity_id || 'FR_017'}</div>
              <p className="text-xs text-slate-300 font-sans mt-0.5">
                {highestRing?.detail || '161 member accounts funneled through 45 shared devices'}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-1">
              <div className="p-2 bg-soc-surface border border-soc-border rounded">
                <span className="text-[9px] text-slate-400 uppercase font-bold">Member Scale</span>
                <div className="text-slate-100 font-bold">161 Accounts</div>
              </div>
              <div className="p-2 bg-soc-surface border border-soc-border rounded">
                <span className="text-[9px] text-slate-400 uppercase font-bold">Spend Volume</span>
                <div className="text-purple-400 font-bold">₹42.45L</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-soc-border/60">
            <button
              onClick={() => handleOpenDrawer({
                id: highestRing?.entity_id || 'FR_017',
                type: 'ring',
                risk_score: 100.0,
                risk_level: 'CRITICAL',
                customer_count: 161,
                transaction_volume: 4245171,
                shared_devices_count: 45,
                shared_payments_count: 41,
                shared_ips_count: 30,
              })}
              className="py-2 px-2 text-xs font-mono font-bold rounded bg-soc-surface border border-purple-500/40 text-purple-300 hover:bg-purple-950/30 transition-colors flex items-center justify-center gap-1"
            >
              <span>Inspect</span>
              <Eye size={12} />
            </button>
            <Link
              to={`/fraud-rings/${highestRing?.entity_id || 'FR_017'}`}
              className="py-2 px-2 text-xs font-mono font-bold rounded bg-purple-600 hover:bg-purple-500 text-white transition-colors flex items-center justify-center gap-1 shadow-sm"
            >
              <span>Topology</span>
              <ArrowUpRight size={13} />
            </Link>
          </div>
        </div>

        {/* Target 3: Critical Priority Action Queue */}
        <div className="soc-interactive-card p-4 space-y-3 border-cyan-500/30 bg-gradient-to-br from-[#0D131F] via-[#0D131F] to-cyan-950/20 flex flex-col justify-between">
          <div className="space-y-2.5">
            <div className="flex items-center justify-between pb-1.5 border-b border-cyan-900/40">
              <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5 font-mono">
                <Radio size={14} className="animate-soc-pulse" />
                CRITICAL ACTION QUEUE
              </span>
              <span className="text-[9px] font-mono text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/30 font-bold">
                {criticalCount} PENDING
              </span>
            </div>

            <div>
              <div className="text-lg font-bold font-mono text-slate-100">{criticalCount} Priority Incidents</div>
              <p className="text-xs text-slate-300 font-sans mt-0.5">
                Accounts exceeding 80.0 critical risk threshold requiring immediate restriction and sign-off.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-1">
              <div className="p-2 bg-soc-surface border border-soc-border rounded">
                <span className="text-[9px] text-slate-400 uppercase font-bold">Critical Outflow</span>
                <div className="text-red-400 font-bold">₹70.7L</div>
              </div>
              <div className="p-2 bg-soc-surface border border-soc-border rounded">
                <span className="text-[9px] text-slate-400 uppercase font-bold">Avg Alert Score</span>
                <div className="text-slate-100 font-bold">92.4 / 100</div>
              </div>
            </div>
          </div>

          <Link
            to="/customers?risk_level=CRITICAL"
            className="w-full py-2 px-3 text-xs font-mono font-bold rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 transition-colors flex items-center justify-center gap-1.5 shadow-sm"
          >
            <span>Triage All Critical Alerts ({criticalCount})</span>
            <ArrowUpRight size={14} />
          </Link>
        </div>
      </div>

      {/* ============================================================
          INTERACTIVE FORENSIC INTELLIGENCE DRAWER
          Slide-out panel for immediate triage without leaving the dashboard
          ============================================================ */}
      <IntelligenceDrawer
        entity={drawerEntity}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </div>
  );
}

export default DashboardPage;
