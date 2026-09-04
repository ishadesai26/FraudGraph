import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  X,
  ArrowUpRight,
  ShieldAlert,
  Network,
  Bot,
  Zap,
  Activity,
  HardDrive,
  CreditCard,
  Globe,
  User,
  Clock,
  ExternalLink,
  Layers,
  MapPin,
} from 'lucide-react';
import RiskBadge from './RiskBadge';

export function IntelligenceDrawer({ entity, isOpen, onClose }) {
  const navigate = useNavigate();

  // Escape key to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !entity) return null;

  // Normalize entity attributes depending on whether it came from customer list, ring list, or graph node
  const id = entity.customer_id || entity.ring_id || entity.id || 'UNKNOWN';
  const type = entity.type || (entity.customer_id ? 'customer' : entity.ring_id ? 'ring' : 'entity');
  const riskScore = entity.risk_score !== undefined ? entity.risk_score : 90.0;
  const riskLevel = entity.risk_level || (riskScore >= 80 ? 'CRITICAL' : riskScore >= 60 ? 'HIGH' : riskScore >= 35 ? 'MEDIUM' : 'LOW');
  const ringId = entity.ring_id;
  const topSignal = entity.top_signal || entity.detail || entity.subtext || 'Coordinated community anomaly';
  const spend = entity.total_spend || entity.transaction_volume;
  const location = entity.home_city;
  const txnCount = entity.transaction_count;

  const handleOpenDossier = () => {
    onClose();
    if (type === 'customer' || id.startsWith('CUST_')) {
      navigate(`/customers/${id}`);
    } else if (type === 'ring' || id.startsWith('FR_')) {
      navigate(`/fraud-rings/${id}`);
    } else if (type === 'transaction' || id.startsWith('TXN_')) {
      navigate(`/transactions/${id}`);
    } else {
      navigate(`/customers`);
    }
  };

  const handleLaunchAgentInvestigation = () => {
    onClose();
    navigate('/agents');
  };

  const handleOpenSimulator = () => {
    onClose();
    navigate('/simulation');
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 transition-opacity animate-in fade-in duration-200"
        onClick={onClose}
      />

      {/* Slide-Over Drawer Container */}
      <div className="fixed top-0 right-0 bottom-0 w-full sm:w-[420px] bg-[#090D16] border-l border-soc-border shadow-2xl z-50 flex flex-col justify-between overflow-hidden animate-in slide-in-from-right duration-300 font-sans select-none">
        {/* Drawer Header */}
        <div className="p-4 bg-[#0D131F] border-b border-soc-border space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-soc-pulse"></span>
              <span className="text-[10px] font-bold uppercase tracking-widest text-cyan-400 font-mono">
                FORENSIC INTELLIGENCE DRAWER
              </span>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded bg-soc-surface border border-soc-border text-slate-400 hover:text-white hover:border-slate-600 transition-colors"
              title="Close Drawer [Esc]"
            >
              <X size={15} />
            </button>
          </div>

          <div className="flex items-center justify-between pt-1">
            <div>
              <span className="text-[9px] uppercase font-bold text-slate-400 font-mono">
                {type} ENTITY TARGET
              </span>
              <h2 className="text-xl font-black font-mono text-slate-100 tracking-tight">
                {id}
              </h2>
            </div>
            <RiskBadge level={riskLevel} score={riskScore} size="lg" />
          </div>
        </div>

        {/* Scrollable Body Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-xs text-slate-300">
          {/* Quick Threat Severity Card */}
          <div className="p-3 rounded bg-soc-panel border border-soc-border space-y-2">
            <div className="flex justify-between items-center text-[10px] text-slate-400 uppercase font-bold">
              <span>Risk Calibration Score</span>
              <span className="text-red-400 font-extrabold">{riskScore.toFixed(1)} / 100</span>
            </div>
            <div className="w-full bg-[#080B11] h-2 rounded-full overflow-hidden border border-soc-border">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${riskScore}%`,
                  backgroundColor: riskScore >= 80 ? '#EF4444' : riskScore >= 60 ? '#F97316' : '#F59E0B',
                }}
              />
            </div>
            <p className="text-[11px] text-slate-400 font-sans leading-relaxed pt-1">
              Primary Signal: <strong className="text-slate-200">{String(topSignal).replace(/_/g, ' ')}</strong>
            </p>
          </div>

          {/* Forensic Entity Attributes */}
          <div className="space-y-2">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              ENTITY TELEMETRY & ATTRIBUTES
            </div>

            <div className="space-y-1.5">
              {spend !== undefined && (
                <div className="p-2.5 bg-soc-surface border border-soc-border rounded flex justify-between items-center">
                  <span className="text-[11px] text-slate-400 flex items-center gap-1.5">
                    <Activity size={13} className="text-cyan-400" />
                    Transaction Volume
                  </span>
                  <span className="font-bold text-slate-100">₹{spend.toLocaleString()}</span>
                </div>
              )}

              {txnCount !== undefined && (
                <div className="p-2.5 bg-soc-surface border border-soc-border rounded flex justify-between items-center">
                  <span className="text-[11px] text-slate-400 flex items-center gap-1.5">
                    <Clock size={13} className="text-cyan-400" />
                    Indexed Transactions
                  </span>
                  <span className="font-bold text-slate-100">{txnCount} Events</span>
                </div>
              )}

              {ringId && (
                <div className="p-2.5 bg-soc-surface border border-soc-border rounded flex justify-between items-center">
                  <span className="text-[11px] text-slate-400 flex items-center gap-1.5">
                    <Network size={13} className="text-purple-400" />
                    Community Syndicate
                  </span>
                  <button
                    onClick={() => {
                      onClose();
                      navigate(`/fraud-rings/${ringId}`);
                    }}
                    className="font-bold text-purple-400 hover:text-purple-300 underline flex items-center gap-1"
                  >
                    <span>{ringId}</span>
                    <ExternalLink size={11} />
                  </button>
                </div>
              )}

              {location && (
                <div className="p-2.5 bg-soc-surface border border-soc-border rounded flex justify-between items-center">
                  <span className="text-[11px] text-slate-400 flex items-center gap-1.5">
                    <MapPin size={13} className="text-orange-400" />
                    Geographic Registry
                  </span>
                  <span className="font-bold text-slate-200">{location}</span>
                </div>
              )}
            </div>
          </div>

          {/* Relational Graph Endpoints */}
          <div className="space-y-2">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              NETWORK GRAPH CORRELATIONS
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2.5 bg-soc-surface border border-soc-border rounded space-y-1">
                <span className="text-[9px] text-slate-400 uppercase font-bold flex items-center gap-1">
                  <HardDrive size={11} className="text-blue-400" />
                  Hardware Link
                </span>
                <div className="text-slate-200 font-bold text-[11px] truncate">
                  {entity.shared_devices_count ? `${entity.shared_devices_count} Devices` : 'DEV_CLUSTER_ACTIVE'}
                </div>
              </div>

              <div className="p-2.5 bg-soc-surface border border-soc-border rounded space-y-1">
                <span className="text-[9px] text-slate-400 uppercase font-bold flex items-center gap-1">
                  <CreditCard size={11} className="text-amber-400" />
                  Payment Instrument
                </span>
                <div className="text-slate-200 font-bold text-[11px] truncate">
                  {entity.shared_payments_count ? `${entity.shared_payments_count} Cards/VPAs` : 'VPA_REUSE_LINK'}
                </div>
              </div>

              <div className="p-2.5 bg-soc-surface border border-soc-border rounded space-y-1">
                <span className="text-[9px] text-slate-400 uppercase font-bold flex items-center gap-1">
                  <Globe size={11} className="text-purple-400" />
                  Proxy IP Relay
                </span>
                <div className="text-slate-200 font-bold text-[11px] truncate">
                  {entity.shared_ips_count ? `${entity.shared_ips_count} Relay IPs` : 'TOR_VPN_OBFUSCATED'}
                </div>
              </div>

              <div className="p-2.5 bg-soc-surface border border-soc-border rounded space-y-1">
                <span className="text-[9px] text-slate-400 uppercase font-bold flex items-center gap-1">
                  <Bot size={11} className="text-cyan-400" />
                  Multi-Agent Scan
                </span>
                <div className="text-emerald-400 font-bold text-[11px]">
                  CONSENSUS (HIGH)
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Drawer Action Bar */}
        <div className="p-4 bg-[#0D131F] border-t border-soc-border space-y-2">
          <button
            onClick={handleOpenDossier}
            className="w-full py-2.5 px-3 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono font-bold text-xs flex items-center justify-center gap-2 transition-colors shadow-sm"
          >
            <span>Open Full Forensic Dossier</span>
            <ArrowUpRight size={14} />
          </button>

          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleLaunchAgentInvestigation}
              className="py-2 px-3 rounded bg-soc-surface border border-soc-border hover:border-cyan-500/50 text-cyan-400 font-mono font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors"
            >
              <Bot size={13} />
              <span>Agent Swarm</span>
            </button>
            <button
              onClick={handleOpenSimulator}
              className="py-2 px-3 rounded bg-soc-surface border border-soc-border hover:border-amber-500/50 text-amber-400 font-mono font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors"
            >
              <Zap size={13} />
              <span>Simulate Attack</span>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default IntelligenceDrawer;
