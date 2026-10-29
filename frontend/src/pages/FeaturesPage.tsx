import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Cpu, Search, Layers, Sparkles, HelpCircle } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export const FeaturesPage: React.FC = () => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<'All' | 'URL' | 'Webpage' | 'NLP'>('All');

  useEffect(() => {
    loadFeatures();
  }, []);

  const loadFeatures = async () => {
    try {
      setLoading(true);
      const res = await api.getFeatureImportance();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const featImportances = data?.feature_importance || {};
  const descriptions = data?.descriptions || {};

  const topChartData = Object.entries(featImportances)
    .sort((a: any, b: any) => b[1] - a[1])
    .slice(0, 10)
    .map(([name, score]) => ({
      name,
      Importance: Math.round((score as number) * 1000) / 1000,
    }));

  const allFeaturesList = Object.entries(descriptions).map(([name, desc]) => {
    const isUrl = [
      'url_length',
      'hostname_length',
      'registered_domain_length',
      'path_length',
      'query_length',
      'count_dots',
      'count_hyphens',
      'count_underscores',
      'count_slashes',
      'count_question_marks',
      'count_equals',
      'count_ampersands',
      'count_percent',
      'count_digits',
      'digit_ratio',
      'subdomain_depth',
      'num_parameters',
      'num_path_segments',
      'suspicious_punctuation_count',
      'has_ip_hostname',
      'has_at_symbol',
      'has_nonstandard_port',
      'has_fragment',
      'is_https',
      'is_punycode',
      'has_encoded_chars',
      'has_suspicious_words_hostname',
      'suspicious_words_count',
      'has_brand_in_subdomain',
      'brand_in_subdomain_count',
      'hostname_entropy',
      'path_entropy',
    ].includes(name);

    const isNLP = [
      'login_keyword_freq',
      'verify_keyword_freq',
      'pw_reset_keyword_freq',
      'financial_keyword_freq',
      'urgency_keyword_freq',
      'brand_impersonation_count',
      'title_domain_mismatch',
    ].includes(name);

    let cat: 'URL' | 'Webpage' | 'NLP' = 'Webpage';
    if (isUrl) cat = 'URL';
    else if (isNLP) cat = 'NLP';

    return {
      name,
      description: desc as string,
      category: cat,
      importance: featImportances[name] ?? 0.0,
      shap: data?.shap_importance?.[name] ?? 0.0,
    };
  });

  const filteredFeatures = allFeaturesList.filter((f) => {
    if (category !== 'All' && f.category !== category) return false;
    if (search && !f.name.toLowerCase().includes(search.toLowerCase()) && !f.description.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 max-w-7xl mx-auto w-full">
      <div>
        <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">Feature Importance & Model Interpretability</h2>
        <p className="text-xs text-slate-400 mt-1">
          Detailed inspection of the 52 multi-modal URL lexical, structural, and webpage NLP features driving the XGBoost classifier.
        </p>
      </div>

      {/* Top 10 Feature Importance Chart */}
      <div className="bg-slate-900/80 p-4 sm:p-6 rounded-2xl border border-slate-800">
        <h3 className="text-sm font-semibold text-white mb-1">Top 10 Influential Features (XGBoost Gain)</h3>
        <p className="text-xs text-slate-400 mb-4">Empirical split-criterion contribution across all trees</p>

        <div className="h-60 sm:h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={topChartData} layout="vertical" margin={{ top: 5, right: 15, left: 110, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" stroke="#64748b" tick={{ fontSize: 9 }} />
              <YAxis dataKey="name" type="category" stroke="#94a3b8" tick={{ fontSize: 9, fontFamily: 'monospace' }} width={105} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }} />
              <Bar dataKey="Importance" fill="#06b6d4" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Feature Catalog & Explanations */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
            {(['All', 'URL', 'Webpage', 'NLP'] as const).map((cat) => (
              <button
                key={cat}
                onClick={() => setCategory(cat)}
                className={`px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  category === cat
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                    : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                }`}
              >
                {cat} Features
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search features..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {filteredFeatures.map((f) => (
            <div key={f.name} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-xs font-semibold text-cyan-300 truncate">{f.name}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 shrink-0">
                    {f.category}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">{f.description}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
                <span>Gain: {f.importance ? f.importance.toFixed(4) : '0.0000'}</span>
                <span>SHAP: {f.shap ? f.shap.toFixed(4) : '0.0000'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
