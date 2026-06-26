from typing import Any, TypedDict

from app.config import settings
from app.services.llm import call_llm, is_llm_available


class SupervisorState(TypedDict):
    message: str
    intent: str
    agents: list[str]
    response: str
    confidence: float


def _keyword_analyze(message: str) -> SupervisorState:
    lowered = message.lower()

    intent_map = {
        "pump": ("maintenance", ["expert", "rca"]),
        "inspection": ("maintenance", ["expert", "rca"]),
        "maintenance": ("maintenance", ["expert", "rca"]),
        "motor": ("maintenance", ["expert", "rca"]),
        "valve": ("maintenance", ["expert", "rca"]),
        "rca": ("rca", ["rca", "expert"]),
        "root cause": ("rca", ["rca", "expert"]),
        "failure": ("rca", ["rca", "expert", "lessons"]),
        "breakdown": ("rca", ["rca", "expert"]),
        "compliance": ("compliance", ["compliance", "expert"]),
        "policy": ("compliance", ["compliance", "expert"]),
        "audit": ("compliance", ["compliance", "expert"]),
        "oisd": ("compliance", ["compliance", "expert"]),
        "iso": ("compliance", ["compliance", "expert"]),
        "peso": ("compliance", ["compliance", "expert"]),
        "lesson": ("lessons", ["lessons", "rca", "expert"]),
        "learned": ("lessons", ["lessons", "rca", "expert"]),
        "near miss": ("lessons", ["lessons", "expert"]),
        "incident": ("lessons", ["lessons", "rca"]),
        "pattern": ("lessons", ["lessons", "rca", "expert"]),
    }

    detected_intent = "general"
    detected_agents = ["expert", "rca", "compliance"]
    best_score = 0

    for keyword, (intent, agents) in intent_map.items():
        if keyword in lowered:
            score = len(keyword)
            if score > best_score:
                best_score = score
                detected_intent = intent
                detected_agents = agents

    intent_response_map = {
        "maintenance": (
            f"Supervisor agent analyzed \"{message}\" and identified a maintenance or "
            f"inspection intent. Routing to expert and RCA agents for equipment assessment."
        ),
        "rca": (
            f"Supervisor agent analyzed \"{message}\" and identified a root cause analysis "
            f"intent. Routing to RCA and expert agents for failure investigation."
        ),
        "compliance": (
            f"Supervisor agent analyzed \"{message}\" and identified a compliance or audit "
            f"intent. Routing to compliance and expert agents for regulatory review."
        ),
        "lessons": (
            f"Supervisor agent analyzed \"{message}\" and identified a lessons-learned "
            f"intent. Routing to lessons, RCA, and expert agents for pattern analysis."
        ),
        "general": (
            f"Supervisor agent received: {message}. Routing to all available agents "
            "for comprehensive analysis."
        ),
    }

    confidence = 0.95 if detected_intent != "general" else 0.50

    return SupervisorState(
        message=message,
        intent=detected_intent,
        agents=detected_agents,
        response=intent_response_map[detected_intent],
        confidence=confidence,
    )


def _llm_analyze(message: str) -> SupervisorState:
    system_prompt = (
        "You are an intelligent supervisor agent for an industrial plant maintenance platform. "
        "Analyze the user message and classify the intent into one of: "
        "'maintenance', 'rca', 'compliance', 'lessons', 'general'. "
        "Respond in this exact format:\n"
        "INTENT: <intent>\n"
        "AGENTS: <comma-separated list of agents from [expert, rca, compliance, lessons]>\n"
        "CONFIDENCE: <0.0-1.0>\n"
        "RESPONSE: <brief explanation of routing decision>"
    )

    result = call_llm(system_prompt, message)
    intent = "general"
    agents = ["expert", "rca", "compliance"]
    response_text = f"Supervisor agent received: {message}"
    confidence = 0.50

    for line in result.split("\n"):
        line = line.strip()
        if line.upper().startswith("INTENT:"):
            parsed = line.split(":", 1)[1].strip().lower()
            if parsed in ("maintenance", "rca", "compliance", "lessons", "general"):
                intent = parsed
        elif line.upper().startswith("AGENTS:"):
            parsed = [a.strip().lower() for a in line.split(":", 1)[1].split(",")]
            valid = {"expert", "rca", "compliance", "lessons"}
            filtered = [a for a in parsed if a in valid]
            if filtered:
                agents = filtered
        elif line.upper().startswith("CONFIDENCE:"):
            try:
                confidence = float(line.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.upper().startswith("RESPONSE:"):
            response_text = line.split(":", 1)[1].strip()

    return SupervisorState(
        message=message,
        intent=intent,
        agents=agents,
        response=response_text,
        confidence=confidence,
    )


def build_supervisor_response(message: str) -> dict[str, object]:
    if is_llm_available():
        state = _llm_analyze(message)
    else:
        state = _keyword_analyze(message)

    return {
        "intent": state["intent"],
        "response": state["response"],
        "agents": state["agents"],
    }
