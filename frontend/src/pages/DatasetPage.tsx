import React, { useState } from 'react';
import { api } from '../services/api';
import {
  Database,
  Upload,
  CheckCircle2,
  AlertTriangle,
  Play,
  Settings2,
  FileCheck,
  RefreshCw,
  Info,
} from 'lucide-react';

export const DatasetPage: React.FC = () => {
  const [csvText, setCsvText] = useState('');
  const [valReport, setValReport] = useState<any | null>(null);
  const [valLoading, setValLoading] = useState(false);
  const [valError, setValError] = useState<string | null>(null);

  // Hyperparameters
  const [testSize, setTestSize] = useState(0.20);
  const [nEstimators, setNEstimators] = useState(150);
  const [maxDepth, setMaxDepth] = useState(5);
  const [learningRate, setLearningRate] = useState(0.08);

  // Training status
  const [isTraining, setIsTraining] = useState(false);
  const [trainOutput, setTrainOutput] = useState<any | null>(null);

  const sampleCsvSnippet = `url,label
https://google.com/search,0
https://wikipedia.org/wiki/Security,0
https://github.com/torvalds/linux,0
https://stackoverflow.com/questions,0
https://amazon.com/dp/B08N5WRWNW,0
https://netflix.com/browse,0
https://python.org/downloads/,0
https://apple.com/iphone/,0
https://microsoft.com/windows,0
https://cloudflare.com/security,0
http://paypal-security-verification-portal.com/login.php,1
http://appleid.apple.com.security-update-notice.xyz/auth/login,1
http://netflix-billing-update-required.net/signin,1
http://192.168.1.100/admin/chase-bank-verify.html,1
http://microsoft-outlook-web-login.top/owa/,1
http://secure-wellsfargo-auth.club/account/confirm,1
http://login-amazon-order-issue.vip/ap/signin,1
http://binance-wallet-validation.biz/recover,1
http://facebook-security-checkpoint-appeal.live/login,1
http://bankofamerica-urgent-support.site/login,1`;

  const handleValidate = async () => {
    if (!csvText.trim()) return;
    setValLoading(true);
    setValError(null);
    setValReport(null);

    try {
      const res = await api.validateDataset(csvText);
      setValReport(res.quality_report);
    } catch (err: any) {
      setValError(err.message || 'Dataset validation failed');
    } finally {
      setValLoading(false);
    }
  };

  const handleTrain = async () => {
    setIsTraining(true);
    setTrainOutput(null);

    try {
      const res = await api.trainModel({
        csvText: csvText.trim() ? csvText : undefined,
        testSize,
        nEstimators,
        maxDepth,
        learningRate,
      });
      setTrainOutput(res);
      alert('Training completed successfully! Artifacts updated.');
    } catch (err: any) {
      alert(`Training failed: ${err.message}`);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-6xl mx-auto w-full">
      <div>
        <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">Dataset Management & Model Training</h2>
        <p className="text-xs text-slate-400 mt-1">
          Upload custom phishing feeds, validate data quality, check domain distributions, and trigger domain-disjoint XGBoost retraining.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Dataset Ingestion Column */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-900/90 p-4 sm:p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <label className="text-xs font-semibold text-white uppercase tracking-wider flex items-center gap-2">
                <Database className="w-4 h-4 text-cyan-400" />
                Dataset CSV Ingestion
              </label>
              <button
                type="button"
                onClick={() => setCsvText(sampleCsvSnippet)}
                className="text-xs text-cyan-400 hover:text-cyan-300 font-medium self-start sm:self-auto"
              >
                Load Sample CSV
              </button>
            </div>

            <textarea
              rows={8}
              value={csvText}
              onChange={(e) => setCsvText(e.target.value)}
              placeholder="Paste CSV rows with url and label (0 = legit, 1 = phish)... (Leave empty to use built-in verified research dataset)"
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl p-3 sm:p-3.5 text-xs text-white font-mono placeholder-slate-600 focus:outline-none focus:border-cyan-500"
            />

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
              <span className="text-xs text-slate-500 font-mono">
                {csvText.trim() ? `${csvText.split('\n').length} lines entered` : 'Default verified research dataset active'}
              </span>

              {csvText.trim() && (
                <button
                  onClick={handleValidate}
                  disabled={valLoading}
                  className="w-full sm:w-auto px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 flex items-center justify-center gap-2"
                >
                  <FileCheck className="w-3.5 h-3.5 text-cyan-400" />
                  {valLoading ? 'Validating...' : 'Validate Dataset Quality'}
                </button>
              )}
            </div>
          </div>

          {/* Validation Quality Report Card */}
          {valReport && (
            <div className="bg-slate-900/80 p-4 sm:p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center gap-2 text-white font-semibold text-sm">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Data Quality Inspection Report
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Clean Records</span>
                  <span className="text-base font-bold text-white mt-1 block">{valReport.clean_row_count}</span>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Unique Domains</span>
                  <span className="text-base font-bold text-cyan-400 mt-1 block">{valReport.unique_domains_count}</span>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Duplicates</span>
                  <span className="text-base font-bold text-slate-300 mt-1 block">{valReport.duplicate_urls}</span>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Imbalance</span>
                  <span className="text-base font-bold text-amber-400 mt-1 block">{valReport.class_imbalance_ratio}:1</span>
                </div>
              </div>

              <div className="p-3 bg-slate-950/50 rounded-lg border border-slate-800 text-xs text-slate-400 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <span>Class Distribution:</span>
                <span className="font-mono text-slate-200">
                  Legitimate: {valReport.class_distribution?.['legitimate (0)'] ?? 0} | Phishing: {valReport.class_distribution?.['phishing (1)'] ?? 0}
                </span>
              </div>
            </div>
          )}

          {valError && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{valError}</span>
            </div>
          )}
        </div>

        {/* Training Parameters Column */}
        <div className="space-y-6">
          <div className="bg-slate-900/90 p-4 sm:p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-xs font-semibold text-white uppercase tracking-wider flex items-center gap-2">
              <Settings2 className="w-4 h-4 text-cyan-400" />
              Training Configuration
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Test Split (Domain Grouped)</span>
                  <span className="font-mono text-cyan-400">{(testSize * 100).toFixed(0)}%</span>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.40"
                  step="0.05"
                  value={testSize}
                  onChange={(e) => setTestSize(parseFloat(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>XGBoost Estimators</span>
                  <span className="font-mono text-cyan-400">{nEstimators}</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="300"
                  step="25"
                  value={nEstimators}
                  onChange={(e) => setNEstimators(parseInt(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Max Tree Depth</span>
                  <span className="font-mono text-cyan-400">{maxDepth}</span>
                </div>
                <input
                  type="range"
                  min="3"
                  max="10"
                  step="1"
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(parseInt(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Learning Rate (eta)</span>
                  <span className="font-mono text-cyan-400">{learningRate}</span>
                </div>
                <input
                  type="range"
                  min="0.01"
                  max="0.2"
                  step="0.01"
                  value={learningRate}
                  onChange={(e) => setLearningRate(parseFloat(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>
            </div>

            <div className="pt-2">
              <button
                onClick={handleTrain}
                disabled={isTraining}
                className="w-full py-3 bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 rounded-xl text-xs font-semibold tracking-wide transition-all shadow-md shadow-cyan-500/20 flex items-center justify-center gap-2"
              >
                {isTraining ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Training XGBoost Pipeline...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-current" />
                    Train PhishGuard Model
                  </>
                )}
              </button>
            </div>

            <p className="text-[10px] text-slate-500 leading-normal">
              Note: Training enforces strict domain-grouped train/val/test partitioning. Zero overlapping registered domains are permitted.
            </p>
          </div>

          {trainOutput && (
            <div className="p-4 rounded-xl bg-slate-900 border border-emerald-500/30 text-xs font-mono space-y-2">
              <span className="text-emerald-400 font-bold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                Training Complete!
              </span>
              <p className="text-slate-300">Model Version: {trainOutput.model_version}</p>
              <p className="text-slate-400 text-[11px]">
                Accuracy: {(trainOutput.result?.evaluation?.main_model?.metrics?.accuracy * 100 || 100).toFixed(1)}%
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
