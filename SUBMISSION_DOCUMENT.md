# IntelliPlant AI - Submission Document
## AI-Powered Industrial Knowledge Intelligence Platform

**Team:** IntelliPlant AI  
**Event:** ET AI Hackathon 2026  
**Date:** June 26, 2026

---

## 1. Executive Summary

IntelliPlant AI is an AI-powered Industrial Knowledge Intelligence Platform that transforms fragmented industrial documents into a unified operational brain. The platform enables engineers, maintenance teams, and plant managers to access critical information through conversational AI, semantic search, knowledge graphs, and intelligent multi-agent systems.

**Tagline:** "Transform Documents into Industrial Intelligence."

---

## 2. Problem Statement

Industrial organizations operate with multiple disconnected systems containing engineering drawings, maintenance work orders, SOP documents, OEM manuals, incident reports, inspection records, and compliance documents. Engineers spend 30-60 minutes searching for information, leading to:

- Increased downtime
- Knowledge loss from expert retirement
- Poor decision making
- Compliance failures
- Repeated incidents

---

## 3. Solution Architecture

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, TypeScript, TailwindCSS 4 |
| Backend API | FastAPI (Python 3.13) |
| AI Orchestration | LangGraph (Stateful Multi-Agent Workflow) |
| LLM | Groq (Llama 3.3 70B) with OpenAI/Gemini fallback |
| Vector Database | Qdrant (Cloud) |
| Knowledge Graph | Neo4j (Cloud) |
| Embeddings | FastEmbed (BAAI/bge-small-en-v1.5) |
| Database | SQLite (demo) / PostgreSQL (production) |
| OCR | PyPDF, python-docx, Tesseract, Pillow |
| Deployment | Docker, Docker Compose |


### High-Level Architecture

```
Users (Engineers, Managers, Technicians)
            │
            ▼
┌─────────────────────────────┐
│    Next.js Frontend          │
│  Dashboard │ Chat │ Graph    │
│  Documents │ Analytics       │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    FastAPI Gateway            │
│  Auth │ Routing │ Validation │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    LangGraph Supervisor       │
│  Intent Detection             │
│  Agent Selection              │
│  Context Management           │
└──────┬──────┬──────┬────────┘
       │      │      │
       ▼      ▼      ▼
┌──────┐ ┌────┐ ┌──────────┐ ┌────────┐
│Expert│ │RCA │ │Compliance│ │Lessons │
│Agent │ │Agent│ │Agent     │ │Agent   │
└──┬───┘ └─┬──┘ └────┬─────┘ └───┬────┘
   │       │         │           │
   └───────┴─────────┴───────────┘
              │
              ▼
┌─────────────────────────────┐
│    Hybrid Retrieval Engine    │
│  40% Vector │ 40% Graph      │
│  20% BM25   │ Fusion         │
└──────┬──────┬──────┬────────┘
       │      │      │
       ▼      ▼      ▼
   Qdrant  Neo4j  SQLite/BM25
              │
              ▼
┌─────────────────────────────┐
│    LLM (Groq/OpenAI/Gemini)  │
│  Context-Grounded Response   │
│  Citation Generation         │
└─────────────────────────────┘
```

---

## 4. Key Features Implemented

### 4.1 Multi-Agent System (LangGraph)

A stateful LangGraph workflow with 7 orchestrated nodes:

1. **Input Node** — Query preprocessing + LLM-based query rewriting
2. **Supervisor Node** — Intent classification (maintenance, RCA, compliance, lessons, general)
3. **Retrieval Node** — Hybrid search across all data sources
4. **Agent Execution Node** — Parallel specialist agent execution
5. **Context Fusion Node** — Merge all context sources
6. **LLM Reasoning Node** — Generate grounded response with full context
7. **Citation Node** — Extract and attach source citations

### 4.2 Specialist Agents

| Agent | Capability |
|-------|-----------|
| Expert Copilot | Equipment SOPs, manuals, maintenance procedures |
| RCA Agent | 5-why analysis, failure patterns, root cause identification |
| Compliance Agent | OISD, ISO 9001, Factory Act, PESO regulatory checks |
| Lessons Learned | Historical incident patterns, near-miss analysis |

### 4.3 Hybrid Search (40/40/20 Formula)

- **Vector Search (40%)** — Semantic similarity via Qdrant + BGE embeddings
- **Graph Search (40%)** — Knowledge graph traversal via Neo4j
- **BM25 Search (20%)** — TF-IDF keyword matching with proper BM25 scoring
- Score normalization and weighted fusion for optimal results

### 4.4 Knowledge Graph

- **Node Types:** Equipment, Failure, Incident, Regulation, Personnel, Document
- **Relationship Types:** FAILED_IN, CAUSES, CONNECTED_TO, INSPECTED_BY, REQUIRES, SIMILAR_TO, LOCATED_IN
- Interactive force-directed visualization with drag, zoom, pan, and filtering
- Entity extraction from uploaded documents

