import type {
  DashboardMetrics,
  UploadResponse,
  DocumentMeta,
  DocumentDetail,
  ChatResponse,
  SearchResponse,
  GraphData,
  AuthResponse,
  User,
  HealthResponse,
  ComplianceResponse,
  RCAResponse,
} from '@/app/types';

const API_BASE = 'http://localhost:8000/api/v1';

function getAuthHeaders(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // ignore parse error
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function fetchMetrics(): Promise<DashboardMetrics> {
  const res = await fetch(`${API_BASE}/dashboard/metrics`, { headers: getAuthHeaders() });
  return handleResponse<DashboardMetrics>(res);
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const headers: Record<string, string> = {};
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}/documents/upload`, { method: 'POST', headers, body: formData });
  return handleResponse<UploadResponse>(res);
}

export async function listDocuments(): Promise<DocumentMeta[]> {
  const res = await fetch(`${API_BASE}/documents`, { headers: getAuthHeaders() });
  return handleResponse<DocumentMeta[]>(res);
}

export async function getDocument(id: string): Promise<DocumentDetail> {
  const res = await fetch(`${API_BASE}/documents/${id}`, { headers: getAuthHeaders() });
  return handleResponse<DocumentDetail>(res);
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: 'DELETE', headers: getAuthHeaders() });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
}

export async function sendChatMessage(message: string, sessionId?: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  return handleResponse<ChatResponse>(res);
}

export async function searchDocuments(query: string): Promise<SearchResponse> {
  const res = await fetch(`${API_BASE}/search`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ query }),
  });
  return handleResponse<SearchResponse>(res);
}

export async function getGraphData(equipmentId: string): Promise<GraphData> {
  const res = await fetch(`${API_BASE}/graph/${equipmentId}`, { headers: getAuthHeaders() });
  return handleResponse<GraphData>(res);
}

export async function loginApi(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse<AuthResponse>(res);
}

export async function registerApi(name: string, email: string, password: string): Promise<User> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  });
  return handleResponse<User>(res);
}

export async function rcaAnalysis(equipment: string): Promise<RCAResponse> {
  const res = await fetch(`${API_BASE}/rca`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ equipment }),
  });
  return handleResponse<RCAResponse>(res);
}

export async function complianceCheck(documentId?: string, query?: string): Promise<ComplianceResponse> {
  const res = await fetch(`${API_BASE}/compliance/check`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ document_id: documentId, query }),
  });
  return handleResponse<ComplianceResponse>(res);
}

export async function lessonsLearned(equipment?: string, query?: string): Promise<{ patterns: string[]; recommendations: string[] }> {
  const res = await fetch(`${API_BASE}/lessons`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ equipment, query }),
  });
  return handleResponse<{ patterns: string[]; recommendations: string[] }>(res);
}

export async function fetchTrends(days: number = 30): Promise<{ date: string; documents: number }[]> {
  const res = await fetch(`${API_BASE}/dashboard/trends?days=${days}`, { headers: getAuthHeaders() });
  return handleResponse<{ date: string; documents: number }[]>(res);
}

export async function healthCheck(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  return handleResponse<HealthResponse>(res);
}
