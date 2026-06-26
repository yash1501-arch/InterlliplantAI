from app.services.llm import call_llm, is_llm_available
from app.services.compliance import check_compliance


def _call_llm(system_prompt: str, user_message: str) -> str:
    return call_llm(system_prompt, user_message, temperature=0.2, max_tokens=512)


def _keyword_compliance(message: str) -> dict[str, object]:
    lowered = message.lower()
    standards_checked = ["OISD", "ISO 9001", "Factory Act", "PESO"]

    standard_map = {
        "oisd": (
            "Compliance agent: OISD standards require regular pressure testing, "
            "relief valve inspection, fire protection system checks, and "
            "safety training records for all operating personnel."
        ),
        "iso": (
            "Compliance agent: ISO 9001 requires documented procedures, internal "
            "audit trails, management review records, and corrective action "
            "documentation for non-conformances."
        ),
        "factory": (
            "Compliance agent: Factory Act compliance requires working hour records, "
            "safety equipment logs, training documentation, and welfare facility "
            "maintenance records."
        ),
        "peso": (
            "Compliance agent: PESO regulations mandate explosive area classification, "
            "flameproof equipment certification, static earthing verification, "
            "and periodic safety audits for hazardous installations."
        ),
    }

    response = (
        f"Compliance agent: Checking compliance against "
        f"{', '.join(standards_checked)} for: {message}"
    )

    for keyword, resp in standard_map.items():
        if keyword in lowered:
            response = resp
            break

    compliance_result = check_compliance(query=message)
    gaps = [
        v for v in compliance_result.get("violations", [])
        if v.get("status") == "insufficient_evidence"
    ]

    return {
        "agent": "compliance",
        "response": response,
        "standards_checked": standards_checked,
        "gaps": gaps,
        "confidence": 0.78,
    }


def _llm_compliance(message: str) -> dict[str, object]:
    system_prompt = (
        "You are a compliance auditor specializing in OISD, ISO 9001, Factory Act, "
        "and PESO regulations for industrial plants. "
        "Analyze the user query and determine which standards apply. "
        "Identify compliance gaps and requirements.\n\n"
        "Respond in this format:\n"
        "STANDARDS_CHECKED: <comma-separated list>\n"
        "GAPS: <comma-separated list of identified gaps or 'none'>\n"
        "CONFIDENCE: <0.0-1.0>\n"
        "RESPONSE: <detailed compliance analysis>"
    )

    result = _call_llm(system_prompt, message)
    standards_checked = ["OISD", "ISO 9001", "Factory Act", "PESO"]
    gaps = []
    confidence = 0.78
    response = f"Compliance agent: Performing compliance check for: {message}"

    for line in result.split("\n"):
        line = line.strip()
        if line.upper().startswith("STANDARDS_CHECKED:"):
            parsed = [s.strip() for s in line.split(":", 1)[1].split(",") if s.strip()]
            if parsed:
                standards_checked = parsed
        elif line.upper().startswith("GAPS:"):
            gap_text = line.split(":", 1)[1].strip()
            if gap_text.lower() != "none":
                gaps = [g.strip() for g in gap_text.split(",") if g.strip()]
        elif line.upper().startswith("CONFIDENCE:"):
            try:
                confidence = float(line.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.upper().startswith("RESPONSE:"):
            response = line.split(":", 1)[1].strip()

    return {
        "agent": "compliance",
        "response": response,
        "standards_checked": standards_checked,
        "gaps": gaps,
        "confidence": confidence,
    }


def build_compliance_agent_response(message: str) -> dict[str, object]:
    if is_llm_available():
        return _llm_compliance(message)
    return _keyword_compliance(message)
