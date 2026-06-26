from app.services.llm import call_llm, is_llm_available
from app.services.rca import perform_rca_analysis


def _call_llm(system_prompt: str, user_message: str) -> str:
    return call_llm(system_prompt, user_message, temperature=0.2, max_tokens=512)


def _keyword_rca(message: str) -> dict[str, object]:
    lowered = message.lower()

    equipment = "general"
    if "pump" in lowered:
        equipment = "pump"
    elif "motor" in lowered:
        equipment = "motor"
    elif "valve" in lowered:
        equipment = "valve"
    elif "compressor" in lowered:
        equipment = "compressor"
    elif "bearing" in lowered:
        equipment = "bearing"

    rca_result = perform_rca_analysis(equipment)

    cause_map = {
        "pump": [
            "Cavitation due to low NPSH or incorrect impeller trim",
            "Bearing degradation from inadequate lubrication or contamination",
            "Shaft misalignment between pump and driver",
            "Wear ring clearance exceeding OEM tolerance",
            "Suction recirculation causing vibration and noise",
        ],
        "motor": [
            "Winding insulation breakdown from thermal stress or moisture ingress",
            "Bearing seizure due to grease starvation or contamination",
            "Unbalanced supply voltage causing current unbalance",
            "Rotor bar breakage from starting stress cycles",
            "Cooling fan blockage leading to overheating",
        ],
        "valve": [
            "Seat erosion from high-velocity flow or cavitation",
            "Stem packing leakage due to improper compression",
            "Actuator hysteresis or stiction causing positioning error",
            "Internal corrosion from incompatible process fluid",
            "Spring fatigue in pressure relief valves",
        ],
    }

    causes = cause_map.get(equipment, [
        "Review maintenance history for recurring failure patterns",
        "Check operating conditions against design parameters",
        "Inspect for material fatigue or environmental degradation",
        "Verify lubrication and cooling system functionality",
    ])

    recommendations = [
        "Schedule vibration analysis and thermography inspection",
        "Review maintenance logs for recurring failure patterns",
        "Verify operating parameters against OEM specifications",
        "Implement condition monitoring for early warning detection",
    ]

    if equipment != "general":
        recommendations.insert(0, f"Conduct dismantling inspection of the {equipment}")

    return {
        "agent": "rca",
        "response": rca_result["root_cause"],
        "root_causes": causes,
        "recommendations": recommendations,
        "confidence": 0.82,
    }


def _llm_rca(message: str) -> dict[str, object]:
    system_prompt = (
        "You are a root cause analysis specialist using the 5-why methodology for industrial equipment failures. "
        "Analyze the described failure or issue and provide:\n"
        "1. Likely root causes (2-5 items)\n"
        "2. Corrective and preventive recommendations (2-5 items)\n"
        "3. A confidence score\n\n"
        "Respond in this format:\n"
        "ROOT_CAUSES: <comma-separated list>\n"
        "RECOMMENDATIONS: <comma-separated list>\n"
        "CONFIDENCE: <0.0-1.0>\n"
        "RESPONSE: <detailed RCA analysis narrative>"
    )

    result = _call_llm(system_prompt, message)
    root_causes = [
        "Review maintenance history for recurring failure patterns",
    ]
    recommendations = [
        "Schedule vibration analysis and thermography inspection",
    ]
    confidence = 0.82
    response = f"RCA agent: Performing root cause analysis for: {message}"

    for line in result.split("\n"):
        line = line.strip()
        if line.upper().startswith("ROOT_CAUSES:"):
            root_causes = [c.strip() for c in line.split(":", 1)[1].split(",") if c.strip()]
        elif line.upper().startswith("RECOMMENDATIONS:"):
            recommendations = [r.strip() for r in line.split(":", 1)[1].split(",") if r.strip()]
        elif line.upper().startswith("CONFIDENCE:"):
            try:
                confidence = float(line.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.upper().startswith("RESPONSE:"):
            response = line.split(":", 1)[1].strip()

    return {
        "agent": "rca",
        "response": response,
        "root_causes": root_causes,
        "recommendations": recommendations,
        "confidence": confidence,
    }


def build_rca_agent_response(message: str) -> dict[str, object]:
    if is_llm_available():
        return _llm_rca(message)
    return _keyword_rca(message)
