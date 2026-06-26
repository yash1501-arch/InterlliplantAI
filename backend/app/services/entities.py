import re

INDUSTRIAL_ENTITY_PATTERNS = {
    "EQUIPMENT": [
        "pump", "motor", "valve", "compressor", "turbine",
        "heat exchanger", "boiler", "pipeline", "vessel", "filter",
    ],
    "FAILURE": [
        "bearing failure", "leakage", "overheating", "corrosion",
        "erosion", "cavitation", "vibration", "fatigue", "fracture",
        "blockage",
    ],
    "INCIDENT": [
        "fire", "explosion", "spill", "trip", "shutdown",
        "near miss", "accident",
    ],
    "REGULATION": [
        "oisd", "iso 9001", "iso 14001", "iso 45001",
        "factory act", "peso", "osha", "api rp",
    ],
    "PERSONNEL": [
        "operator", "engineer", "manager", "inspector", "technician",
    ],
}


def extract_entities(text: str) -> list[dict]:
    lowered = text.lower()
    found = {}
    for entity_type, keywords in INDUSTRIAL_ENTITY_PATTERNS.items():
        for keyword in keywords:
            exact_pattern = re.compile(r"\b" + re.escape(keyword) + r"\b")
            exact_match = exact_pattern.search(lowered)

            if exact_match:
                confidence = 1.0
                match = exact_match
            elif keyword in lowered:
                confidence = 0.7
                match = re.search(re.escape(keyword), lowered)
            else:
                continue

            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].replace("\n", " ")
            entity_name = text[match.start() : match.end()]

            key = keyword
            if key not in found or confidence > found[key]["confidence"]:
                found[key] = {
                    "entity": entity_name,
                    "type": entity_type,
                    "confidence": confidence,
                    "context": context.strip(),
                }
    return list(found.values())
