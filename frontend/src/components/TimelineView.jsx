import React from 'react';
import { Clock, Zap, CreditCard, Smartphone, Globe, Store } from 'lucide-react';
import { Link } from 'react-router-dom';

export function TimelineView({ timeline = [] }) {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="glass-panel p-6 text-center text-xs text-slate-400 italic">
        No transactional timeline recorded for this entity.
      </div>
    );
  }

  return (
    <div className="glass-panel p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Clock className="text-cyan-400" size={18} />
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
            Chronological Transaction Forensics
          </h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {timeline.length} Total Events
        </span>
      </div>

      <div className="relative border-l-2 border-slate-800 ml-3.5 space-y-4 pl-6 py-2">
        {timeline.map((event, idx) => {
          const isBurst = event.is_burst;
          return (
            <div key={idx} className="relative group">
              {/* Timeline Node Dot */}
              <div
                className={`absolute -left-[31px] top-1.5 w-3.5 h-3.5 rounded-full border-2 border-[#0B0F19] ${
                  isBurst ? 'bg-red-500 shadow-md shadow-red-500/50' : 'bg-cyan-500'
                }`}
              />

              {/* Event Card */}
              <div className="p-3.5 bg-slate-900/80 border border-slate-800 rounded-xl hover:border-slate-700 transition-colors space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Link
                      to={`/transactions/${event.transaction_id}`}
                      className="text-xs font-mono font-bold text-cyan-400 hover:underline"
                    >
                      {event.transaction_id}
                    </Link>
                    <span className="text-xs font-mono text-slate-400">{event.timestamp}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {isBurst && (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded bg-red-500/15 text-red-400 border border-red-500/30 font-mono">
                        <Zap size={12} /> BURST SYNC ({Math.round(event.seconds_since_previous || 0)}s)
                      </span>
                    )}
                    <span className="text-sm font-bold font-mono text-slate-100">
                      ₹{event.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>

                {/* Meta details */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800/60 text-[11px] text-slate-400 font-mono">
                  <div className="flex items-center gap-1.5">
                    <Store size={13} className="text-pink-400" />
                    <span>{event.merchant_id}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <CreditCard size={13} className="text-amber-400" />
                    <span>{event.payment_type}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Smartphone size={13} className="text-blue-400" />
                    <span>{event.device_id}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Globe size={13} className="text-purple-400" />
                    <span>{event.ip_id} ({event.city})</span>
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
