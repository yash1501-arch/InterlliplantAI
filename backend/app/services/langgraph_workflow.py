"""
LangGraph Stateful Workflow for IntelliPlant AI
Implements the multi-agent orchestration as specified in the architecture documents.

Flow: Input → Supervisor → Agent Selection → Retrieval → Fusion → LLM → Citation → Response
"""
import logging
from typing import Any, TypedDict

from langgraph.graph import StateGraph, END

from app.config import settings
from app.services.llm import call_llm, is_llm_available

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """State object flowing through the LangGraph workflow."""
    query: str
    intent: str
    selected_agents: list[str]
    retrieved_docs: list[dict]
    vector_context: list[dict]
    graph_context: list[dict]
    keyword_context: list[dict]
    merged_context: str
    agent_outputs: dict[str, Any]
    answer: str
    confidence_score: float
    citations: list[dict]
    errors: list[str]


# ─── Node Functions ───────────────────────────────────────────────────────────


def input_node(state: GraphState) -> GraphState:
    """Preprocess and validate the user query."""
    query = state["query"].strip()
    if not query:
        state["errors"].append("Empty query received")
        return state

    # Query rewriting: expand abbreviations and clarify intent
    if is_llm_available():
        try:
            rewrite_prompt = (
                "You are a query rewriter for an industrial knowledge platform. "
                "Rewrite the following user query to improve search relevance. "
                "Expand abbreviations (e.g., 'P101' → 'Pump P101'), resolve acronyms, "
                "and make the query more specific. Keep it concise (max 2 sentences). "
                "If the query is already clear, return it unchanged.\n\n"
                "ONLY return the rewritten query, nothing else."
            )
            rewritten = call_llm(rewrite_prompt, query, max_tokens=100)
            if rewritten and len(rewritten) < 500:
                state["query"] = rewritten
        except Exception:
            pass  # Keep original query on failure

    return state


def supervisor_node(state: GraphState) -> GraphState:
    """Classify intent and select agents."""
    from app.agents.supervisor import build_supervisor_response

    result = build_supervisor_response(state["query"])
    state["intent"] = result["intent"]
    state["selected_agents"] = result["agents"]
    return state


def retrieval_node(state: GraphState) -> GraphState:
    """Execute hybrid retrieval: Vector + Graph + BM25."""
    from app.services.retrieval import hybrid_retrieval, _load_documents, _bm25_score, _vector_search, _graph_search

    documents = _load_documents()
    query = state["query"]

    # Vector search
    try:
        vector_results = _vector_search(query, limit=5)
        state["vector_context"] = vector_results
    except Exception as e:
        state["errors"].append(f"Vector search error: {e}")
        state["vector_context"] = []

    # Graph search
    try:
        graph_results = _graph_search(query)
        state["graph_context"] = graph_results
    except Exception as e:
        state["errors"].append(f"Graph search error: {e}")
        state["graph_context"] = []

    # BM25 keyword search
    try:
        bm25_results = _bm25_score(query, documents)
        state["keyword_context"] = bm25_results[:5]
    except Exception as e:
        state["errors"].append(f"BM25 search error: {e}")
        state["keyword_context"] = []

    # Full hybrid retrieval
    try:
        hybrid_results = hybrid_retrieval(query, documents, limit=5)
        state["retrieved_docs"] = hybrid_results
    except Exception as e:
        state["errors"].append(f"Hybrid retrieval error: {e}")
        state["retrieved_docs"] = []

    return state


def agent_execution_node(state: GraphState) -> GraphState:
    """Execute selected specialist agents."""
    from app.agents.expert import build_expert_response
    from app.agents.rca_agent import build_rca_agent_response
    from app.agents.compliance_agent import build_compliance_agent_response
    from app.agents.lessons_agent import build_lessons_agent_response

    agent_outputs = {}
    selected = state["selected_agents"]

    if "expert" in selected:
        try:
            agent_outputs["expert"] = build_expert_response(state["query"])
        except Exception as e:
            state["errors"].append(f"Expert agent error: {e}")

    if "rca" in selected:
        try:
            agent_outputs["rca"] = build_rca_agent_response(state["query"])
        except Exception as e:
            state["errors"].append(f"RCA agent error: {e}")

    if "compliance" in selected:
        try:
            agent_outputs["compliance"] = build_compliance_agent_response(state["query"])
        except Exception as e:
            state["errors"].append(f"Compliance agent error: {e}")

    if "lessons" in selected:
        try:
            agent_outputs["lessons"] = build_lessons_agent_response(state["query"])
        except Exception as e:
            state["errors"].append(f"Lessons agent error: {e}")

    state["agent_outputs"] = agent_outputs
    return state


def context_fusion_node(state: GraphState) -> GraphState:
    """Merge all retrieved context into a unified context string."""
    parts = []

    # Add retrieved document snippets
    for doc in state["retrieved_docs"][:5]:
        text = doc.get("text", "")
        if text:
            parts.append(f"[DOC:{doc.get('document_name', 'unknown')}] {text[:300]}")

    # Add graph context
    for gc in state["graph_context"][:3]:
        parts.append(f"[GRAPH] {gc.get('text', '')}")

    # Add agent insights
    for agent_name, output in state["agent_outputs"].items():
        if isinstance(output, dict) and output.get("response"):
            parts.append(f"[{agent_name.upper()}] {output['response'][:300]}")

    state["merged_context"] = "\n\n".join(parts) if parts else "No context available."
    return state


