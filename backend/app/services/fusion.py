from app.config import settings
from app.services.orchestrator import build_agent_plan


def build_fused_response(message: str, agent_plan: list[str]) -> dict[str, object]:
    lowered = message.lower()
    insights = []

    if "expert" in agent_plan:
        insights.append(
            "Expert review: cross-referencing equipment specifications, "
            "maintenance history, and manufacturer guidelines to assess the condition."
        )
    if "rca" in agent_plan:
        insights.append(
            "RCA review: applying 5-why methodology to trace the failure "
            "chain and identify contributory factors."
        )
    if "compliance" in agent_plan:
        insights.append(
            "Compliance review: auditing the response against OISD, ISO 9001, "
            "Factory Act, and PESO regulatory requirements."
        )
    if "lessons" in agent_plan:
        insights.append(
            "Lessons review: mining historical incident patterns and near-miss "
            "reports for recurring failure modes."
        )

    if not insights:
        insights.append(
            "General review: summarizing the query and identifying next "
            "recommended actions for the operations team."
        )

    summary = " | ".join(insights)

    return {
        "summary": summary,
        "insights": insights,
    }
