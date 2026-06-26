from app.config import settings
import openai


def build_agent_plan(message: str) -> list[str]:
    lowered = message.lower()
    agents = ["supervisor"]

    keywords_expert = {"pump", "inspection", "maintenance", "motor", "valve",
                       "equipment", "repair", "sop", "manual", "guideline",
                       "diagnostic", "troubleshoot", "alignment", "bearing"}
    keywords_rca = {"rca", "root cause", "failure", "incident", "breakdown",
                    "why", "analysis", "fault", "defect", "anomaly", "crash"}
    keywords_compliance = {"compliance", "policy", "audit", "oisd", "iso",
                           "factory act", "peso", "regulation", "standard",
                           "legal", "safety", "inspection"}
    keywords_lessons = {"lesson", "learned", "pattern", "near miss",
                        "recurring", "historical", "trend", "incident"}

    if any(k in lowered for k in keywords_expert):
        agents.append("expert")
    if any(k in lowered for k in keywords_rca):
        agents.append("rca")
    if any(k in lowered for k in keywords_compliance):
        agents.append("compliance")
    if any(k in lowered for k in keywords_lessons):
        agents.append("lessons")

    if len(agents) == 1:
        agents.append("expert")

    return agents