def llm_reasoning_node(state: GraphState) -> GraphState:
    """Generate final answer using LLM with full context."""
    if not is_llm_available():
        # Fallback: combine agent outputs directly
        responses = []
        for agent_name, output in state["agent_outputs"].items():
            if isinstance(output, dict) and output.get("response"):
                responses.append(output["response"])
        state["answer"] = " ".join(responses) if responses else f"Analysis for: {state['query']}"
        state["confidence_score"] = 0.6
        return state

    system_prompt = f"""You are IntelliPlant AI, an expert industrial knowledge intelligence assistant.
You help engineers with equipment maintenance, root cause analysis, compliance, and lessons learned.

Your intent classification: {state['intent']}
Active agents: {', '.join(state['selected_agents'])}

Context from retrieval and agents:
{state['merged_context']}

Instructions:
- Provide a clear, actionable response grounded in the context provided.
- If the context contains relevant equipment data, reference it specifically.
- Include specific recommendations where applicable.
- Be concise but thorough.
- End with a confidence assessment (high/medium/low) based on evidence quality."""

    try:
        answer = call_llm(system_prompt, state["query"], max_tokens=1024)
        state["answer"] = answer
        # Estimate confidence from context richness
        context_signals = len(state["retrieved_docs"]) + len(state["graph_context"]) + len(state["agent_outputs"])
        state["confidence_score"] = min(0.95, 0.5 + (context_signals * 0.05))
    except Exception as e:
        state["errors"].append(f"LLM error: {e}")
        # Fallback
        responses = [o["response"] for o in state["agent_outputs"].values() if isinstance(o, dict) and o.get("response")]
        state["answer"] = " ".join(responses) if responses else f"I encountered an error processing your query: {state['query']}"
        state["confidence_score"] = 0.4

    return state


def citation_node(state: GraphState) -> GraphState:
    """Generate citations from retrieved documents."""
    citations = []
    seen_docs = set()

    for doc in state["retrieved_docs"]:
        doc_id = doc.get("document_id", "")
        doc_name = doc.get("document_name", "")
        if doc_id and doc_id not in seen_docs:
            seen_docs.add(doc_id)
            citations.append({
                "source": doc_name or doc_id,
                "document_id": doc_id,
                "relevance_score": round(doc.get("score", 0), 3),
                "matched_entities": doc.get("matched_entities", []),
            })

    # Add graph-sourced citations
    for gc in state["graph_context"]:
        doc_id = gc.get("document_id", "")
        if doc_id and doc_id not in seen_docs:
            seen_docs.add(doc_id)
            citations.append({
                "source": gc.get("document_name", doc_id),
                "document_id": doc_id,
                "relevance_score": round(gc.get("score", 0), 3),
                "graph_relation": gc.get("graph_relation", ""),
            })

    state["citations"] = citations[:10]
    return state


# ─── Graph Construction ───────────────────────────────────────────────────────


def build_workflow() -> StateGraph:
    """Build the LangGraph workflow."""
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("input", input_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("agent_execution", agent_execution_node)
    workflow.add_node("context_fusion", context_fusion_node)
    workflow.add_node("llm_reasoning", llm_reasoning_node)
    workflow.add_node("citation", citation_node)

    # Define edges (sequential flow)
    workflow.set_entry_point("input")
    workflow.add_edge("input", "supervisor")
    workflow.add_edge("supervisor", "retrieval")
    workflow.add_edge("retrieval", "agent_execution")
    workflow.add_edge("agent_execution", "context_fusion")
    workflow.add_edge("context_fusion", "llm_reasoning")
    workflow.add_edge("llm_reasoning", "citation")
    workflow.add_edge("citation", END)

    return workflow


# Compile the workflow once
_compiled_workflow = None


def get_workflow():
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = build_workflow().compile()
    return _compiled_workflow


def run_chat_workflow(query: str) -> dict[str, Any]:
    """
    Execute the full LangGraph workflow for a chat query.
    Returns the complete response with answer, citations, agents, and confidence.
    """
    initial_state: GraphState = {
        "query": query,
        "intent": "general",
        "selected_agents": [],
        "retrieved_docs": [],
        "vector_context": [],
        "graph_context": [],
        "keyword_context": [],
        "merged_context": "",
        "agent_outputs": {},
        "answer": "",
        "confidence_score": 0.0,
        "citations": [],
        "errors": [],
    }

    try:
        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)
    except Exception as e:
        logger.error("LangGraph workflow failed: %s", e)
        # Graceful fallback
        from app.agents.supervisor import build_supervisor_response
        from app.services.fusion import build_fused_response
        from app.services.orchestrator import build_agent_plan

        supervisor = build_supervisor_response(query)
        plan = build_agent_plan(query)
        fused = build_fused_response(query, plan)
        final_state = {
            **initial_state,
            "intent": supervisor["intent"],
            "selected_agents": plan,
            "answer": f"{supervisor['response']} {fused['summary']}",
            "confidence_score": 0.5,
            "errors": [str(e)],
        }

    return {
        "response": final_state["answer"],
        "intent": final_state["intent"],
        "agents": final_state["selected_agents"],
        "confidence": final_state["confidence_score"],
        "citations": final_state["citations"],
        "retrieval": {
            "vector_results": len(final_state.get("vector_context", [])),
            "graph_results": len(final_state.get("graph_context", [])),
            "bm25_results": len(final_state.get("keyword_context", [])),
            "total_docs": len(final_state.get("retrieved_docs", [])),
        },
        "errors": final_state.get("errors", []),
    }
