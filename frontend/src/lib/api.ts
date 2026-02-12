// frontend/src/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_LIFEAI_API_KEY;
const USER_ID = process.env.NEXT_PUBLIC_LIFEAI_USER_ID || 'local-dev';
const USER_ROLE = process.env.NEXT_PUBLIC_LIFEAI_USER_ROLE || 'developer';

export interface Model {
  id: string | number;
  name: string;
  description: string;
  governance_status: string;
  risk_level: 'Low' | 'Medium' | 'High';
  created_at: string;
  updated_at: string;
}

export interface ModelListItem {
  id: number;
  name: string;
  version: string;
  status: string;
  description?: string;
  repo_link?: string;
  created_at: string;
}

export interface ControlMapping {
  osfi_control: string;
  ai_rationale: string;
  status: 'Proposed' | 'Gap';
  confidence?: number;
}

export interface ModelAnalysis {
  model_id: number;
  documentation: string;
  control_mappings: ControlMapping[];
  status: string;
}

export interface ModelDetail extends Model {
  documentation: string;
  controls: ControlMapping[];
}

export interface DashboardMetrics {
  total_models: number;
  active_models: number;
  high_risk_models: number;
  open_gaps: number;
  controls_verified: number;
}

export interface DashboardAlert {
  id: string;
  title: string;
  model_name: string;
  severity: 'low' | 'medium' | 'high';
  created_at: string;
  details: string;
}

export interface DashboardModelStatus {
  id: string;
  name: string;
  status: string;
  risk_level: 'Low' | 'Medium' | 'High';
  controls_total: number;
  gaps: number;
  last_updated: string;
}

export interface DashboardSummary {
  generated_at: string;
  metrics: DashboardMetrics;
  recent_alerts: DashboardAlert[];
  model_status: DashboardModelStatus[];
}

// Generic API call function
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(API_KEY ? { 'x-api-key': API_KEY } : {}),
      'x-user-id': USER_ID,
      'x-user-role': USER_ROLE,
      ...options?.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

// Dashboard API functions
export const dashboardApi = {
  getMetrics: (): Promise<DashboardMetrics> => 
    apiCall<DashboardMetrics>('/dashboard/metrics'),

  getSummary: (): Promise<DashboardSummary> =>
    apiCall<DashboardSummary>('/dashboard/summary'),
  
  search: (query: string): Promise<any[]> =>
    apiCall<any[]>(`/dashboard/search?q=${encodeURIComponent(query)}`),
};

// Model API functions
export const modelApi = {
  getAll: (filters?: { risk?: string; status?: string; dateFrom?: string; dateTo?: string }): Promise<ModelListItem[]> => {
    const params = new URLSearchParams();
    if (filters?.risk) params.append('risk', filters.risk);
    if (filters?.status) params.append('status', filters.status.toLowerCase());
    if (filters?.dateFrom) params.append('dateFrom', filters.dateFrom);
    if (filters?.dateTo) params.append('dateTo', filters.dateTo);
    const query = params.toString() ? `?${params.toString()}` : '';
    return apiCall<ModelListItem[]>(`/api/models${query}`);
  },
  
  create: (data: { name: string; version: string; description?: string; repo_link?: string; status?: string }): Promise<ModelListItem> =>
    apiCall<ModelListItem>('/api/models', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getById: (id: string | number): Promise<ModelDetail> => 
    apiCall<ModelDetail>(`/api/models/${id}`),
  
  analyze: (id: string | number): Promise<ModelDetail> => 
    apiCall<ModelDetail>(`/api/models/${id}/analyze`, { method: 'POST' }),
  
  search: (query: string): Promise<ModelListItem[]> =>
    apiCall<ModelListItem[]>(`/api/models/search?q=${encodeURIComponent(query)}`),
};
