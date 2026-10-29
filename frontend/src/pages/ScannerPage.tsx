import React, { useState } from 'react';
import { api } from '../services/api';
import { PredictionResult } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { ScoreGauge } from '../components/ScoreGauge';
import {
  Search,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Globe,
  Lock,
  Layers,
  ChevronDown,
  ChevronUp,
  Info,
  Clock,
  Sparkles,
  ArrowUpRight,
} from 'lucide-react';

interface Props {
  initialUrl?: string;
}

export const ScannerPage: React.FC<Props> = ({ initialUrl = '' }) => {
  const [url, setUrl] = useState(initialUrl);
  const [enableFetch, setEnableFetch] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const presets = [
    { label: 'Google Search', url: 'https://www.google.com/search?q=cybersecurity' },
    { label: 'PayPal Lure', url: 'http://paypal-security-verification-portal.com/login.php' },
    { label: 'Chase Bank IP', url: 'http://192.168.1.100/admin/chase-bank-verify.html' },
    { label: 'Netflix Lure', url: 'http://netflix-billing-update-required.net/signin' },
  ];

  const handleScan = async (targetUrl: string = url) => {
    if (!targetUrl.trim()) return;
    setError(null);
    setLoading(true);
    setResult(null);

    try {
      const data = await api.predictUrl(targetUrl.trim(), enableFetch);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'An error occurred during scanning.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-6xl mx-auto w-full">
      {/* Header */}
      <div>
        <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">Interactive URL Scanner</h2>
        <p className="text-xs text-slate-400 mt-1">
          Perform multi-layered feature inspection, XGBoost classification, and SHAP feature-attribution analysis on any submitted URL.
        </p>
      </div>

      {/* Input Box */}
      <div className="bg-slate-900/90 p-4 sm:p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleScan();
          }}
          className="flex flex-col sm:flex-row gap-3"
        >
          <div className="relative flex-1">
            <Globe className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter URL (e.g. https://domain.com/login)"
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-10 pr-4 py-3 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all font-mono"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="w-full sm:w-auto px-6 py-3 bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 rounded-xl text-xs sm:text-sm font-semibold tracking-wide transition-all shadow-md shadow-cyan-500/20 flex items-center justify-center gap-2 shrink-0"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Analyze URL
              </>
            )}
          </button>
        </form>

        {/* Controls and Presets */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-800/80">
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
            <span className="text-[11px] sm:text-xs text-slate-400 font-medium">Presets:</span>
            {presets.map((p) => (
              <button
                key={p.label}
                type="button"
                onClick={() => {
                  setUrl(p.url);
                  handleScan(p.url);
                }}
                className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700/80 rounded-md text-[10px] sm:text-[11px] font-mono text-cyan-300 border border-slate-700 transition-colors"
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* Webpage fetch toggle */}
          <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300 select-none">
            <input
              type="checkbox"
              checked={enableFetch}
              onChange={(e) => setEnableFetch(e.target.checked)}
              className="w-4 h-4 rounded bg-slate-950 border-slate-700 text-cyan-500 focus:ring-cyan-500"
            />
            <span className="flex items-center gap-1.5 text-[11px] sm:text-xs text-slate-300">
              <Lock className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              Safe Webpage Fetch (SSRF Guarded)
            </span>
          </label>
        </div>
      </div>

      {/* Error alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs sm:text-sm flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-rose-300">Scan Failed</h4>
            <p className="text-xs text-rose-400/90 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* Prediction Results */}
      {result && (
        <div className="space-y-6">
          {/* Main Assessment Header Card */}
          <div className="bg-slate-900/90 p-5 sm:p-6 rounded-2xl border border-slate-800 shadow-xl grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
            <div className="lg:col-span-2 space-y-3">
              <div className="flex items-center gap-3">
                <RiskBadge prediction={result.prediction} size="lg" />
                <span className="text-xs text-slate-500 font-mono">ID: #{result.prediction_id}</span>
              </div>

              <div>
                <h3 className="text-base sm:text-lg font-bold text-white font-mono break-all">{result.url}</h3>
                <p className="text-xs text-slate-400 mt-1 font-mono">
                  Registered Domain:{' '}
                  <span className="text-cyan-300 font-semibold">{result.registered_domain}</span>
                </p>
              </div>

              <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
                <p className="text-xs text-slate-300 font-medium">{result.risk_label}</p>
                <p className="text-[10px] sm:text-[11px] text-slate-500 mt-1">
                  Analysis Mode: {result.analysis_mode} | Model Version: {result.model_version}
                </p>
              </div>
            </div>

            <div className="w-full flex justify-center lg:justify-end">
              <ScoreGauge
                score={result.model_score ?? 0}
                label={result.calibrated_probability !== null ? 'Calibrated Probability' : 'Model Score'}
              />
            </div>
          </div>

          {/* Explainable AI: SHAP Breakdown & Insights */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Plain text observed evidence */}
            <div className="bg-slate-900/80 p-5 sm:p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center gap-2 text-white font-semibold text-sm">
                <Sparkles className="w-4 h-4 text-cyan-400 shrink-0" />
                Observable Risk Evidence
              </div>

              <div className="space-y-2">
                {result.explanation?.plain_text_insights &&
                result.explanation.plain_text_insights.length > 0 ? (
                  result.explanation.plain_text_insights.map((insight, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 text-xs text-slate-300 flex items-start gap-2.5"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0 mt-1.5" />
                      <span>{insight}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-500">No prominent risk flags observed.</p>
                )}
              </div>

              {result.explanation?.missing_features && result.explanation.missing_features.length > 0 && (
                <div className="p-3 bg-slate-950/40 rounded-xl border border-amber-500/20 text-xs text-amber-400/90 flex items-start gap-2">
                  <Info className="w-4 h-4 shrink-0 mt-0.5 text-amber-400" />
                  <span>{result.explanation.missing_features[0]}</span>
                </div>
              )}
            </div>

            {/* SHAP Feature Contribution Factors */}
            <div className="bg-slate-900/80 p-5 sm:p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between text-white font-semibold text-sm">
                <span className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400 shrink-0" />
                  Top Influential Features (SHAP)
                </span>
                <span className="text-[10px] text-slate-400 font-mono">TreeExplainer</span>
              </div>

              <div className="space-y-2.5">
                {/* Positive (Phishing) factors */}
                {result.explanation?.top_phishing_factors.map((f, idx) => (
                  <div key={`phish-${idx}`} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-mono text-slate-300 font-medium truncate max-w-[150px] sm:max-w-none">{f.feature_name}</span>
                      <span className="font-mono text-rose-400 shrink-0">+{f.shap_value.toFixed(3)} (Phish)</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-rose-500 h-1.5 rounded-full"
                        style={{ width: `${Math.min(100, Math.max(10, f.magnitude * 250))}%` }}
                      />
                    </div>
                    <p className="text-[10px] text-slate-500 leading-tight">{f.description}</p>
                  </div>
                ))}

                {/* Negative (Legitimate) factors */}
                {result.explanation?.top_legitimate_factors.map((f, idx) => (
                  <div key={`legit-${idx}`} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="font-mono text-slate-300 font-medium truncate max-w-[150px] sm:max-w-none">{f.feature_name}</span>
                      <span className="font-mono text-emerald-400 shrink-0">{f.shap_value.toFixed(3)} (Legit)</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-emerald-500 h-1.5 rounded-full"
                        style={{ width: `${Math.min(100, Math.max(10, f.magnitude * 250))}%` }}
                      />
                    </div>
                    <p className="text-[10px] text-slate-500 leading-tight">{f.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Research Disclaimer */}
          <div className="p-4 bg-slate-950/70 rounded-xl border border-slate-800 text-xs text-slate-400 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <p>
              <strong className="text-slate-300">Notice:</strong> {result.explanation?.disclaimer}
            </p>
            <span className="text-[10px] font-mono text-slate-500 shrink-0">Threshold: Legit &lt; 0.30 | Phish ≥ 0.70</span>
          </div>
        </div>
      )}
    </div>
  );
};
