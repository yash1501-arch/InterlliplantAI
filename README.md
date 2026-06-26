<p align="center">
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Groq-Llama_3.3_70B-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Qdrant-Vector_DB-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Neo4j-Knowledge_Graph-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Next.js_16-Frontend-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge" />
</p>

<h1 align="center">🏭 IntelliPlant AI</h1>
<h3 align="center">AI-Powered Industrial Knowledge Intelligence Platform</h3>
<p align="center"><em>"Transform Documents into Industrial Intelligence"</em></p>

<p align="center">
  <strong>ET AI Hackathon 2026</strong> · Built by <strong>Narayan Parab</strong>
</p>

---

## 🎯 What is IntelliPlant AI?

IntelliPlant AI transforms **fragmented industrial documents** (maintenance manuals, SOPs, incident reports, inspection records, compliance docs) into a **unified AI-powered knowledge brain** — reducing information retrieval from **60 minutes to 20 seconds**.

Engineers, maintenance teams, and plant managers can query the system in natural language and receive **grounded, cited responses** from specialized AI agents.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **Multi-Agent System** | LangGraph-powered Supervisor + 4 specialist agents (Expert, RCA, Compliance, Lessons) |
| 🔍 **Hybrid Search** | 40% Vector + 40% Graph + 20% BM25 with weighted score fusion |
| 🕸️ **Knowledge Graph** | Interactive Neo4j graph with Equipment, Failures, Incidents, Regulations |
| 📄 **Document Pipeline** | Upload → OCR → Chunk → Embed → Index → Graph Build (automatic) |
| 💬 **AI Chat with Citations** | Every response includes source documents and confidence scores |
| 📊 **Analytics Dashboard** | Real-time metrics, agent usage, upload trends, system health |
| 🔐 **Auth & RBAC** | JWT authentication with Admin/Engineer/Viewer roles |
| ⚡ **Query Rewriting** | LLM automatically rewrites queries for better retrieval |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│               Frontend (Next.js 16)                  │
│     Dashboard │ Chat │ Graph │ Documents │ Analytics │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              API Gateway (FastAPI)                    │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           LangGraph Workflow (7 Nodes)                │
│                                                      │
│  Input → Supervisor → Retrieval → Agents →           │
│  Fusion → LLM Reasoning → Citations                  │
└──────┬────────────┬────────────┬────────────────────┘
       │            │            │
       ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │ Qdrant │  │ Neo4j  │  │ SQLite │
   │Vectors │  │ Graph  │  │Metadata│
   └────────┘  └────────┘  └────────┘
```


---

## 🤖 AI Agent System

The platform uses **5 specialized agents** orchestrated via LangGraph:

| Agent | Role | Handles |
|-------|------|---------|
| **Supervisor** | Intent Detection & Routing | Classifies queries and activates relevant agents |
| **Expert Copilot** | Equipment Intelligence | SOPs, maintenance procedures, troubleshooting |
| **RCA Agent** | Root Cause Analysis | 5-why methodology, failure patterns, recommendations |
| **Compliance Agent** | Regulatory Audit | OISD, ISO 9001, Factory Act, PESO checks |
| **Lessons Agent** | Pattern Intelligence | Historical incidents, near-misses, recurring failures |

### LangGraph Workflow (7 Nodes)

```
User Query → Input (Query Rewriter) → Supervisor (Intent Classification)
    → Hybrid Retrieval (Vector + Graph + BM25)
    → Agent Execution (Parallel specialists)
    → Context Fusion (Merge all sources)
    → LLM Reasoning (Groq Llama 3.3 70B)
    → Citation Generation → Response
```

---

## 🔍 Hybrid Search Engine

Three search methods combined with weighted scoring:

```
Final Score = 0.4 × Vector Score (Qdrant)
            + 0.4 × Graph Score (Neo4j)
            + 0.2 × BM25 Score (Keyword)
