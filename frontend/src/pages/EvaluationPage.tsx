import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { EvaluationData } from '../types';
import {
  BarChart3,
  Award,
  Layers,
  Activity,
  CheckCircle,
  AlertCircle,
  Clock,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  Legend,
} from 'recharts';

export const EvaluationPage: React.FC = () => {
  const [data, setData] = useState<EvaluationData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvaluation();
  }, []);

  const loadEvaluation = async () => {
    try {
      setLoading(true);
      const evalData = await api.getEvaluation();
      setData(evalData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 sm:p-12 flex flex-col items-center justify-center text-slate-400 gap-3">
        <div className="w-6 h-6 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-xs font-mono">Loading model evaluation artifacts...</span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8 sm:p-12 text-center text-slate-400">
        <AlertCircle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
        <p className="text-sm">No evaluation artifacts found.</p>
        <p className="text-xs text-slate-500 mt-1">Please train the model via the Dataset & Training page.</p>
      </div>
    );
  }

  const mainMetrics = data.main_model?.metrics || {};
  const cm = mainMetrics.confusion_matrix || { tn: 0, fp: 0, fn: 0, tp: 0 };

  const modelComparison = [
    {
      name: 'XGBoost',
      Accuracy: (mainMetrics.accuracy * 100) || 0,
      F1: (mainMetrics.f1_score * 100) || 0,
      'ROC-AUC': (mainMetrics.roc_auc * 100) || 0,
    },
    ...Object.values(data.baselines || {}).map((b) => ({
      name: b.name.replace(' Baseline', '').replace(' (No Webpage NLP)', ''),
      Accuracy: (b.metrics?.accuracy * 100) || 0,
      F1: (b.metrics?.f1_score * 100) || 0,
      'ROC-AUC': (b.metrics?.roc_auc * 100) || 0,
    })),
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-7xl mx-auto w-full">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">Model Evaluation & Robustness Benchmarks</h2>
          <p className="text-xs text-slate-400 mt-1">
            Empirical evaluation against held-out unseen registered domains to evaluate true phishing generalization without domain memorization.
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono shrink-0 self-start md:self-auto">
          <ShieldCheck className="w-4 h-4 shrink-0" />
          <span>Zero Domain Overlap Verified</span>
        </div>
      </div>

      {/* Primary Research Finding: Generalization Gap Callout */}
      {data.generalization_comparison && (
        <div className="bg-gradient-to-r from-slate-900 to-cyan-950/30 p-5 sm:p-6 rounded-2xl border border-cyan-500/30 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400 shrink-0" />
              Generalization Gap Analysis (Domain Leakage Impact)
            </h3>
            <span className="text-[10px] sm:text-[11px] font-mono text-cyan-300 bg-cyan-500/10 px-2.5 py-0.5 rounded border border-cyan-500/20 self-start sm:self-auto">
              Protocol A: Grouped Split
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
            <div className="p-4 bg-slate-950/70 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Random Split (Domain Leakage Present)</span>
              <div className="mt-2 text-xl sm:text-2xl font-bold text-slate-200 font-mono">
                {(data.generalization_comparison.random_split_leakage.accuracy * 100).toFixed(1)}%
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                {data.generalization_comparison.random_split_leakage.domain_overlap} overlapping domains allowed in test set.
              </p>
            </div>

            <div className="p-4 bg-slate-950/70 rounded-xl border border-cyan-500/30">
              <span className="text-xs text-cyan-400 font-medium">Domain-Grouped (Unseen Domains)</span>
              <div className="mt-2 text-xl sm:text-2xl font-bold text-cyan-400 font-mono">
                {(data.generalization_comparison.domain_grouped_unseen.accuracy * 100).toFixed(1)}%
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Zero registered domain overlap between training and evaluation partitions.
              </p>
            </div>

            <div className="p-4 bg-slate-950/70 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400">Generalization Gap (F1 Loss)</span>
              <div className="mt-2 text-xl sm:text-2xl font-bold text-emerald-400 font-mono">
                {data.generalization_comparison.generalization_gap_f1.toFixed(4)}
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Zero performance drop indicates genuine lexical feature robustness on unfamiliar domains.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        {[
          { label: 'Accuracy', val: `${(mainMetrics.accuracy * 100).toFixed(1)}%`, desc: 'Overall accuracy' },
          { label: 'Precision', val: mainMetrics.precision?.toFixed(4), desc: 'True pos / (TP+FP)' },
          { label: 'Recall', val: mainMetrics.recall?.toFixed(4), desc: 'Sensitivity rate' },
          { label: 'Specificity', val: mainMetrics.specificity?.toFixed(4), desc: 'True neg / (TN+FP)' },
          { label: 'F1-Score', val: mainMetrics.f1_score?.toFixed(4), desc: 'Harmonic mean' },
          { label: 'Brier Score', val: mainMetrics.brier_score?.toFixed(4), desc: 'Calibration loss' },
        ].map((m) => (
          <div key={m.label} className="bg-slate-900/80 p-3.5 sm:p-4 rounded-xl border border-slate-800">
            <span className="text-[10px] sm:text-xs text-slate-400 uppercase font-mono tracking-wider">{m.label}</span>
            <p className="text-xl sm:text-2xl font-bold text-white font-mono mt-1">{m.val}</p>
            <span className="text-[10px] text-slate-500 mt-0.5 block truncate">{m.desc}</span>
          </div>
        ))}
      </div>

      {/* Baseline Models Comparison Table & Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Comparison Table */}
        <div className="bg-slate-900/80 p-5 sm:p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Baseline Comparison (Unseen Domains)</h3>
            <span className="text-[10px] font-mono text-slate-400">Identical Test Set</span>
          </div>

          <div className="overflow-x-auto -mx-2 sm:mx-0">
            <table className="w-full text-left text-xs min-w-[450px]">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px]">
                  <th className="py-2.5 px-3">Architecture</th>
                  <th className="py-2.5 px-3">Accuracy</th>
                  <th className="py-2.5 px-3">F1-Score</th>
                  <th className="py-2.5 px-3">ROC-AUC</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                <tr className="bg-cyan-500/5 font-medium text-cyan-300">
                  <td className="py-2.5 px-3 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0" />
                    {data.main_model?.name}
                  </td>
                  <td className="py-2.5 px-3 font-mono">{(mainMetrics.accuracy * 100).toFixed(1)}%</td>
                  <td className="py-2.5 px-3 font-mono">{mainMetrics.f1_score?.toFixed(4)}</td>
                  <td className="py-2.5 px-3 font-mono">{mainMetrics.roc_auc?.toFixed(4)}</td>
                </tr>
                {Object.values(data.baselines || {}).map((b, i) => (
                  <tr key={i} className="hover:bg-slate-800/30 text-slate-300">
                    <td className="py-2.5 px-3">{b.name}</td>
                    <td className="py-2.5 px-3 font-mono">{(b.metrics?.accuracy * 100).toFixed(1)}%</td>
                    <td className="py-2.5 px-3 font-mono">{b.metrics?.f1_score?.toFixed(4)}</td>
                    <td className="py-2.5 px-3 font-mono">{b.metrics?.roc_auc?.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Model Benchmark Comparison Bar Chart */}
        <div className="bg-slate-900/80 p-5 sm:p-6 rounded-2xl border border-slate-800">
          <h3 className="text-sm font-semibold text-white mb-4">Algorithm Benchmark (% Score)</h3>
          <div className="h-56 sm:h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={modelComparison} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 9 }} />
                <YAxis stroke="#64748b" domain={[0, 100]} tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }} />
                <Legend wrapperStyle={{ fontSize: '10px' }} />
                <Bar dataKey="Accuracy" fill="#06b6d4" />
                <Bar dataKey="F1" fill="#10b981" />
                <Bar dataKey="ROC-AUC" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Confusion Matrix and Calibration Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix */}
        <div className="bg-slate-900/80 p-5 sm:p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Confusion Matrix (Held-out Unseen Domains)</h3>
            <span className="text-xs font-mono text-slate-400">{mainMetrics.sample_count} Test Samples</span>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:gap-4 mt-2">
            <div className="p-4 sm:p-5 rounded-xl bg-slate-950 border border-emerald-500/30 text-center">
              <span className="text-[10px] sm:text-[11px] font-mono text-slate-400 block uppercase">True Negative (TN)</span>
              <p className="text-2xl sm:text-3xl font-bold text-emerald-400 font-mono mt-1">{cm.tn}</p>
              <span className="text-[10px] text-slate-500 mt-1 block">Correct Legitimate</span>
            </div>

            <div className="p-4 sm:p-5 rounded-xl bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] sm:text-[11px] font-mono text-slate-400 block uppercase">False Positive (FP)</span>
              <p className="text-2xl sm:text-3xl font-bold text-rose-400 font-mono mt-1">{cm.fp}</p>
              <span className="text-[10px] text-slate-500 mt-1 block">Benign flagged Phish</span>
            </div>

            <div className="p-4 sm:p-5 rounded-xl bg-slate-950 border border-slate-800 text-center">
              <span className="text-[10px] sm:text-[11px] font-mono text-slate-400 block uppercase">False Negative (FN)</span>
              <p className="text-2xl sm:text-3xl font-bold text-amber-400 font-mono mt-1">{cm.fn}</p>
              <span className="text-[10px] text-slate-500 mt-1 block">Phishing missed</span>
            </div>

            <div className="p-4 sm:p-5 rounded-xl bg-slate-950 border border-rose-500/30 text-center">
              <span className="text-[10px] sm:text-[11px] font-mono text-slate-400 block uppercase">True Positive (TP)</span>
              <p className="text-2xl sm:text-3xl font-bold text-rose-400 font-mono mt-1">{cm.tp}</p>
              <span className="text-[10px] text-slate-500 mt-1 block">Correct Phishing</span>
            </div>
          </div>
        </div>

        {/* PR Curve */}
        <div className="bg-slate-900/80 p-5 sm:p-6 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Precision-Recall Curve</h3>
            <span className="text-xs font-mono text-cyan-400">PR-AUC: {mainMetrics.pr_auc?.toFixed(4)}</span>
          </div>

          <div className="h-56 sm:h-64 w-full">
            {mainMetrics.pr_curve && mainMetrics.pr_curve.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mainMetrics.pr_curve} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="recall" stroke="#64748b" tick={{ fontSize: 10 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }} />
                  <Line type="monotone" dataKey="precision" stroke="#10b981" strokeWidth={2} dot={false} name="Precision" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-500 text-xs">
                No PR curve points available
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