### 4.5 Document Intelligence Pipeline

```
Upload → OCR → Text Extraction → Chunking (1024/200 overlap)
    → Embedding Generation → Qdrant Index
    → Entity Extraction → Relationship Extraction → Neo4j Graph
```

Supported formats: PDF, DOCX, XLSX, CSV, TXT, PNG, JPG, TIFF


### 4.6 Conversational AI with Citations

- Natural language Q&A powered by LangGraph workflow
- Real-time streaming responses (Server-Sent Events)
- Source citations with relevance scores attached to every response
- Confidence scoring based on evidence quality
- Session-based conversation history

### 4.7 Authentication & RBAC

- JWT-based authentication (access + refresh tokens)
- Role-based access control (Admin, Engineer, Viewer)
- bcrypt password hashing
- Configurable auth (enable/disable for demo)

### 4.8 Dashboard & Analytics

- Real-time metrics: documents, sessions, messages, equipment count
- Upload trend charts
- Agent usage distribution (pie chart)
- Document type breakdown
- System health monitoring panel

---

## 5. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User authentication |
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/documents/upload` | Document upload + full pipeline |
| GET | `/api/v1/documents` | List all documents |
| POST | `/api/v1/documents/reindex` | Reindex all docs to Qdrant |
| POST | `/api/v1/chat` | AI chat (LangGraph workflow) |
| POST | `/api/v1/search` | Hybrid search |
| POST | `/api/v1/rca` | Root cause analysis |
| POST | `/api/v1/compliance/check` | Compliance check |
| POST | `/api/v1/lessons` | Lessons learned |
| GET | `/api/v1/graph/{equipment_id}` | Knowledge graph |
| GET | `/api/v1/dashboard/metrics` | Dashboard metrics |
| GET | `/api/v1/dashboard/trends` | Upload trends |
| WS | `/ws/chat` | WebSocket real-time chat |

---

## 6. Demo Walkthrough (3-4 minutes)

### Scene 1: Dashboard (30 sec)
- Show the dashboard with live metrics (589 documents, 56 sessions, 469 messages)
- Point out the weekly activity chart and recent uploads

### Scene 2: Document Upload (30 sec)
- Upload a sample maintenance document
- Show the full pipeline: OCR → chunking → embedding → graph extraction
- Status changes from "processing" to "completed"

### Scene 3: AI Chat (60 sec)
- Ask: "Why do pumps fail?"
- Show the LangGraph response with:
  - Expert + RCA agents activated
  - Technical response grounded in uploaded documents
  - Citations with source documents listed
  - Confidence score (95%)
- Ask: "Are we compliant with OISD standards?"
  - Compliance agent activated
  - Regulatory analysis response

### Scene 4: Knowledge Graph (30 sec)
- Search for "pump"
- Show interactive force-directed graph visualization
- Click nodes to see connections
- Filter by node type (Equipment, Failure, Regulation)

### Scene 5: Analytics (30 sec)
- Show analytics page with charts
- Agent usage distribution
- System health panel

---

## 7. Innovation Highlights

1. **LangGraph Orchestration** — Not just prompt chaining; a stateful graph workflow with conditional routing, parallel execution, and error recovery
2. **Triple Hybrid Search** — Industry-specified 40/40/20 formula combining vector, graph, and keyword search
3. **Query Rewriting** — LLM automatically rewrites queries for better retrieval before searching
4. **Citation-First AI** — Every response includes traceable source documents with relevance scores
5. **Industrial Domain Ontology** — Purpose-built entity/relationship extraction for plant equipment, failures, and regulations

---

## 8. Business Impact

| Metric | Before | After |
|--------|--------|-------|
| Information retrieval time | 30-60 min | < 20 seconds |
| Knowledge preserved | Tribal/informal | Structured graph |
| Compliance gap detection | Manual audits | Automated AI |
| Incident pattern recognition | Reactive | Proactive |
| Engineer productivity | Low | High |

---

## 9. How to Run

```bash
# Backend
cd backend
pip install -r requirements.txt
python run.py  # Starts on port 8000

# Frontend
cd frontend
npm install
npm run dev   # Starts on port 3000

# Docker (full stack)
docker-compose up
```

---

## 10. Team

**Team IntelliPlant AI** — ET AI Hackathon 2026

---

## 11. Future Roadmap

- Celery background workers for async OCR processing
- BAAI BGE-Reranker-v2 for result quality improvement
- Multi-hop graph reasoning (2-3 hop traversal)
- Redis-based conversation memory
- Document auto-classification (Manual, SOP, Incident Report)
- Mobile-responsive field technician interface
- Real-time SCADA/IoT integration
