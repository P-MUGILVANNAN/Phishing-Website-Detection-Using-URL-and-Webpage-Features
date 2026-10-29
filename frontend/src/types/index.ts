export interface HealthInfo {
  status: string;
  app_name: string;
  version: string;
  database_connected: boolean;
  model_loaded: boolean;
  model_version: string | null;
  webpage_fetch_enabled: boolean;
}

export interface FeatureFactor {
  feature_name: string;
  description: string;
  observed_value: number;
  shap_value: number;
  impact: 'phishing' | 'legitimate';
  magnitude: number;
}

export interface ExplanationData {
  prediction: string;
  model_score: number;
  risk_label: string;
  top_phishing_factors: FeatureFactor[];
  top_legitimate_factors: FeatureFactor[];
  plain_text_insights: string[];
  missing_features: string[];
  disclaimer: string;
}

export interface PredictionResult {
  is_success: boolean;
  prediction_id?: number;
  url: string;
  normalized_url?: string;
  registered_domain?: string;
  prediction?: 'Legitimate' | 'Phishing' | 'Suspicious / Uncertain';
  model_score?: number;
  risk_label?: string;
  risk_level?: 'low' | 'medium' | 'high';
  calibrated_probability?: number | null;
  thresholds?: {
    legitimate: number;
    phishing: number;
  };
  analysis_mode?: string;
  webpage_fetch?: {
    status: string;
    status_code?: number | null;
    error?: string | null;
  };
  explanation?: ExplanationData;
  features_summary?: Record<string, any>;
  model_version?: string;
  error?: string;
}

export interface DashboardSummary {
  total_analyzed: number;
  phishing_count: number;
  legitimate_count: number;
  uncertain_count: number;
  recent_predictions: Array<{
    id: number;
    submitted_url: string;
    normalized_domain: string;
    prediction: string;
    model_score: number;
    analysis_mode: string;
    created_at: string;
  }>;
  model_status: string;
  model_version: string | null;
  evaluation_summary?: {
    accuracy: number;
    precision: number;
    recall: number;
    specificity: number;
    f1_score: number;
    roc_auc: number;
    pr_auc: number;
    false_positive_rate: number;
    false_negative_rate: number;
    brier_score: number;
    latency_ms: number;
    confusion_matrix: {
      tn: number;
      fp: number;
      fn: number;
      tp: number;
    };
    roc_curve: Array<{ fpr: number; tpr: number }>;
    pr_curve: Array<{ recall: number; precision: number }>;
    calibration_curve: Array<{ prob_pred: number; prob_true: number }>;
  };
  generalization_gap?: {
    domain_grouped_unseen: {
      accuracy: number;
      f1_score: number;
      roc_auc: number;
      domain_overlap: number;
    };
    random_split_leakage: {
      accuracy: number;
      f1_score: number;
      roc_auc: number;
      domain_overlap: number;
    };
    generalization_gap_f1: number;
  };
}

export interface EvaluationData {
  model_version: string;
  evaluated_at: string;
  evaluation_protocol: string;
  domain_leakage_overlap: number;
  main_model: {
    name: string;
    metrics: any;
  };
  baselines: Record<string, {
    name: string;
    metrics: any;
  }>;
  generalization_comparison: {
    domain_grouped_unseen: any;
    random_split_leakage: any;
    generalization_gap_f1: number;
  };
  feature_importance: Record<string, number>;
  shap_importance: Record<string, number>;
}

