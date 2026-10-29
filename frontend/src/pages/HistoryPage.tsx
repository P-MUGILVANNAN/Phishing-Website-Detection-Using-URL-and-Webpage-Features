import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { RiskBadge } from '../components/RiskBadge';
import {
  History,
  Search,
  Filter,
  Download,
  Eye,
  X,
  FileText,
  Clock,
  Globe,
  Layers,
} from 'lucide-react';

export const HistoryPage: React.FC = () => {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'All' | 'Phishing' | 'Legitimate' | 'Suspicious'>('All');
  const [selectedReport, setSelectedReport] = useState<any | null>(null);
  const [reportLoading, setReportLoading] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await api.getPredictions(100);
      setPredictions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewReport = async (id: number) => {
    try {
      setReportLoading(true);
      const rep = await api.getPredictionReport(id);
      setSelectedReport(rep);
    } catch (err) {
      console.error(err);
    } finally {
      setReportLoading(false);
    }
  };

  const filtered = predictions.filter((p) => {
    if (filter === 'Phishing' && p.prediction !== 'Phishing') return false;
    if (filter === 'Legitimate' && p.prediction !== 'Legitimate') return false;
    if (filter === 'Suspicious' && !p.prediction?.includes('Suspicious')) return false;
    if (search && !p.submitted_url.toLowerCase().includes(search.toLowerCase()) && !p.normalized_domain.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-7xl mx-auto w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">Prediction History & Forensic Logs</h2>
          <p className="text-xs text-slate-400 mt-1">
            Persisted history of inspected URLs, model scores, decision thresholds, and SHAP explainability records.
          </p>
        </div>

        <button
          onClick={loadHistory}
          className="self-start sm:self-auto px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-lg text-xs font-medium border border-slate-800 transition-colors shrink-0"
        >
          Refresh Logs
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
          {(['All', 'Phishing', 'Legitimate', 'Suspicious'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                filter === tab
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                  : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-80">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search URL or domain..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto -mx-2 sm:mx-0">
          <table className="w-full text-left text-xs min-w-[650px]">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px] bg-slate-950/40">
                <th className="py-3 px-4">ID</th>
                <th className="py-3 px-4">Submitted URL</th>
                <th className="py-3 px-4">Domain</th>
                <th className="py-3 px-4">Prediction</th>
                <th className="py-3 px-4">Model Score</th>
                <th className="py-3 px-4">Mode</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4 text-right">Audit Report</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {filtered.length > 0 ? (
                filtered.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4 font-mono text-slate-500">#{p.id}</td>
                    <td className="py-3 px-4 max-w-xs truncate font-mono text-slate-300" title={p.submitted_url}>
                      {p.submitted_url}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-400">{p.normalized_domain}</td>
                    <td className="py-3 px-4">
                      <RiskBadge prediction={p.prediction} size="sm" />
                    </td>
                    <td className="py-3 px-4 font-mono font-medium">
                      {(p.model_score * 100).toFixed(1)}%
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px] whitespace-nowrap">{p.analysis_mode}</td>
                    <td className="py-3 px-4 text-slate-500 font-mono text-[11px] whitespace-nowrap">
                      {new Date(p.created_at).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleViewReport(p.id)}
                        className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-md font-medium text-[11px] inline-flex items-center gap-1.5 transition-colors border border-slate-700"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-slate-500 text-xs">
                    {loading ? 'Loading prediction history...' : 'No matching prediction history records.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedReport && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-4 sm:p-6 space-y-5 sm:space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-cyan-400 shrink-0" />
                <h3 className="text-sm sm:text-base font-bold text-white font-mono">{selectedReport.report_id}</h3>
              </div>
              <button
                onClick={() => setSelectedReport(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs font-mono">
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-400 text-[10px] uppercase">Target URL</span>
                <p className="text-white break-all">{selectedReport.analyzed_target?.submitted_url}</p>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-slate-400 text-[11px] pt-1">
                  <span>Domain: {selectedReport.analyzed_target?.registered_domain}</span>
                  <span>Mode: {selectedReport.analyzed_target?.analysis_mode}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                  <span className="text-slate-400 text-[10px] uppercase">Prediction</span>
                  <div className="mt-1">
                    <RiskBadge prediction={selectedReport.model_assessment?.prediction} size="md" />
                  </div>
                </div>
                <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                  <span className="text-slate-400 text-[10px] uppercase">Model Score</span>
                  <p className="text-lg font-bold text-white mt-1">
                    {((selectedReport.model_assessment?.risk_score || 0) * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Insights */}
              <div className="space-y-2">
                <span className="text-slate-400 text-[10px] uppercase">Observed Risk Evidence</span>
                {selectedReport.explainable_evidence?.plain_text_insights?.map((ins: string, idx: number) => (
                  <div key={idx} className="p-2.5 bg-slate-950 rounded-lg text-slate-300 text-xs">
                    • {ins}
                  </div>
                ))}
              </div>

              {/* Disclaimer */}
              <div className="p-3 bg-slate-950 rounded-lg text-[10px] text-slate-500">
                {selectedReport.disclaimer}
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2 border-t border-slate-800">
              <button
                onClick={() => setSelectedReport(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
