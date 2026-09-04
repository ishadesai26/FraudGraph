import React from 'react';
import { Clock, Zap, CreditCard, Smartphone, Globe, Store } from 'lucide-react';
import { Link } from 'react-router-dom';

export function TimelineView({ timeline = [] }) {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="soc-panel p-6 text-center text-xs text-slate-400 font-mono italic">
        No transactional timeline events recorded for this entity.
      </div>
    );
  }

  return (
    <div className="soc-panel p-4 space-y-4">
      <div className="flex items-center justify-between pb-2.5 border-b border-soc-border">
        <div className="flex items-center gap-2">
          <Clock className="text-cyan-400" size={16} />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
            CHRONOLOGICAL TRANSACTION AUDIT FEED
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          {timeline.length} Recorded Events
        </span>
      </div>

      <div className="relative border-l border-soc-border ml-3 space-y-3.5 pl-5 py-1">
        {timeline.map((event, idx) => {
          const isBurst = event.is_burst;
          return (
            <div key={idx} className="relative group">
              {/* Node Dot */}
              <div
                className={`absolute -left-[25px] top-2 w-2.5 h-2.5 rounded-full border-2 border-[#090D16] ${
                  isBurst ? 'bg-red-500 shadow-sm shadow-red-500/50' : 'bg-cyan-500'
                }`}
              />

              {/* Event Card */}
              <div
                className={`p-3 rounded border transition-colors space-y-2 ${
                  isBurst
                    ? 'bg-red-950/10 border-red-500/30 hover:border-red-500/50'
                    : 'bg-soc-surface border-soc-border hover:border-slate-700'
                }`}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Link
                      to={`/transactions/${event.transaction_id}`}
                      className="text-xs font-mono font-bold text-cyan-400 hover:underline"
                    >
                      {event.transaction_id}
                    </Link>
                    <span className="text-[11px] font-mono text-slate-400">{event.timestamp}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    {isBurst && (
                      <span className="inline-flex items-center gap-1 text-[9px] font-bold px-1.5 py-0.5 rounded bg-red-500/15 text-red-400 border border-red-500/30 font-mono">
                        <Zap size={11} /> BURST SYNC ({Math.round(event.seconds_since_previous || 0)}s)
                      </span>
                    )}
                    <span className="text-sm font-bold font-mono text-slate-100">
                      ₹{event.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>

                {/* Meta details grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-soc-border/70 text-[10px] text-slate-400 font-mono">
                  <div className="flex items-center gap-1.5 truncate">
                    <Store size={12} className="text-pink-400 flex-shrink-0" />
                    <span className="truncate">{event.merchant_id}</span>
                  </div>
                  <div className="flex items-center gap-1.5 truncate">
                    <CreditCard size={12} className="text-amber-400 flex-shrink-0" />
                    <span className="truncate">{event.payment_type}</span>
                  </div>
                  <div className="flex items-center gap-1.5 truncate">
                    <Smartphone size={12} className="text-blue-400 flex-shrink-0" />
                    <span className="truncate">{event.device_id}</span>
                  </div>
                  <div className="flex items-center gap-1.5 truncate">
                    <Globe size={12} className="text-purple-400 flex-shrink-0" />
                    <span className="truncate">{event.ip_id} ({event.city})</span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default TimelineView;
