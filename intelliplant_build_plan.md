# IntelliPlant AI — Full Platform Build Plan

## Current State
Starter scaffold with FastAPI skeleton, all 9 API route modules (thin wrappers), SQLite DB, rule-based mock agents, 5 static HTML pages, 17 passing tests. Everything intelligent is a placeholder.

## Build Phases

### Phase 1: Foundation & Infrastructure
**Goal:** Dockerize, add config, wire up real databases
- [ ] Add `.env` configuration (python-dotenv)
- [ ] Set up Docker Compose (PostgreSQL, Neo4j, Qdrant, Redis, MinIO)
- [ ] Update `requirements.txt` with all AI/ML/db dependencies
- [ ] Switch from SQLite to PostgreSQL with SQLAlchemy + Alembic migrations
- [ ] Add Neo4j driver connection
- [ ] Add Qdrant client connection
- [ ] Add Redis connection (cache + task queue)
- [ ] Add MinIO client (file storage)
- [ ] Create proper middleware (auth, CORS, rate limiting, logging)
- [ ] Add structured error handling

### Phase 2: Auth & User Management
**Goal:** Real JWT auth with RBAC
- [ ] Implement real JWT (access + refresh tokens)
- [ ] bcrypt password hashing
- [ ] User CRUD with PostgreSQL
- [ ] RBAC middleware (Admin, Manager, Engineer, Technician)
- [ ] Registration endpoint
- [ ] OAuth2 support (future)
- [ ] Auth tests

### Phase 3: Document Ingestion Pipeline
**Goal:** Full ingestion workflow
- [ ] File type detection & validation
- [ ] PDF parsing (pdfplumber/pypdf2)
- [ ] OCR integration (Tesseract + PaddleOCR via API)
- [ ] Table extraction
- [ ] Metadata extraction (title, author, dates, equipment references)
- [ ] Text chunking (overlap strategy)
- [ ] Embedding generation (BGE-Large via sentence-transformers)
- [ ] Vector storage in Qdrant
- [ ] File storage in MinIO
- [ ] Celery worker for async processing
- [ ] WebSocket progress notifications
- [ ] Retry + dead-letter queue
- [ ] Ingestion tests

### Phase 4: Entity Extraction & Knowledge Graph
**Goal:** Extract industrial entities and build Neo4j knowledge graph
- [ ] Domain NER (Equipment, Failure, Incident, Regulation, Personnel)
- [ ] LLM-based entity extraction (Gemini/OpenAI)
- [ ] Entity validation & linking
- [ ] Typed relationship extraction (CAUSES, FAILED_IN, INSPECTED_BY, etc.)
- [ ] Neo4j graph construction with 9 node types + 9 relationship types
- [ ] Confidence scoring for entities/relationships
- [ ] Graph traversal queries
- [ ] Entity extraction tests

### Phase 5: Hybrid Search Engine
**Goal:** Weighted hybrid search (Vector + Graph + BM25)
- [ ] BM25 keyword index
- [ ] Semantic vector search (Qdrant)
- [ ] Graph traversal search (Neo4j)
- [ ] Weighted fusion: 0.4 Vector + 0.4 Graph + 0.2 BM25
- [ ] BGE Reranker integration
- [ ] Query intent detection
- [ ] Graceful degradation (fallback strategies)
- [ ] Search tests

### Phase 6: GraphRAG
**Goal:** Graph-enhanced RAG with citations + confidence
- [ ] Query processing pipeline
- [ ] Context fusion (vector + graph + keyword results)
- [ ] LLM answer generation with source grounding
- [ ] Citation generation
- [ ] Confidence scoring: 0.4×Retrieval + 0.3×Citation + 0.3×GraphEvidence
- [ ] Hallucination detection (threshold <0.7 → "Insufficient evidence")
- [ ] Memory integration (short/long-term)
- [ ] GraphRAG tests

### Phase 7: Multi-Agent System (LangGraph)
**Goal:** Full LangGraph-orchestrated agent system
- [ ] LangGraph state machine
- [ ] **Supervisor Agent** — intent detection, task routing, context management
- [ ] **Expert Copilot Agent** — SOP retrieval, engineering Q&A, manual lookup
- [ ] **RCA Agent** — failure analysis, 5-why, historical incidents, recommendations
- [ ] **Compliance Agent** — Factory Act, OISD, ISO, PESO checking + audit reports
- [ ] **Lessons Learned Agent** — near misses, incident patterns, recommendations
- [ ] **Memory Agent** — short-term (Redis) + long-term (Neo4j/PostgreSQL)
- [ ] Conditional routing, parallel execution, human-in-the-loop
- [ ] Agent tests

### Phase 8: Frontend (NextJS)
**Goal:** Full NextJS frontend replacing static HTML
- [ ] Initialize NextJS + TypeScript + TailwindCSS + Shadcn
- [ ] **Auth pages** — Login, Register
- [ ] **Dashboard** — metrics cards, charts (recharts), recent activity, trend indicators
- [ ] **Document Management** — upload, list, search, detail view, delete
- [ ] **Chat Interface** — WebSocket streaming, markdown rendering, citations display, confidence scores, agent routing metadata
- [ ] **Knowledge Graph Visualization** — interactive D3.js/Cytoscape graph, zoom/pan, click for details
- [ ] **RCA Dashboard** — RCA history, causal chain visualization
- [ ] **Compliance Dashboard** — audit results, gap analysis, report generation
- [ ] **Analytics** — usage stats, search trends, document metrics

### Phase 9: API Completion
**Goal:** Complete all API endpoints with full implementation
- [ ] Chat — streaming, history, session management
- [ ] Search — pagination, filters, hybrid results
- [ ] RCA — full analysis with historical data
- [ ] Compliance — full audit with gap analysis
- [ ] Lessons — pattern mining with recommendations
- [ ] Graph — interactive queries, subgraph extraction
- [ ] Dashboard — time-series, trends, aggregation
- [ ] WebSocket — real-time streaming for chat + progress

### Phase 10: Testing & Quality
**Goal:** Comprehensive test coverage
- [ ] Unit tests for every service
- [ ] Integration tests for all API endpoints
- [ ] E2E tests for critical flows
- [ ] Performance/load tests
- [ ] Security tests (injection, XSS, auth bypass)

### Phase 11: Deployment
**Goal:** Production-ready deployment
- [ ] Docker Compose for all services
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Logging (ELK Stack)
- [ ] Health checks + readiness probes

---

## Immediate Next Steps (Starting Now)

I will begin with **Phase 1** (Foundation & Infrastructure) and **Phase 3** (Document Ingestion) in parallel since they are the most critical dependencies for everything else.

### Files to modify:
- `backend/requirements.txt` — add all deps
- `backend/.env` — new file for config
- `backend/app/config.py` — new file for settings
- `backend/app/db/database.py` — upgrade to PostgreSQL + Alembic
- `backend/app/db/__init__.py` — new
- `backend/app/services/ocr.py` — real OCR
- `backend/app/services/ingestion.py` — pipeline
- `docker-compose.yml` — new
- `Dockerfile` — new

### Verification:
- `docker-compose up` brings all services online
- `pytest` passes all existing tests
- `POST /api/v1/documents/upload` with a PDF returns a valid response
- `GET /health` returns status ok