```

| Method | Technology | Finds |
|--------|-----------|-------|
| **Vector Search** | Qdrant + BGE Embeddings | Semantically similar content |
| **Graph Search** | Neo4j Traversal | Related entities via relationships |
| **BM25 Search** | TF-IDF Scoring | Exact keyword matches |

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 16, React 19, TailwindCSS 4 | UI with SSR and interactive visualizations |
| Backend | FastAPI (Python 3.13) | REST API with async support |
| AI Orchestration | LangGraph | Stateful multi-agent workflow |
| LLM | Groq (Llama 3.3 70B) | Real-time language reasoning |
| Vector DB | Qdrant (Cloud) | Semantic embedding storage & search |
| Graph DB | Neo4j (AuraDB Cloud) | Knowledge graph relationships |
| Embeddings | FastEmbed (BAAI/bge-small-en-v1.5) | Local text-to-vector conversion |
| Database | SQLite (demo) / PostgreSQL (prod) | Users, documents, sessions |
| OCR | PyPDF, python-docx, Tesseract | Text extraction from documents |
| Deployment | Docker, Docker Compose | Containerized services |

---

## 📁 Project Structure

```
IntelliPlant AI/
├── backend/
│   ├── app/
│   │   ├── agents/            # AI agents (supervisor, expert, rca, compliance, lessons)
│   │   ├── api/               # API routes (auth, chat, documents, graph, search, etc.)
│   │   ├── services/          # Core services (LangGraph, retrieval, vector store, etc.)
│   │   ├── db/                # Database models and connections
│   │   ├── models/            # Pydantic schemas
│   │   ├── config.py          # Environment configuration
│   │   └── main.py            # FastAPI application
│   ├── tests/                 # Test suite
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Backend container
│   └── run.py                 # Entry point
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx           # Dashboard
│   │   ├── chat/              # AI Chat interface
│   │   ├── documents/         # Document management
│   │   ├── graph/             # Knowledge graph visualization
│   │   ├── analytics/         # Usage analytics
│   │   ├── landing/           # Product landing page
│   │   ├── about/             # Creator profile
│   │   ├── services/api.ts    # API client
│   │   └── types/index.ts     # TypeScript types
│   ├── package.json           # Node dependencies
│   └── Dockerfile             # Frontend container
├── docs/                      # Architecture & design PDFs (24 documents)
├── docker-compose.yml         # Full stack deployment
├── .env.example               # Environment variable template
├── TECHNICAL_DOCUMENTATION.md # Detailed technical reference
├── SUBMISSION_DOCUMENT.md     # Hackathon submission document
└── DEMO_SCRIPT.md             # Demo recording guide
```


---

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Node.js 22+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yash1501-arch/InterlliplantAI.git
cd InterlliplantAI
```

### 2. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - GROQ_API_KEY (get from https://console.groq.com)
# - QDRANT_URL + QDRANT_API_KEY (get from https://cloud.qdrant.io)
# - NEO4J_URI + NEO4J_PASSWORD (get from https://neo4j.com/cloud)
```

### 3. Start Backend
```bash
cd backend
pip install -r requirements.txt
python run.py
# Server starts at http://localhost:8000
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
# App starts at http://localhost:3000
```

### 5. (Alternative) Docker Compose
```bash
docker-compose up
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User authentication |
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/documents/upload` | Upload + full AI pipeline |
| GET | `/api/v1/documents` | List all documents |
| POST | `/api/v1/documents/reindex` | Reindex all docs to Qdrant |
| POST | `/api/v1/chat` | AI chat (LangGraph workflow) |
| POST | `/api/v1/search` | Hybrid search (40/40/20) |
| POST | `/api/v1/rca` | Root cause analysis |
| POST | `/api/v1/compliance/check` | Compliance check |
| POST | `/api/v1/lessons` | Lessons learned |
| GET | `/api/v1/graph/{equipment_id}` | Knowledge graph data |
| GET | `/api/v1/dashboard/metrics` | Dashboard metrics |
| GET | `/api/v1/dashboard/trends` | Upload trends |
| WS | `/ws/chat` | WebSocket real-time chat |
| GET | `/health` | Health check |

---

## 📸 Screenshots

### Dashboard
- Real-time metrics (documents, sessions, messages, equipment)
- Weekly activity trends chart
- Recent uploads list

### AI Chat
- Natural language Q&A with LangGraph-powered responses
- Source citations with relevance scores
- Confidence indicator
- Agent routing metadata

### Knowledge Graph
- Interactive force-directed visualization
- Drag, zoom, pan controls
- Filter by node type (Equipment, Failure, Incident, Regulation, Personnel)
- Click nodes to view connections
- Statistics panel

### Landing Page
- Animated hero section with counters
- Feature showcase
- Agent system explanation
- Technology stack display
- Creator profile

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Health check | < 50ms |
| Dashboard load | < 100ms |
| Search (hybrid) | < 500ms |
| Chat response (with LLM) | 3-8 seconds |
| Document upload + pipeline | 2-10 seconds |
| Graph visualization | < 500ms |

---

## 🔒 Security

- **JWT Authentication** — Access tokens (15min) + Refresh tokens (7 days)
- **RBAC** — Role-based access (Admin, Engineer, Viewer)
- **bcrypt** — One-way password hashing
- **Input Validation** — Pydantic schemas prevent injection
- **CORS** — Configured for frontend origin only
- **Secrets** — Environment variables, never committed to git

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md) | Full technical reference with judge Q&A |
| [SUBMISSION_DOCUMENT.md](./SUBMISSION_DOCUMENT.md) | Hackathon submission document |
| [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) | Demo video recording guide |
| [docs/](./docs/) | 24 architecture & design PDFs |

---

## 🗺️ Roadmap

- [ ] Celery background workers for async OCR
- [ ] BGE Reranker for improved result quality
- [ ] Multi-hop graph reasoning (2-3 hops)
- [ ] Redis conversation memory
- [ ] Document auto-classification
- [ ] Mobile app for field technicians
- [ ] SCADA/IoT real-time integration

---

## 👨‍💻 Author

**Narayan Parab**  
Data Analyst | Full Stack Developer | AI Engineer

- 📧 narayanp1501@gmail.com
- 🎓 B.E. Information Technology — Atharva College of Engineering, Mumbai
- 🏆 ET AI Hackathon 2026

---

## 📄 License

This project was built for the ET AI Hackathon 2026. All rights reserved.

---

<p align="center">
  <strong>⚡ IntelliPlant AI — Transform Documents into Industrial Intelligence ⚡</strong>
</p>
