import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  CreditCard,
  Store,
  Smartphone,
  Globe,
  MapPin,
  Calendar,
  AlertTriangle,
  User,
  ChevronRight,
  ArrowUpRight,
} from 'lucide-react';
import apiService from '../services/api';
import RiskBadge from '../components/RiskBadge';
import RiskMeter from '../components/RiskMeter';
import CytoscapeGraph from '../components/CytoscapeGraph';
import EvidenceTable from '../components/EvidenceTable';

export function TransactionDetailPage() {
  const { transactionId } = useParams();
  const navigate = useNavigate();

  const [transaction, setTransaction] = useState(null);
  const [networkGraph, setNetworkGraph] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadTransaction() {
      try {
        setLoading(true);
        setError(null);
        const [txnRes, netRes] = await Promise.all([
          apiService.getTransaction(transactionId),
          apiService.getNetwork('transaction', transactionId),
        ]);
        setTransaction(txnRes);
        setNetworkGraph(netRes);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadTransaction();
  }, [transactionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 text-cyan-400">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs font-mono text-slate-400">Loading Transaction Forensics for {transactionId}...</p>
        </div>
      </div>
    );
  }

  if (error || !transaction) {
    return (
      <div className="space-y-4 p-6">
        <button
          onClick={() => navigate('/customers')}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200"
        >
          <ArrowLeft size={14} /> Back to Search
        </button>
        <div className="glass-panel p-8 text-center text-xs text-red-400 space-y-2 border-red-500/30">
          <AlertTriangle className="mx-auto text-red-400" size={32} />
          <h3 className="text-sm font-bold text-red-300">Transaction Investigation Error</h3>
          <p>{error || `Transaction '${transactionId}' not found.`}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-16">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link to="/customers" className="hover:text-slate-200">Customers</Link>
        <ChevronRight size={14} />
        <Link to={`/customers/${transaction.customer_id}`} className="hover:text-slate-200 font-mono">
          {transaction.customer_id}
        </Link>
        <ChevronRight size={14} />
        <span className="text-slate-200 font-mono font-semibold">{transaction.transaction_id}</span>
      </div>

      {/* Hero Dossier */}
      <div className="glass-panel p-6 relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border-slate-800">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-extrabold text-slate-100 font-mono">{transaction.transaction_id}</h1>
              <RiskBadge level={transaction.risk_level} score={transaction.risk_score} size="lg" />
            </div>

            <div className="text-3xl font-extrabold font-mono text-slate-100">
              ₹{transaction.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 font-mono">
              <span className="flex items-center gap-1.5 text-slate-300">
                <Calendar size={14} className="text-cyan-400" />
                {transaction.timestamp}
              </span>
              <span className="flex items-center gap-1.5 text-pink-400">
                <Store size={14} />
                {transaction.merchant_id}
              </span>
              <span className="flex items-center gap-1.5 text-amber-400">
                <CreditCard size={14} />
                {transaction.payment_type}
              </span>
              <span className="flex items-center gap-1.5 text-purple-400">
                <MapPin size={14} />
                {transaction.city}
              </span>
            </div>
          </div>

          {/* Right: Initiating Account Link & Risk Meter */}
          <div className="flex items-center gap-4">
            <Link
              to={`/customers/${transaction.customer_id}`}
              className="p-3.5 bg-slate-900/90 border border-slate-800 hover:border-cyan-500/50 rounded-xl text-left transition-colors group"
            >
              <span className="text-[10px] uppercase font-bold text-slate-400 flex items-center justify-between">
                <span>Initiating Customer</span>
                <ArrowUpRight size={12} className="text-cyan-400 group-hover:translate-x-0.5 transition-transform" />
              </span>
              <div className="text-base font-bold font-mono text-cyan-400 mt-1">
                {transaction.customer_id}
              </div>
              <span className="text-[11px] text-slate-400">Click for full dossier</span>
            </Link>
            <RiskMeter score={transaction.risk_score} level={transaction.risk_level} />
          </div>
        </div>
      </div>

      {/* Network Graph */}
      {networkGraph && (
        <CytoscapeGraph
          graphData={networkGraph}
          height="380px"
          title={`Transaction Entity Linkage Graph (${transaction.transaction_id})`}
        />
      )}

      {/* Evidence Breakdown */}
      <EvidenceTable
        evidence={transaction.evidence}
        protectiveFactors={transaction.protective_factors}
        contributingSignals={transaction.contributing_signals}
      />
    </div>
  );
}

export default TransactionDetailPage;
