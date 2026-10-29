import React, { useState } from 'react';
import { api } from '../services/api';
import { RiskBadge } from '../components/RiskBadge';
import {
  Layers,
  Upload,
  Download,
  FileSpreadsheet,
  AlertCircle,
  CheckCircle2,
  Filter,
} from 'lucide-react';

export const BatchPage: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any | null>(null);
  const [filter, setFilter] = useState<'All' | 'Phishing' | 'Legitimate' | 'Suspicious'>('All');
  const [search, setSearch] = useState('');

  const sampleBatch = `https://google.com/search?q=test
http://paypal-security-verification-portal.com/login.php
https://en.wikipedia.org/wiki/Machine_learning
http://netflix-billing-update-required.net/signin
https://github.com/torvalds/linux
http://192.168.1.100/admin/chase-bank-verify.html`;

  const handleRunBatch = async () => {
    const urls = inputText
      .split('\n')
      .map((l) => l.trim())
      .filter((l) => l.length > 0);

    if (urls.length === 0) return;

    setLoading(true);
    setResults(null);
    try {
      const data = await api.predictBatch(urls, false);
      setResults(data);
    } catch (err: any) {
      alert(err.message || 'Batch analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (!results || !results.items) return;
    const header = ['URL', 'Registered Domain', 'Prediction', 'Risk Score', 'Analysis Mode'];
    const rows = results.items.map((item: any) => [
      `"${item.url || ''}"`,
      `"${item.registered_domain || ''}"`,
      `"${item.prediction || 'Error'}"`,
      item.model_score !== undefined ? item.model_score : '',
      `"${item.analysis_mode || ''}"`,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [header.join(','), ...rows.map((e: any[]) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `phishguard_batch_results_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredItems = (results?.items || []).filter((item: any) => {
    if (filter === 'Phishing' && item.prediction !== 'Phishing') return false;
    if (filter === 'Legitimate' && item.prediction !== 'Legitimate') return false;
    if (filter === 'Suspicious' && !item.prediction?.includes('Suspicious')) return false;
    if (search && !item.url?.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-6xl mx-auto w-full">
      <div>
        <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">Batch URL Analysis</h2>
        <p className="text-xs text-slate-400 mt-1">
          Submit batches of URLs for bulk security screening, risk scoring, and exported forensic reporting.
        </p>
      </div>

      {/* Input panel */}
      <div className="bg-slate-900/90 p-4 sm:p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4 text-cyan-400" />
            Enter URLs (One per line, up to 500 URLs)
          </label>
          <button
            type="button"
            onClick={() => setInputText(sampleBatch)}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium self-start sm:self-auto"
          >
            Insert Sample Batch
          </button>
        </div>

        <textarea
          rows={6}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="https://example.com/login&#10;http://suspicious-portal.xyz/verify&#10;https://another-domain.org"
          className="w-full bg-slate-950 border border-slate-700/80 rounded-xl p-3 sm:p-3.5 text-xs text-white font-mono placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
        />

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
          <span className="text-xs text-slate-400 font-mono">
            {inputText.split('\n').filter((l) => l.trim().length > 0).length} URLs queued
          </span>

          <button
            onClick={handleRunBatch}
            disabled={loading || !inputText.trim()}
            className="w-full sm:w-auto px-6 py-2.5 bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 rounded-xl text-xs font-semibold tracking-wide transition-all shadow-md shadow-cyan-500/20 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                Processing Batch...
              </>
            ) : (
              <>
                <Layers className="w-4 h-4" />
                Analyze Batch
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {results && (
        <div className="space-y-6">
          {/* Summary metrics: 2x2 on mobile, 4 in row on desktop */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
            <div className="bg-slate-900/80 p-3.5 sm:p-4 rounded-xl border border-slate-800">
              <span className="text-[11px] sm:text-xs text-slate-400">Total Scanned</span>
              <p className="text-xl sm:text-2xl font-bold text-white font-mono mt-1">{results.total_processed}</p>
            </div>
            <div className="bg-slate-900/80 p-3.5 sm:p-4 rounded-xl border border-slate-800">
              <span className="text-[11px] sm:text-xs text-rose-400 font-medium">Phishing</span>
              <p className="text-xl sm:text-2xl font-bold text-rose-400 font-mono mt-1">
                {results.summary_counts?.Phishing ?? 0}
              </p>
            </div>
            <div className="bg-slate-900/80 p-3.5 sm:p-4 rounded-xl border border-slate-800">
              <span className="text-[11px] sm:text-xs text-emerald-400 font-medium">Legitimate</span>
              <p className="text-xl sm:text-2xl font-bold text-emerald-400 font-mono mt-1">
                {results.summary_counts?.Legitimate ?? 0}
              </p>
            </div>
            <div className="bg-slate-900/80 p-3.5 sm:p-4 rounded-xl border border-slate-800">
              <span className="text-[11px] sm:text-xs text-amber-400 font-medium">Uncertain</span>
              <p className="text-xl sm:text-2xl font-bold text-amber-400 font-mono mt-1">
                {results.summary_counts?.['Suspicious / Uncertain'] ?? 0}
              </p>
            </div>
          </div>

          {/* Filtering and download controls */}
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

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
              <input
                type="text"
                placeholder="Filter results..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
              />

              <button
                onClick={downloadCSV}
                className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium flex items-center justify-center gap-2 border border-slate-700 transition-colors shrink-0"
              >
                <Download className="w-3.5 h-3.5" />
                Export CSV
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="bg-slate-900/80 rounded-2xl border border-slate-800 overflow-hidden">
            <div className="overflow-x-auto -mx-2 sm:mx-0">
              <table className="w-full text-left text-xs min-w-[550px]">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px] bg-slate-950/40">
                    <th className="py-3 px-4">URL</th>
                    <th className="py-3 px-4">Domain</th>
                    <th className="py-3 px-4">Decision</th>
                    <th className="py-3 px-4">Score</th>
                    <th className="py-3 px-4">Top Evidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-sans">
                  {filteredItems.map((item: any, i: number) => (
                    <tr key={i} className="hover:bg-slate-800/30">
                      <td className="py-3 px-4 max-w-xs truncate font-mono text-slate-300" title={item.url}>
                        {item.url}
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-400">{item.registered_domain || '—'}</td>
                      <td className="py-3 px-4">
                        <RiskBadge prediction={item.prediction} size="sm" />
                      </td>
                      <td className="py-3 px-4 font-mono font-medium">
                        {item.model_score !== undefined ? `${(item.model_score * 100).toFixed(1)}%` : '—'}
                      </td>
                      <td className="py-3 px-4 text-slate-400 text-[11px] truncate max-w-xs">
                        {item.explanation?.plain_text_insights?.[0] || '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
