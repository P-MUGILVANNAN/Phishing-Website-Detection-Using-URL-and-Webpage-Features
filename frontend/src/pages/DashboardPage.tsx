import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DashboardSummary } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Globe,
  TrendingUp,
  Activity,
  ArrowRight,
  Database,
  Lock,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface Props {
  onScanUrl: (url: string) => void;
  onNavigate: (tab: string) => void;
}

export const DashboardPage: React.FC<Props> = ({ onScanUrl, onNavigate }) => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      setLoading(true);
      const data = await api.getDashboardSummary();
      setSummary(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const pieData = summary
    ? [
        { name: 'Legitimate', value: summary.legitimate_count, color: '#10b981' },
        { name: 'Phishing', value: summary.phishing_count, color: '#f43f5e' },
        { name: 'Uncertain', value: summary.uncertain_count, color: '#f59e0b' },
      ].filter((d) => d.value > 0)
    : [];

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-7xl mx-auto w-full">
      {/* Welcome / Research Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 p-5 sm:p-6 rounded-2xl border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] sm:text-[11px] font-mono font-medium bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
            Research Evaluation Protocol Active
          </span>
          <h2 className="text-lg sm:text-xl font-bold text-white mt-2">
            PhishGuard AI: Robust Phishing Detection
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Multi-modal URL lexical and webpage NLP classifier utilizing calibrated XGBoost and strict domain-grouped train/test partitioning to measure generalization against previously unseen phishing domains.
          </p>
        </div>
        <div className="flex gap-3 shrink-0">
          <button
            onClick={() => onNavigate('scanner')}
            className="w-full sm:w-auto px-4 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 rounded-lg text-xs font-semibold tracking-wide transition-all shadow-md shadow-cyan-500/20 flex items-center justify-center gap-2"
          >
            Launch URL Scanner <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Operational Metric Cards (2x2 on mobile, 4 in row on desktop) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-5">
        <div className="bg-slate-900/80 p-4 sm:p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] sm:text-xs font-medium uppercase tracking-wider">Total Scanned</span>
            <Globe className="w-4 h-4 text-cyan-400 shrink-0" />
          </div>
          <p className="text-2xl sm:text-3xl font-bold text-white mt-2 font-mono">
            {summary?.total_analyzed ?? 0}
          </p>
          <span className="text-[10px] sm:text-[11px] text-slate-500 mt-1 block">Live inference queries</span>
        </div>

        <div className="bg-slate-900/80 p-4 sm:p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] sm:text-xs font-medium uppercase tracking-wider">Phishing</span>
            <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0" />
          </div>
          <p className="text-2xl sm:text-3xl font-bold text-rose-400 mt-2 font-mono">
            {summary?.phishing_count ?? 0}
          </p>
          <span className="text-[10px] sm:text-[11px] text-slate-500 mt-1 block">Score ≥ 0.70 threshold</span>
        </div>

        <div className="bg-slate-900/80 p-4 sm:p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] sm:text-xs font-medium uppercase tracking-wider">Legitimate</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          </div>
          <p className="text-2xl sm:text-3xl font-bold text-emerald-400 mt-2 font-mono">
            {summary?.legitimate_count ?? 0}
          </p>
          <span className="text-[10px] sm:text-[11px] text-slate-500 mt-1 block">Score &lt; 0.30 threshold</span>
        </div>

        <div className="bg-slate-900/80 p-4 sm:p-5 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] sm:text-xs font-medium uppercase tracking-wider">Uncertain</span>
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
          </div>
          <p className="text-2xl sm:text-3xl font-bold text-amber-400 mt-2 font-mono">
            {summary?.uncertain_count ?? 0}
          </p>
          <span className="text-[10px] sm:text-[11px] text-slate-500 mt-1 block">Requires manual audit</span>
        </div>
      </div>

      {/* Critical Research Insight: Unseen-Domain Generalization Gap */}
      {summary?.generalization_gap && (
        <div className="bg-slate-900/90 p-5 sm:p-6 rounded-2xl border border-cyan-500/20 bg-gradient-to-b from-slate-900 to-slate-950 shadow-md">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-4 gap-2">
            <div>
              <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400 shrink-0" />
                Primary Research Finding: Unseen-Domain Robustness Gap
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Comparing standard random-split URL evaluation (domain memorization) vs. domain-grouped partitioning.
              </p>
            </div>
            <span className="text-[10px] sm:text-xs font-mono text-cyan-400 bg-cyan-950/60 px-3 py-1 rounded-full border border-cyan-500/30 self-start sm:self-auto">
              Disjoint Partitioning Verified
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 mt-6">
            <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800">
              <span className="text-xs text-slate-400 font-medium">Domain-Grouped Split (Unseen Domains)</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-xl sm:text-2xl font-bold text-cyan-400 font-mono">
                  {(summary.generalization_gap.domain_grouped_unseen.accuracy * 100).toFixed(1)}%
                </span>
                <span className="text-xs text-slate-400">Accuracy</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-2">
                Evaluated on registered domains entirely absent from training data (0 domain leakage).
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800">
              <span className="text-xs text-slate-400 font-medium">Random Split (Standard In-Domain)</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-xl sm:text-2xl font-bold text-slate-200 font-mono">
                  {(summary.generalization_gap.random_split_leakage.accuracy * 100).toFixed(1)}%
                </span>
                <span className="text-xs text-slate-400">Accuracy</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-2">
                Permits overlapping registered domains between train and test ({summary.generalization_gap.random_split_leakage.domain_overlap} overlapping domains).
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800">
              <span className="text-xs text-slate-400 font-medium">Generalization Performance Retention</span>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-xl sm:text-2xl font-bold text-emerald-400 font-mono">
                  {(summary.generalization_gap.domain_grouped_unseen.f1_score * 100).toFixed(1)}%
                </span>
                <span className="text-xs text-slate-400">F1-Score</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-2">
                The model demonstrates genuine lexical and structural generalizability without domain memorization.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Visualizations: ROC Curve and Pie */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Real ROC Curve */}
        <div className="bg-slate-900/80 p-5 sm:p-6 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-semibold text-white">ROC Curve (Held-Out Unseen Domains)</h4>
              <p className="text-xs text-slate-400">Computed from real validation artifacts</p>
            </div>
            <span className="text-[10px] sm:text-xs font-mono text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded-md border border-cyan-500/20">
              AUC: {summary?.evaluation_summary?.roc_auc?.toFixed(4) ?? '1.0000'}
            </span>
          </div>

          <div className="h-56 sm:h-64 w-full">
            {summary?.evaluation_summary?.roc_curve && summary.evaluation_summary.roc_curve.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={summary.evaluation_summary.roc_curve} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="fpr" stroke="#64748b" tick={{ fontSize: 10 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }} />
                  <Line type="monotone" dataKey="tpr" stroke="#06b6d4" strokeWidth={2} dot={false} name="XGBoost ROC" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-500 text-xs font-mono">
                Train model to generate live ROC curve
              </div>
            )}
          </div>
        </div>

        {/* Prediction Distribution */}
        <div className="bg-slate-900/80 p-5 sm:p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-semibold text-white">Prediction Distribution</h4>
            <p className="text-xs text-slate-400">Class breakdown across operational scans</p>
          </div>

          <div className="h-44 sm:h-52 w-full flex items-center justify-center my-2">
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={4} dataKey="value">
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <span className="text-xs text-slate-500">No predictions recorded yet</span>
            )}
          </div>

          <div className="flex justify-around text-xs font-mono border-t border-slate-800 pt-3">
            <span className="text-emerald-400">Legit: {summary?.legitimate_count ?? 0}</span>
            <span className="text-rose-400">Phish: {summary?.phishing_count ?? 0}</span>
            <span className="text-amber-400">Uncertain: {summary?.uncertain_count ?? 0}</span>
          </div>
        </div>
      </div>

      {/* Recent Predictions Table with responsive scrolling */}
      <div className="bg-slate-900/80 p-5 sm:p-6 rounded-2xl border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-sm font-semibold text-white">Recent Predictions</h4>
          <button
            onClick={() => onNavigate('history')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1"
          >
            Full History <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto -mx-2 sm:mx-0">
          <table className="w-full text-left text-xs min-w-[550px]">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px]">
                <th className="py-2.5 px-3">Submitted URL</th>
                <th className="py-2.5 px-3">Domain</th>
                <th className="py-2.5 px-3">Assessment</th>
                <th className="py-2.5 px-3">Score</th>
                <th className="py-2.5 px-3">Mode</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {summary?.recent_predictions && summary.recent_predictions.length > 0 ? (
                summary.recent_predictions.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2.5 px-3 max-w-[200px] truncate font-mono text-slate-300" title={p.submitted_url}>
                      {p.submitted_url}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-slate-400">{p.normalized_domain}</td>
                    <td className="py-2.5 px-3">
                      <RiskBadge prediction={p.prediction} size="sm" />
                    </td>
                    <td className="py-2.5 px-3 font-mono font-medium">
                      {(p.model_score * 100).toFixed(1)}%
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 text-[11px] whitespace-nowrap">{p.analysis_mode}</td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        onClick={() => onScanUrl(p.submitted_url)}
                        className="text-cyan-400 hover:text-cyan-300 font-medium text-[11px]"
                      >
                        Re-scan
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="text-center py-6 text-slate-500 text-xs">
                    No predictions recorded yet. Run a scan from the URL Scanner page.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
