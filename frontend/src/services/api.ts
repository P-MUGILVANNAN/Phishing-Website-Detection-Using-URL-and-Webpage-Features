import { HealthInfo, PredictionResult, DashboardSummary, EvaluationData } from '../types';

const API_BASE = '/api';

export const api = {
  async getHealth(): Promise<HealthInfo> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to fetch system health');
    return res.json();
  },

  async predictUrl(url: string, enableFetch: boolean = false): Promise<PredictionResult> {
    const res = await fetch(`${API_BASE}/predict/url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, enable_fetch: enableFetch }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Prediction failed' }));
      throw new Error(err.detail || 'Prediction failed');
    }
    return res.json();
  },

  async predictBatch(urls: string[], enableFetch: boolean = false): Promise<any> {
    const res = await fetch(`${API_BASE}/predict/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls, enable_fetch: enableFetch }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Batch failed' }));
      throw new Error(err.detail || 'Batch analysis failed');
    }
    return res.json();
  },

  async getDashboardSummary(): Promise<DashboardSummary> {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    if (!res.ok) throw new Error('Failed to load dashboard summary');
    return res.json();
  },

  async getEvaluation(): Promise<EvaluationData> {
    const res = await fetch(`${API_BASE}/model/evaluation`);
    if (!res.ok) throw new Error('Failed to fetch evaluation metrics');
    return res.json();
  },

  async getFeatureImportance(): Promise<any> {
    const res = await fetch(`${API_BASE}/model/feature-importance`);
    if (!res.ok) throw new Error('Failed to load feature importances');
    return res.json();
  },

  async getPredictions(limit: number = 50, offset: number = 0): Promise<any[]> {
    const res = await fetch(`${API_BASE}/predictions?limit=${limit}&offset=${offset}`);
    if (!res.ok) throw new Error('Failed to fetch prediction history');
    return res.json();
  },

  async getPredictionReport(predictionId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/reports/${predictionId}`);
    if (!res.ok) throw new Error('Failed to fetch report');
    return res.json();
  },

  async validateDataset(csvText: string): Promise<any> {
    const res = await fetch(`${API_BASE}/datasets/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ csv_text: csvText }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Validation failed' }));
      throw new Error(err.detail || 'Dataset validation failed');
    }
    return res.json();
  },

  async trainModel(params: {
    csvText?: string;
    testSize?: number;
    nEstimators?: number;
    maxDepth?: number;
    learningRate?: number;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/model/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        csv_text: params.csvText || null,
        test_size: params.testSize ?? 0.20,
        n_estimators: params.nEstimators ?? 150,
        max_depth: params.maxDepth ?? 5,
        learning_rate: params.learningRate ?? 0.08,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Training failed' }));
      throw new Error(err.detail || 'Model training failed');
    }
    return res.json();
  },

  async getTrainingStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/model/training-status`);
    if (!res.ok) throw new Error('Failed to fetch training status');
    return res.json();
  },
};

