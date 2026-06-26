# IntelliPlant AI - Demo Recording Script (3-4 minutes)

## Setup Before Recording
1. Open browser to `http://localhost:3000`
2. Make sure backend is running (`python run.py` from project root)
3. Keep the browser window clean (close other tabs)

---

## Scene 1: Introduction + Dashboard (0:00 - 0:30)

**Show:** Dashboard page (localhost:3000)

**Say:**
> "This is IntelliPlant AI — an AI-powered Industrial Knowledge Intelligence Platform. 
> It transforms fragmented industrial documents into a unified knowledge brain.
> Here you can see our dashboard showing 589 uploaded documents, 56 active sessions, 
> and 469 AI-powered queries processed. The weekly activity chart shows document 
> ingestion trends."

**Action:** Scroll to show recent uploads and the trend chart.

---

## Scene 2: Document Upload (0:30 - 1:00)

**Navigate:** Click "Documents" in sidebar

**Say:**
> "The platform ingests industrial documents through a full AI pipeline. 
> When we upload a document, it goes through OCR, text extraction, semantic chunking, 
> vector embedding into Qdrant, entity extraction, and knowledge graph construction in Neo4j."

**Action:** Click upload, select a sample file (any .txt or .pdf), show it appears in the list.

**Say:**
> "Each document is automatically indexed for semantic search, keyword search, 
> and graph-based retrieval."

---

## Scene 3: AI Chat with LangGraph (1:00 - 2:15)

**Navigate:** Click "Chat" in sidebar

**Say:**
> "The core of our platform is the LangGraph-powered conversational AI. 
> It uses a multi-agent system with a Supervisor that routes queries to 
> specialist agents."

**Type:** `Why do pumps fail?`

**Wait for response, then say:**
> "Notice how the system detected a 'maintenance' intent and activated the Expert 
> and RCA agents. The response is grounded in our uploaded documents — you can see 
> the citations below with source documents and relevance scores. 
> Confidence is 95% because it found strong evidence."

**Point out:** Citations badges, confidence score, routing metadata

**Type:** `Are we compliant with OISD standards?`

**Say:**
> "Now it detects 'compliance' intent and routes to the Compliance agent, 
> which checks against OISD, ISO 9001, Factory Act, and PESO regulations."

**Type:** `What lessons can we learn from recurring motor failures?`

**Say:**
> "This activates the Lessons Learned agent along with RCA for pattern analysis 
> across historical incidents."

---

## Scene 4: Knowledge Graph (2:15 - 2:50)

**Navigate:** Click "Graph" in sidebar

**Say:**
> "Our Knowledge Graph visualizes relationships extracted from documents. 
> Entities like equipment, failures, incidents, and regulations are connected 
> through relationships like FAILED_IN, CAUSES, and REQUIRES."

**Action:** Type `pump` and click "Explore"

**Say:**
> "Here we see the pump entity connected to related failures and inspections. 
> You can drag nodes, zoom, pan, and filter by type."

**Action:** Click a node to show detail panel. Toggle a filter chip.

---

## Scene 5: Analytics + Architecture (2:50 - 3:30)

**Navigate:** Click "Analytics" in sidebar

**Say:**
> "The analytics dashboard shows platform usage — agent distribution, 
> document types, upload trends, and system health including our 
> Qdrant vector store, Neo4j graph, and Groq LLM connections."

**Wrap up:**
> "Under the hood, our hybrid search uses a 40% Vector, 40% Graph, 20% BM25 
> scoring formula. The LangGraph workflow has 7 nodes: Input with query rewriting, 
> Supervisor for intent classification, Hybrid Retrieval, Agent Execution, 
> Context Fusion, LLM Reasoning, and Citation Generation.
> 
> IntelliPlant AI: Transform Documents into Industrial Intelligence."

---

## Tips for Recording
- Use OBS Studio or Windows Game Bar (Win+G) to record
- Resolution: 1920x1080
- Keep video under 50MB (3-4 min at 720p should be ~30-40MB)
- Speak clearly and not too fast
- Pause briefly after each action to let the UI update
