RELATIONSHIP_RULES = {
    "FAILED_IN": {
        "source_types": ["EQUIPMENT"],
        "target_types": ["FAILURE"],
        "triggers": [
            "failure", "failed", "breakdown", "malfunction",
            "fault", "defect", "damage",
        ],
    },
    "CAUSES": {
        "source_types": ["FAILURE"],
        "target_types": ["FAILURE", "INCIDENT"],
        "triggers": [
            "caused", "causes", "led to", "resulted in",
            "triggered", "lead to",
        ],
    },
    "CONNECTED_TO": {
        "source_types": ["EQUIPMENT"],
        "target_types": ["EQUIPMENT"],
        "triggers": [
            "connected", "linked", "attached", "adjacent",
            "coupled", "joined",
        ],
    },
    "INSPECTED_BY": {
        "source_types": ["EQUIPMENT"],
        "target_types": ["PERSONNEL"],
        "triggers": [
            "inspected", "inspection", "checked", "check",
            "reviewed", "examined", "monitor",
        ],
    },
    "REQUIRES": {
        "source_types": ["EQUIPMENT"],
        "target_types": ["REGULATION"],
        "triggers": [
            "requires", "must comply", "regulated", "standard",
            "compliance", "mandatory",
        ],
    },
    "DESCRIBED_BY": {
        "source_types": ["EQUIPMENT"],
        "target_types": ["DOCUMENT"],
        "triggers": ["see", "refer", "described", "documented"],
    },
    "REFERENCES": {
        "source_types": ["DOCUMENT"],
        "target_types": ["REGULATION"],
        "triggers": [
            "reference", "according to", "per", "compliant",
            "as per",
        ],
    },
    "SIMILAR_TO": {
        "source_types": ["FAILURE"],
        "target_types": ["FAILURE"],
        "triggers": [
            "similar", "like", "analogous", "comparable",
            "same as",
        ],
    },
    "LOCATED_IN": {
        "source_types": ["EQUIPMENT"],
        "target_types": ["LOCATION"],
        "triggers": [
            "located", "installed", "situated", "area",
            "positioned", "mounted",
        ],
    },
}


def extract_relationships(entities: list[dict], text: str) -> list[dict]:
    lowered = text.lower()
    rels = []
    seen_pairs = set()

    for i, src in enumerate(entities):
        for j, tgt in enumerate(entities):
            if i == j:
                continue
            pair_key = (src["entity"].lower(), tgt["entity"].lower())
            if pair_key in seen_pairs:
                continue

            src_idx = lowered.find(src["entity"].lower())
            tgt_idx = lowered.find(tgt["entity"].lower())
            if src_idx < 0 or tgt_idx < 0:
                continue
            distance = abs(tgt_idx - src_idx)

            for rel_type, rule in RELATIONSHIP_RULES.items():
                if (
                    src["type"] in rule["source_types"]
                    and tgt["type"] in rule["target_types"]
                ):
                    trigger = next(
                        (t for t in rule["triggers"] if t in lowered), None
                    )

                    if trigger or distance < 200:
                        seen_pairs.add(pair_key)
                        if trigger:
                            tdx = lowered.index(trigger)
                        else:
                            tdx = min(src_idx, tgt_idx)
                        start = max(0, tdx - 30)
                        end = min(len(text), tdx + 60)
                        evidence = text[start:end].replace("\n", " ")
                        rels.append(
                            {
                                "source": src["entity"],
                                "target": tgt["entity"],
                                "type": rel_type,
                                "confidence": min(
                                    src["confidence"], tgt["confidence"]
                                ),
                                "evidence": evidence.strip(),
                            }
                        )
                        break
    return rels
