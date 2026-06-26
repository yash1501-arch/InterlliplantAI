export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface DocumentMeta {
  id: string;
  name: string;
  status: string;
  size: number;
  preview: string;
  metadata: Record<string, unknown>;
}

export interface DocumentDetail extends DocumentMeta {
  text: string;
}

export interface UploadResponse {
  file_id: string;
  filename: string;
  size: number;
  content_type: string;
  status: string;
  message: string;
}

export interface ChatResponse {
  message: string;
  response: string;
  session_id: string;
  agents: Record<string, unknown>;
  context: Record<string, unknown>;
  routing: Record<string, unknown>;
  citations: ChatCitation[];
  fusion: Record<string, unknown>;
}

export interface ChatCitation {
  source: string;
  document_id: string;
  relevance_score: number;
  matched_entities?: string[];
  graph_relation?: string;
}

export interface SearchResult {
  document_id: string;
  text: string;
  score: number;
  matched_entities: string[];
  document_name: string;
}

export interface SearchResponse {
  results: SearchResult[];
}

export interface RCAResponse {
  analysis: string;
  root_causes: string[];
  recommendations: string[];
  confidence: number;
}

export interface ComplianceResponse {
  results: Record<string, unknown>;
  standards_checked: string[];
  gaps: string[];
  score: number;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface RecentDocument {
  name: string;
  size: number;
  status: string;
  uploaded_at: string;
}

export interface DashboardMetrics {
  documents: number;
  sessions: number;
  messages: number;
  equipment: number;
  recent_documents: RecentDocument[];
}

export interface HealthResponse {
  status: string;
}
