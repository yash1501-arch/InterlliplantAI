from app.services.llm import call_llm, is_llm_available
from app.services.lessons import extract_lessons


def _call_llm(system_prompt: str, user_message: str) -> str:
    return call_llm(system_prompt, user_message, temperature=0.2, max_tokens=512)


def _keyword_lessons(message: str) -> dict[str, object]:
    lowered = message.lower()

    patterns = []
    recommendations = []

    if "failure" in lowered or "incident" in lowered or "breakdown" in lowered:
        patterns.extend([
            {
                "pattern": "Equipment failure due to inadequate preventive maintenance",
                "frequency": "high",
                "severity": "high",
            },
            {
                "pattern": "Repeat failures on similar equipment classes indicating systemic gaps",
                "frequency": "medium",
                "severity": "high",
            },
        ])
        recommendations.extend([
            "Implement predictive maintenance schedule based on OEM recommendations",
            "Create a cross-functional review team for repeated failure modes",
            "Update preventive maintenance checklists with lessons-learned insights",
        ])

    if "near miss" in lowered or "close call" in lowered or "near-miss" in lowered:
        patterns.append({
            "pattern": "Near-miss events indicating latent safety system gaps",
            "frequency": "medium",
            "severity": "medium",
        })
        recommendations.extend([
            "Conduct root cause analysis on near-miss events",
            "Update safety procedures and conduct refresher training",
            "Implement a near-miss reporting and tracking system",
        ])

    if "motor" in lowered:
        patterns.append({
            "pattern": "Motor winding failures correlated with power quality events",
            "frequency": "medium",
            "severity": "high",
        })
        recommendations.append("Install power quality monitoring on critical motor circuits")

    if "pump" in lowered:
        patterns.append({
            "pattern": "Pump seal failures linked to off-BEP operation and cavitation",
            "frequency": "high",
            "severity": "medium",
        })
        recommendations.append("Review pump operating points against best efficiency range")

    if not patterns:
        patterns.append({
            "pattern": "No significant incident patterns detected from ingested documents",
            "frequency": "unknown",
            "severity": "low",
        })
        recommendations.append("Continue routine monitoring and document ingestion")

    response = (
        f"Lessons agent: Identified {len(patterns)} incident pattern(s). "
        f"Key recommendation: {recommendations[0] if recommendations else 'Continue monitoring'}."
    )

    return {
        "agent": "lessons",
        "response": response,
        "patterns": patterns,
        "recommendations": recommendations,
        "confidence": 0.80,
    }


def _llm_lessons(message: str) -> dict[str, object]:
    system_prompt = (
        "You are a lessons-learned analyst for industrial plant operations. "
        "Analyze the user query and mine for incident patterns, near-miss trends, "
        "and recurring failure modes. Provide actionable recommendations.\n\n"
        "Respond in this format:\n"
        "PATTERNS: <comma-separated list of incident patterns>\n"
        "RECOMMENDATIONS: <comma-separated list>\n"
        "CONFIDENCE: <0.0-1.0>\n"
        "RESPONSE: <detailed lessons-learned analysis>"
    )

    result = _call_llm(system_prompt, message)
    patterns = []
    recommendations = []
    confidence = 0.80
    response = f"Lessons agent: Analyzing incident patterns for: {message}"

    for line in result.split("\n"):
        line = line.strip()
        if line.upper().startswith("PATTERNS:"):
            patterns_raw = line.split(":", 1)[1].strip()
            patterns = [
                {
                    "pattern": p.strip(),
                    "frequency": "medium",
                    "severity": "medium",
                }
                for p in patterns_raw.split(",")
                if p.strip()
            ]
            if not patterns:
                patterns.append({
                    "pattern": "No significant incident patterns detected",
                    "frequency": "unknown",
                    "severity": "low",
                })
        elif line.upper().startswith("RECOMMENDATIONS:"):
            recommendations = [r.strip() for r in line.split(":", 1)[1].split(",") if r.strip()]
        elif line.upper().startswith("CONFIDENCE:"):
            try:
                confidence = float(line.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.upper().startswith("RESPONSE:"):
            response = line.split(":", 1)[1].strip()

    if not patterns:
        patterns.append({
            "pattern": "No significant incident patterns detected",
            "frequency": "unknown",
            "severity": "low",
        })

    return {
        "agent": "lessons",
        "response": response,
        "patterns": patterns,
        "recommendations": recommendations,
        "confidence": confidence,
    }


def build_lessons_agent_response(message: str) -> dict[str, object]:
    if is_llm_available():
        return _llm_lessons(message)
    return _keyword_lessons(message)
