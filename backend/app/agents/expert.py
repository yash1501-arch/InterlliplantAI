from app.services.llm import call_llm, is_llm_available
from app.services.retrieval import build_demo_search_result


def _call_llm(system_prompt: str, user_message: str) -> str:
    return call_llm(system_prompt, user_message, temperature=0.2, max_tokens=512)


def _keyword_expert(message: str) -> dict[str, object]:
    lowered = message.lower()

    focus_map = {
        "pump": (
            "Expert agent: Based on pump operating data, inspect impeller wear, "
            "check seal condition, verify alignment, and review vibration trends.",
            "pump_inspection",
        ),
        "motor": (
            "Expert agent: Check motor winding resistance, bearing temperature, "
            "vibration levels, and insulation integrity.",
            "motor_analysis",
        ),
        "valve": (
            "Expert agent: Verify valve stroke timing, seat leakage, actuator "
            "response, and positioner calibration.",
            "valve_diagnostics",
        ),
        "compressor": (
            "Expert agent: Inspect compressor valves, piston rings, cylinder "
            "lubrication, and intercooler efficiency.",
            "compressor_analysis",
        ),
        "bearing": (
            "Expert agent: Check bearing temperature, vibration spectrum, "
            "lubrication condition, and alignment tolerances.",
            "bearing_assessment",
        ),
        "seal": (
            "Expert agent: Inspect mechanical seal faces, flush plan integrity, "
            "and leakage rates against OEM specifications.",
            "seal_inspection",
        ),
    }

    focus = "general_assessment"
    response = f"Expert agent: Performing general equipment assessment for: {message}"

    for keyword, (resp, foc) in focus_map.items():
        if keyword in lowered:
            response = resp
            focus = foc
            break

    search_results = build_demo_search_result(message)

    return {
        "agent": "expert",
        "response": response,
        "focus": focus,
        "confidence": 0.85,
        "sources": [r["title"] for r in search_results["results"][:3]],
    }


def _llm_expert(message: str) -> dict[str, object]:
    search_results = build_demo_search_result(message)
    source_titles = [r["title"] for r in search_results["results"][:3]]
    source_context = "; ".join(source_titles) if source_titles else "No specific documents found"

    system_prompt = (
        "You are an expert maintenance and reliability engineer for industrial plant equipment. "
        "Answer the user's question with specific technical guidance, referencing SOPs, "
        "manufacturer guidelines, and engineering best practices. "
        "Include the relevant equipment focus area.\n\n"
        f"Relevant documents from search: {source_context}\n\n"
        "Respond in this format:\n"
        "FOCUS: <focus_area>\n"
        "CONFIDENCE: <0.0-1.0>\n"
        "RESPONSE: <detailed technical guidance>"
    )

    result = _call_llm(system_prompt, message)
    focus = "general_assessment"
    confidence = 0.85
    response = f"Expert agent: Performing general equipment assessment for: {message}"

    for line in result.split("\n"):
        line = line.strip()
        if line.upper().startswith("FOCUS:"):
            focus = line.split(":", 1)[1].strip().lower().replace(" ", "_")
        elif line.upper().startswith("CONFIDENCE:"):
            try:
                confidence = float(line.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.upper().startswith("RESPONSE:"):
            response = line.split(":", 1)[1].strip()

    return {
        "agent": "expert",
        "response": response,
        "focus": focus,
        "confidence": confidence,
        "sources": source_titles,
    }


def build_expert_response(message: str) -> dict[str, object]:
    if is_llm_available():
        return _llm_expert(message)
    return _keyword_expert(message)
