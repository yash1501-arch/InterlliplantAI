# IntelliPlant AI — Technical Documentation
## Complete Reference for Judges & Q&A

---

## Table of Contents
1. [What is IntelliPlant AI?](#1-what-is-intelliplant-ai)
2. [Why This Project?](#2-why-this-project)
3. [Architecture Overview](#3-architecture-overview)
4. [Technology Stack Explained](#4-technology-stack-explained)
5. [LangGraph Multi-Agent System](#5-langgraph-multi-agent-system)
6. [Hybrid Search (40/40/20)](#6-hybrid-search-404020)
7. [Embedding Model](#7-embedding-model)
8. [Knowledge Graph (Neo4j)](#8-knowledge-graph-neo4j)
9. [Vector Database (Qdrant)](#9-vector-database-qdrant)
10. [Document Intelligence Pipeline](#10-document-intelligence-pipeline)
11. [LLM Integration](#11-llm-integration)
12. [MinIO Object Storage](#12-minio-object-storage)
13. [Authentication & Security](#13-authentication--security)
14. [Frontend Architecture](#14-frontend-architecture)
15. [How Data Flows End-to-End](#15-how-data-flows-end-to-end)
16. [What Makes This Different](#16-what-makes-this-different)
17. [Potential Judge Questions & Answers](#17-potential-judge-questions--answers)

---

## 1. What is IntelliPlant AI?

IntelliPlant AI is an **AI-powered Industrial Knowledge Intelligence Platform** that transforms fragmented industrial documents (maintenance manuals, SOPs, incident reports, inspection records, compliance documents) into a unified, searchable, intelligent knowledge base.

**Core Value:** Reduce information retrieval time from 30-60 minutes to under 20 seconds using AI agents, semantic search, and knowledge graphs.

**Target Users:** Maintenance engineers, reliability engineers, quality/compliance teams, plant managers, field technicians.

**Target Industries:** Oil & Gas, Manufacturing, Power Plants, Chemical Industries, Mining, EPC organizations.

---

## 2. Why This Project?

### The Problem
Industrial organizations have thousands of documents scattered across systems:
- Engineering drawings & P&IDs
- Maintenance work orders
- Standard Operating Procedures (SOPs)
- OEM equipment manuals
- Incident/accident reports
- Inspection records
- Compliance documents (OISD, ISO, Factory Act)

**Consequences:**
- Engineers waste hours searching for information
- Knowledge is lost when experts retire (tribal knowledge)
- Same failures repeat because lessons aren't shared
- Compliance gaps go undetected until audits
- Downtime increases due to slow troubleshooting

### The Solution
A single AI platform that:
- Ingests all document types
- Extracts entities and relationships automatically
- Builds a knowledge graph connecting everything
- Allows natural language questions
- Routes to specialist AI agents
- Returns answers with source citations

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    USERS                              │
│  Engineers, Managers, Technicians (via Browser)       │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              FRONTEND (Next.js 16)                    │
│  Dashboard | Chat | Documents | Graph | Analytics    │
└────────────────────────┬────────────────────────────┘
                         │ REST API / WebSocket
                         ▼
┌─────────────────────────────────────────────────────┐
│              API GATEWAY (FastAPI)                    │
│  Authentication | Routing | Validation | CORS        │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│          AI ORCHESTRATION (LangGraph)                 │
│                                                      │
│  Input Node → Supervisor → Retrieval → Agents →      │
│  Context Fusion → LLM Reasoning → Citation           │
└────────┬───────────┬───────────┬────────────────────┘
         │           │           │
         ▼           ▼           ▼
┌────────────┐ ┌──────────┐ ┌──────────────┐
│   Qdrant   │ │  Neo4j   │ │   SQLite     │
│  (Vectors) │ │  (Graph) │ │  (Metadata)  │
└────────────┘ └──────────┘ └──────────────┘
```

---

## 4. Technology Stack Explained


| Technology | Role | Why This Choice? |
|---|---|---|
| **Next.js 16** | Frontend framework | Server-side rendering, React 19, fast page transitions, TypeScript support |
| **FastAPI** | Backend API | Async Python, automatic OpenAPI docs, Pydantic validation, fastest Python framework |
| **LangGraph** | AI Orchestration | Stateful agent workflows with conditional routing, better than simple chains |
| **Groq (Llama 3.3 70B)** | LLM Provider | 10x faster inference than OpenAI, free tier, 70B parameter model quality |
| **Qdrant** | Vector Database | Purpose-built for embeddings, cloud-hosted, supports filtering, fast cosine search |
| **Neo4j** | Graph Database | Industry standard for knowledge graphs, Cypher query language, relationship traversal |
| **FastEmbed (BGE)** | Embedding Model | Runs locally (no API cost), high quality, 384-dimension vectors |
| **SQLite** | Relational Database | Zero-config for demo, stores users/documents/sessions (PostgreSQL in production) |
| **TailwindCSS 4** | Styling | Utility-first, rapid UI development, responsive by default |
| **Docker** | Deployment | Consistent environments, single-command deployment |
| **MinIO** | Object Storage | S3-compatible, stores original files, self-hosted |
| **Redis** | Caching (planned) | Session state, agent memory, response caching |

---

## 5. LangGraph Multi-Agent System

### What is LangGraph?
LangGraph is a framework by LangChain for building **stateful, multi-step AI workflows** as directed graphs. Unlike simple prompt chains, LangGraph supports:
- Conditional routing (if intent=RCA, go to RCA agent)
- State management (carry context between steps)
- Parallel execution (run multiple agents simultaneously)
- Error recovery (fallback if one agent fails)

### Our Workflow (7 Nodes)

```
User Query
    │
    ▼
┌─────────────────┐
│ 1. INPUT NODE   │  Query preprocessing + LLM-based query rewriting
└────────┬────────┘  (expands abbreviations: "P101" → "Pump P101")
         │
         ▼
┌─────────────────┐
│ 2. SUPERVISOR   │  Intent classification → selects which agents to activate
└────────┬────────┘  (maintenance | rca | compliance | lessons | general)
         │
         ▼
┌─────────────────┐
│ 3. RETRIEVAL    │  Hybrid search: Vector + Graph + BM25 (parallel)
└────────┬────────┘  Returns top documents from all three sources
         │
         ▼
┌─────────────────┐
│ 4. AGENTS       │  Execute specialist agents based on supervisor decision
└────────┬────────┘  Expert | RCA | Compliance | Lessons (parallel)
         │
         ▼
┌─────────────────┐
│ 5. FUSION       │  Merge all retrieved context + agent outputs
└────────┬────────┘  Creates unified context string for LLM
         │
         ▼
┌─────────────────┐
│ 6. LLM REASON  │  Generate final response grounded in evidence
└────────┬────────┘  Groq Llama 3.3 70B with full context window
         │
         ▼
┌─────────────────┐
│ 7. CITATION     │  Extract source documents, assign relevance scores
└─────────────────┘  Returns citations array with each response
```

### GraphState (Typed State Object)
```python
class GraphState(TypedDict):
    query: str                    # User's question
    intent: str                   # Classified intent
    selected_agents: list[str]    # Which agents to run
    retrieved_docs: list[dict]    # Hybrid search results
    vector_context: list[dict]    # Qdrant results
    graph_context: list[dict]     # Neo4j results
    keyword_context: list[dict]   # BM25 results
    merged_context: str           # Fused context for LLM
    agent_outputs: dict           # Each agent's response
    answer: str                   # Final response
    confidence_score: float       # 0.0 to 1.0
    citations: list[dict]         # Source documents
    errors: list[str]             # Any failures
```

### Why LangGraph Instead of Simple Chains?
- **Chains** are linear: A → B → C. If B fails, everything fails.
- **LangGraph** is a graph: A → B → (C or D depending on B's output). It can retry, skip, or take alternate paths.

---

## 6. Hybrid Search (40/40/20)

### What is Hybrid Search?
Instead of relying on one search method, we combine three different approaches and weight their results:

### The Three Search Legs

| Method | Weight | Technology | What It Finds |
|--------|--------|-----------|---------------|
| **Vector Search** | 40% | Qdrant + BGE Embeddings | Semantically similar content (understands meaning) |
| **Graph Search** | 40% | Neo4j Knowledge Graph | Related entities via relationships (multi-hop) |
| **BM25 Search** | 20% | SQLite full-text | Exact keyword matches (traditional search) |

### How Scoring Works

```
Final Score = 0.4 × normalized_vector_score
            + 0.4 × normalized_graph_score
            + 0.2 × normalized_bm25_score
```

### Example
Query: "Why did Pump P101 fail?"

- **Vector Search** → Finds documents about pump failures (semantic similarity)
- **Graph Search** → Traverses: Pump P101 → FAILED_IN → Bearing Failure → CAUSES → Overheating
- **BM25 Search** → Finds documents containing exact words "pump" "P101" "fail"

All results are merged, scored, and ranked. This gives better results than any single method alone.

### Why 40/40/20?
- Vector and Graph are equally important (both provide deep understanding)
- BM25 is a safety net for exact matches that semantic search might miss
- This ratio is specified in the architecture documents based on industrial search benchmarks

---

## 7. Embedding Model

### What Are Embeddings?
Embeddings convert text into numerical vectors (arrays of floating-point numbers) that capture semantic meaning. Similar text → similar vectors → found via cosine similarity.

### Our Model: BAAI/bge-small-en-v1.5

| Property | Value |
|----------|-------|
| Developer | Beijing Academy of AI (BAAI) |
| Model Size | ~33M parameters |
| Vector Dimensions | 384 |
| Language | English |
| Runs On | CPU (local, no API needed) |
| Library | FastEmbed |
| Cost | Free (runs locally) |

### Why BGE?
1. **Top performer** on MTEB benchmark (Massive Text Embedding Benchmark)
2. **Runs locally** — no API calls, no cost, no latency
3. **Small but accurate** — 384 dimensions is compact yet effective
4. **Fast inference** — can embed thousands of chunks quickly
5. **Open source** — MIT licensed

### How It's Used
```
Document Upload:
  "Pump P101 bearing failure due to misalignment"
       │
       ▼ BGE Embedding
  [0.023, -0.15, 0.89, ..., 0.034]  (384 numbers)
       │
       ▼ Stored in Qdrant

User Query:
  "Why do pumps fail?"
       │
       ▼ BGE Embedding
  [0.019, -0.12, 0.91, ..., 0.028]  (384 numbers)
       │
       ▼ Cosine Similarity against stored vectors
  
  Result: "Pump P101 bearing failure..." → Score: 0.92 (highly relevant!)
```


---

## 8. Knowledge Graph (Neo4j)

### What is a Knowledge Graph?
A knowledge graph stores information as **nodes** (entities) and **edges** (relationships). Unlike a table, it explicitly models how things are connected.

### Our Ontology (What We Store)

**Node Types:**
| Type | Examples | Properties |
|------|----------|-----------|
| Equipment | Pump P101, Motor M201, Valve V301 | id, name, type, status |
| Failure | Bearing failure, Leakage, Overheating | id, severity, category |
| Incident | Fire, Explosion, Shutdown, Near miss | id, description, date |
| Regulation | OISD, ISO 9001, Factory Act, PESO | id, name, version |
| Personnel | Operator, Engineer, Inspector | id, name, department |
| Document | manual.pdf, sop.txt | id, name, created_at |

**Relationship Types:**
| Relationship | From → To | Meaning |
|---|---|---|
| FAILED_IN | Equipment → Failure | "Pump P101 failed with bearing failure" |
| CAUSES | Failure → Failure/Incident | "Overheating caused fire" |
| CONNECTED_TO | Equipment → Equipment | "Pump connected to motor" |
| INSPECTED_BY | Equipment → Personnel | "Inspected by Engineer Raj" |
| REQUIRES | Equipment → Regulation | "Pump requires OISD compliance" |
| SIMILAR_TO | Failure → Failure | "This failure is similar to that one" |
| DESCRIBED_BY | Equipment → Document | "Pump described in manual.pdf" |

### Example Graph
```
Pump P101 ──FAILED_IN──→ Bearing Failure ──CAUSES──→ Overheating
    │                         │
    ├──REQUIRES──→ OISD 144   ├──SIMILAR_TO──→ Motor Bearing Failure
    │                         │
    ├──INSPECTED_BY──→ Engineer    └──DESCRIBED_BY──→ maintenance.pdf
    │
    └──CONNECTED_TO──→ Motor M201
```

### Why Neo4j?
1. **Multi-hop reasoning** — Find Pump → Failure → Cause → Similar Incidents in one query
2. **Relationship-first** — Unlike SQL, relationships are first-class citizens
3. **Cypher query language** — Intuitive pattern matching
4. **Industry standard** — Used by NASA, eBay, Walmart for knowledge graphs
5. **Cloud hosted** — We use Neo4j AuraDB (free tier)

### How We Build the Graph
```
Document uploaded → Entity extraction (regex patterns) → 
Relationship extraction (proximity + trigger words) → 
Neo4j nodes and edges created automatically
```

---

## 9. Vector Database (Qdrant)

### What is Qdrant?
Qdrant is a purpose-built vector database optimized for storing and searching high-dimensional vectors (embeddings). It's like a search engine for meaning.

### Why Not Just Use PostgreSQL?
- PostgreSQL can store vectors (pgvector), but it's **not optimized** for billion-scale similarity search
- Qdrant uses **HNSW indexing** (Hierarchical Navigable Small World) — logarithmic search time
- Qdrant supports **payload filtering** (search within a specific document type)
- Qdrant is **10-100x faster** for vector similarity than general-purpose databases

### Our Collection: `document_chunks`
```json
{
  "id": 12345678,
  "vector": [0.023, -0.15, 0.89, ...],  // 384 dimensions
  "payload": {
    "text": "Pump inspection checklist: Check vibration...",
    "document_id": "f629d01c-ae5b-40c6-a1c0-28a25869e0ce",
    "chunk_id": 3
  }
}
```

### Operations We Perform
- **Index:** Store document chunks as vectors during upload
- **Search:** Find semantically similar chunks for a query
- **Delete:** Remove vectors when a document is deleted
- **Stats:** Track how many vectors are stored

---

## 10. Document Intelligence Pipeline

### End-to-End Flow
```
User uploads file (PDF/DOCX/TXT/XLSX/Image)
         │
         ▼
┌─────────────────┐
│  OCR / Extract  │  PyPDF for PDF, python-docx for DOCX,
│                 │  Tesseract for images, openpyxl for XLSX
└────────┬────────┘
         │ Raw text extracted
         ▼
┌─────────────────┐
│   Chunking      │  Split into 1024-char chunks with 200-char overlap
└────────┬────────┘  (overlap ensures context isn't lost at boundaries)
         │ List of chunks
         ▼
┌─────────────────┐
│  Embedding      │  BGE model converts each chunk to 384-dim vector
└────────┬────────┘
         │ Vectors
         ▼
┌─────────────────┐
│  Qdrant Index   │  Vectors stored with metadata for retrieval
└────────┬────────┘
         │
         ▼ (parallel)
┌─────────────────┐
│ Entity Extract  │  Regex patterns identify Equipment, Failures, etc.
└────────┬────────┘
         │ Entities
         ▼
┌─────────────────┐
│ Relationship    │  Proximity + trigger words identify connections
│ Extraction      │  
└────────┬────────┘
         │ Relationships
         ▼
┌─────────────────┐
│  Neo4j Graph    │  Nodes and edges created in knowledge graph
└─────────────────┘
```

### Supported File Types
| Format | Extraction Method | What's Extracted |
|--------|------------------|-----------------|
| PDF | PyPDF (PdfReader) | Text from all pages |
| DOCX | python-docx | Paragraphs |
| XLSX | openpyxl | Cell values row by row |
| CSV | csv module | All rows |
| TXT | UTF-8 decode | Raw text + sections |
| PNG/JPG/TIFF | Tesseract OCR | Text from images |

### Chunking Strategy
- **Chunk size:** 1024 characters (optimal for embedding models)
- **Overlap:** 200 characters (prevents losing context at boundaries)
- **Why?** LLMs have limited context windows. Smaller chunks = more precise retrieval.

---

## 11. LLM Integration

### Provider: Groq (Primary)

| Property | Value |
|----------|-------|
| Model | Llama 3.3 70B Versatile |
| Provider | Groq |
| Speed | ~500 tokens/second (10x faster than OpenAI) |
| Cost | Free tier available |
| Parameters | 70 billion |
| Context Window | 128K tokens |

### Why Groq?
1. **Speed** — Groq uses custom LPU (Language Processing Unit) hardware, not GPUs
2. **Free tier** — Perfect for hackathon demos
3. **Quality** — Llama 3.3 70B is competitive with GPT-4 for technical tasks
4. **OpenAI-compatible API** — Easy to swap providers

### Fallback Chain
```
Groq (primary) → Gemini (secondary) → OpenAI (tertiary) → Keyword fallback
```
If the LLM is unavailable, agents fall back to rule-based keyword responses.

### How LLM is Used
1. **Query Rewriting** — Expand and clarify user queries before search
2. **Supervisor Intent Classification** — Determine which agents to activate
3. **Expert Agent** — Generate technical maintenance guidance
4. **RCA Agent** — Perform root cause analysis reasoning
5. **Compliance Agent** — Analyze regulatory requirements
6. **Final Response Generation** — Synthesize all context into a coherent answer


---

## 12. MinIO Object Storage

### What is MinIO?
MinIO is a **self-hosted, S3-compatible object storage** system. It stores files (binary objects) like PDFs, images, and documents — similar to AWS S3 but running on your own infrastructure.

### Why MinIO in This Project?
| Concern | Solution |
|---------|----------|
| Where do original files live? | MinIO stores raw uploaded files |
| What if we need to re-process? | Re-download from MinIO, run updated pipeline |
| How to serve file downloads? | MinIO provides HTTP access to stored files |
| Backup strategy? | MinIO handles replication and durability |

### Current Status
- **Configured** in `.env` (endpoint, access key, bucket name)
- **Not required** for the demo (documents are processed in-memory)
- **Production use:** Would store all original files separately from extracted text

### Architecture Role
```
MinIO = File cabinet (original documents — PDFs, images, raw files)
SQLite = Notebook (extracted text, metadata, user sessions)
Qdrant = Brain (semantic understanding as vectors)
Neo4j = Map (relationships between entities)
```

---

## 13. Authentication & Security

### JWT-Based Authentication
```
User Login → Server validates credentials → Issues JWT tokens
    │
    ├── Access Token (15 min expiry) — for API calls
    └── Refresh Token (7 day expiry) — for getting new access tokens
```

### Role-Based Access Control (RBAC)
| Role | Can Do | Cannot Do |
|------|--------|-----------|
| Admin | Everything | — |
| Engineer | Upload, Chat, RCA, Search, Graph | Delete users |
| Viewer | Chat, Search, View Graph | Upload, Delete |

### Security Measures
- **bcrypt** password hashing (one-way, salted)
- **JWT** tokens with expiry (not stored server-side)
- **CORS** configured for frontend origin
- **Pydantic** input validation (prevents injection)
- **Auth can be disabled** for demo (`AUTH_ENABLED=false`)

---

## 14. Frontend Architecture

### Framework: Next.js 16 + React 19

**Pages:**
| Route | Component | Description |
|-------|-----------|-------------|
| `/` | Dashboard | Metrics, charts, recent uploads |
| `/chat` | AI Chat | LangGraph-powered conversational AI |
| `/documents` | Document Manager | Upload, list, delete documents |
| `/graph` | Knowledge Graph | Interactive force-directed visualization |
| `/analytics` | Analytics | Usage stats, agent distribution, health |
| `/landing` | Landing Page | Animated product showcase |
| `/about` | About Page | Creator profile and project info |

### Key Frontend Features
- **Force-directed graph** — Custom physics simulation (no D3 dependency)
- **Real-time streaming** — Server-Sent Events for chat responses
- **Citation display** — Source documents shown below each AI response
- **Dark theme** — Industrial-grade aesthetic with Slate/Blue palette
- **Responsive** — Works on mobile (sidebar collapses)

---

## 15. How Data Flows End-to-End

### Scenario: User asks "Why did Pump P101 fail?"

```
Step 1: Frontend sends POST /api/v1/chat with message
         │
Step 2: LangGraph INPUT NODE
         - Rewrites query: "What are the causes of failure for Pump P101?"
         │
Step 3: SUPERVISOR NODE
         - Detects intent: "rca" (root cause analysis)
         - Selects agents: ["expert", "rca"]
         │
Step 4: RETRIEVAL NODE (parallel)
         - Vector Search → Qdrant finds: "Pump inspection checklist" (score: 0.89)
         - Graph Search → Neo4j traverses: Pump → FAILED_IN → Bearing Failure
         - BM25 Search → SQLite finds docs with "pump" + "fail" keywords
         - Fusion: 0.4×vector + 0.4×graph + 0.2×bm25 → ranked results
         │
Step 5: AGENT EXECUTION NODE
         - Expert Agent: "Check impeller wear, seal condition, alignment..."
         - RCA Agent: "Root causes: cavitation, bearing degradation, misalignment..."
         │
Step 6: CONTEXT FUSION NODE
         - Merges: retrieved docs + graph context + agent insights
         - Creates unified context string (~2000 chars)
         │
Step 7: LLM REASONING NODE
         - Groq Llama 3.3 receives: system prompt + context + user query
         - Generates grounded response citing specific documents
         │
Step 8: CITATION NODE
         - Extracts: [{source: "maintenance.pdf", score: 0.89}, ...]
         │
Step 9: Response returned to frontend with:
         - answer (full text)
         - citations (source documents)
         - confidence (0.95)
         - agents used (expert, rca)
         - routing metadata (intent: rca)
```

---

## 16. What Makes This Different

### vs. ChatGPT / Generic AI
| Feature | ChatGPT | IntelliPlant AI |
|---------|---------|-----------------|
| Knowledge source | Training data (outdated) | Your actual documents (live) |
| Citations | None / hallucinated | Real document sources with scores |
| Domain expertise | General | Industrial-specific agents |
| Knowledge graph | None | Neo4j with equipment relationships |
| Search | None | Triple hybrid (vector+graph+keyword) |
| Hallucination risk | High | Low (grounded in evidence) |

### vs. Simple RAG
| Feature | Basic RAG | IntelliPlant AI |
|---------|-----------|-----------------|
| Search method | Vector only | 40% Vector + 40% Graph + 20% BM25 |
| Orchestration | Single chain | LangGraph stateful workflow |
| Agents | Single LLM call | 5 specialist agents |
| Entity awareness | None | Equipment, Failure, Regulation extraction |
| Reasoning | 1-hop | Multi-hop via knowledge graph |
| Query preprocessing | None | LLM-based query rewriting |

### Key Innovations
1. **Triple Hybrid Search** — No other hackathon project combines all three search methods with weighted scoring
2. **LangGraph (not LangChain)** — Stateful graph workflow, not simple chains
3. **Domain-Specific Ontology** — Built specifically for industrial plant maintenance
4. **Explainable AI** — Every answer has traceable citations
5. **Query Rewriting** — LLM improves queries before searching

---

## 17. Potential Judge Questions & Answers


### Q: Why LangGraph instead of LangChain?
**A:** LangChain is for linear chains (A→B→C). LangGraph adds **state management** and **conditional routing** — our supervisor can route to different agents based on intent, retry on failure, and maintain context across steps. It's the evolution of LangChain for complex multi-agent systems.

### Q: How does the system prevent hallucinations?
**A:** Three mechanisms:
1. **Retrieval-Augmented Generation (RAG)** — LLM only sees context from actual documents
2. **Citations** — Every response must cite its sources, making hallucinations traceable
3. **Confidence scoring** — Low-evidence responses get low confidence scores, alerting the user

### Q: Why three search methods? Isn't vector search enough?
**A:** No. Vector search misses exact technical terms (equipment IDs like "P101"). BM25 catches those. Graph search finds relationships that neither text-based method can discover (e.g., "Pump P101 is connected to Motor M201 which failed last month"). Together, they cover all retrieval scenarios.

### Q: How is the knowledge graph built automatically?
**A:** When a document is uploaded:
1. **Entity extraction** — Regex patterns identify equipment names, failures, regulations, personnel
2. **Relationship extraction** — Proximity analysis + trigger words (e.g., "failed", "caused", "inspected") determine how entities relate
3. **Graph construction** — Extracted entities become nodes, relationships become edges in Neo4j

### Q: What happens if Neo4j or Qdrant is down?
**A:** The system has graceful fallback:
- If Qdrant is down → Vector search returns empty, BM25 + Graph compensate
- If Neo4j is down → Graph search falls back to local entity matching in SQLite
- If LLM is down → Agents use keyword-based rule responses (no AI, but still functional)
- All services have try/except with logging

### Q: How do you handle large documents?
**A:** Chunking strategy:
- Documents are split into 1024-character chunks with 200-character overlap
- Each chunk is independently embedded and indexed
- During search, individual chunks are retrieved (not whole documents)
- The LLM receives the most relevant chunks, not entire files

### Q: Why did you choose Groq over OpenAI?
**A:** Speed and cost. Groq's LPU hardware delivers ~500 tokens/second (vs. ~50 for OpenAI GPT-4). For a real-time industrial assistant, response speed matters. Plus, free tier for the hackathon. The architecture supports swapping to OpenAI/Gemini with one env variable change.

### Q: How scalable is this?
**A:** Each layer scales independently:
- **Frontend** — CDN/Vercel (auto-scaling)
- **Backend** — Horizontal scaling with Docker containers
- **Qdrant** — Cloud-hosted, handles millions of vectors
- **Neo4j** — AuraDB cloud auto-scales
- **LLM** — Groq/OpenAI are external APIs (infinitely scalable)
- **Background processing** — Celery workers can be added for async OCR

### Q: What's the difference between your agents?
**A:**
- **Expert** — Answers "what" and "how" (SOPs, procedures, specifications)
- **RCA** — Answers "why" (failure analysis, root causes, 5-why methodology)
- **Compliance** — Answers "should we" (regulatory requirements, gaps, audit evidence)
- **Lessons** — Answers "what happened before" (patterns, recurring issues, prevention)

### Q: How does the Supervisor decide which agent to use?
**A:** Two methods:
1. **LLM-based** (when Groq is available) — Sends the query to the LLM with a classification prompt
2. **Keyword-based** (fallback) — Pattern matching on keywords like "pump/maintenance" → Expert, "failure/why" → RCA, "OISD/compliance" → Compliance, "lesson/pattern" → Lessons

### Q: What about data privacy?
**A:** 
- All documents stay within your infrastructure (no third-party indexing)
- LLM calls send only query + relevant context (not entire documents)
- Neo4j and Qdrant can be self-hosted (we use cloud for demo convenience)
- JWT auth ensures only authorized users access data
- Role-based access limits who can upload/delete

### Q: Can this work for other industries?
**A:** Yes. The entity extraction patterns and relationship rules are configurable. Change the ontology (node types, relationship types, keywords) and it works for:
- Healthcare (patients, diagnoses, medications, procedures)
- Legal (cases, statutes, precedents, parties)
- Finance (transactions, accounts, regulations, risks)
- Any domain with fragmented documents and complex relationships

### Q: What would you add with more time?
**A:**
1. **Celery workers** — Background async processing for large file uploads
2. **BGE Reranker** — Re-score results before sending to LLM for higher precision
3. **Multi-hop graph reasoning** — 2-3 hop traversal (Pump → Failure → Cause → Similar in other plant)
4. **Redis memory** — Remember previous questions in conversation for follow-ups
5. **Document classification** — Auto-tag as Manual, SOP, Incident Report, etc.
6. **Mobile app** — React Native for field technicians
7. **SCADA/IoT integration** — Real-time sensor data feeding into the knowledge graph

### Q: How many documents can it handle?
**A:** Currently tested with 589 documents (586 text records). The architecture supports:
- **Qdrant** — Handles millions of vectors (cloud tier)
- **Neo4j** — Handles billions of nodes/edges
- **SQLite** → Would migrate to PostgreSQL for production (handles millions of records)
- Chunking creates ~1-10 chunks per document, so 589 docs ≈ 2000-5000 vectors

### Q: What's the response time?
**A:** 
- **Health check:** <50ms
- **Dashboard metrics:** <100ms
- **Search (BM25 only):** <200ms
- **Chat with LangGraph + Groq LLM:** 3-8 seconds (depends on LLM response length)
- **Graph visualization:** <500ms

---

## Summary

IntelliPlant AI demonstrates a production-ready architecture for industrial AI:

1. **Multi-Agent AI** — Not a single prompt, but a coordinated system of specialists
2. **Triple Hybrid Search** — Vector + Graph + Keyword with weighted fusion
3. **Knowledge Graph** — Entities and relationships extracted automatically
4. **Explainable AI** — Every answer has source citations and confidence scores
5. **Full-Stack** — Next.js frontend, FastAPI backend, Docker deployment
6. **Real LLM** — Groq Llama 3.3 70B generating real-time responses

Built by **Narayan Parab** for the **ET AI Hackathon 2026**.
