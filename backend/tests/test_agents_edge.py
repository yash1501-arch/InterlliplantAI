from app.agents.supervisor import build_supervisor_response
from app.agents.expert import build_expert_response
from app.agents.rca_agent import build_rca_agent_response
from app.agents.compliance_agent import build_compliance_agent_response
from app.agents.lessons_agent import build_lessons_agent_response


def test_supervisor_with_empty_string() -> None:
    result = build_supervisor_response("")
    assert result["intent"] == "general"
    assert result["response"]
    assert len(result["agents"]) > 0


def test_supervisor_with_maintenance_intent() -> None:
    result = build_supervisor_response("pump inspection needed")
    assert result["intent"] == "maintenance"
    assert "expert" in result["agents"]


def test_supervisor_with_rca_intent() -> None:
    result = build_supervisor_response("root cause analysis of motor failure")
    assert result["intent"] == "rca"
    assert "rca" in result["agents"]


def test_supervisor_with_compliance_intent() -> None:
    result = build_supervisor_response("compliance check for OISD standards")
    assert result["intent"] == "compliance"
    assert "compliance" in result["agents"]


def test_supervisor_with_lessons_intent() -> None:
    result = build_supervisor_response("lessons learned from incident")
    assert result["intent"] == "lessons"
    assert "lessons" in result["agents"]


def test_supervisor_with_special_characters() -> None:
    result = build_supervisor_response("pump!@#$%^&*() failure?")
    assert result["response"]


def test_supervisor_with_unicode() -> None:
    result = build_supervisor_response("motör héat exchánger failure")
    assert result["response"]


def test_expert_with_unknown_equipment() -> None:
    result = build_expert_response("analyze the hyperdrive reactor")
    assert result["agent"] == "expert"
    assert result.get("response") or result.get("focus")


def test_expert_with_known_equipment() -> None:
    result = build_expert_response("pump vibration analysis")
    assert "pump" in result["response"].lower() or "pump" in result["focus"]
    assert result["confidence"] > 0


def test_expert_with_empty_string() -> None:
    result = build_expert_response("")
    assert result["agent"] == "expert"


def test_rca_with_non_failure_query() -> None:
    result = build_rca_agent_response("weather forecast for today")
    assert result["agent"] == "rca"
    assert result["response"]


def test_rca_with_equipment_failure() -> None:
    result = build_rca_agent_response("pump bearing failure")
    assert result["agent"] == "rca"
    assert len(result["root_causes"]) > 0
    assert len(result["recommendations"]) > 0


def test_rca_with_empty_string() -> None:
    result = build_rca_agent_response("")
    assert result["agent"] == "rca"


def test_compliance_with_irrelevant_query() -> None:
    result = build_compliance_agent_response("what is the weather today")
    assert result["agent"] == "compliance"
    assert result["standards_checked"]


def test_compliance_with_oisd_query() -> None:
    result = build_compliance_agent_response("OISD compliance for pressure vessels")
    assert result["agent"] == "compliance"
    assert "OISD" in result["standards_checked"] or "oisd" in str(result["standards_checked"]).lower()


def test_compliance_with_empty_string() -> None:
    result = build_compliance_agent_response("")
    assert result["agent"] == "compliance"


def test_lessons_with_failure_input() -> None:
    result = build_lessons_agent_response("failure and incident analysis")
    assert result["agent"] == "lessons"
    assert len(result["patterns"]) > 0
    assert len(result["recommendations"]) > 0


def test_lessons_with_pump_input() -> None:
    result = build_lessons_agent_response("pump seal failures")
    assert result["agent"] == "lessons"
    assert len(result["patterns"]) > 0


def test_lessons_with_near_miss_input() -> None:
    result = build_lessons_agent_response("near miss reporting")
    assert result["agent"] == "lessons"
    assert len(result["patterns"]) > 0


def test_lessons_with_empty_string() -> None:
    result = build_lessons_agent_response("")
    assert result["agent"] == "lessons"
    assert len(result["patterns"]) > 0


def test_lessons_with_no_incident_keywords() -> None:
    result = build_lessons_agent_response("hello world test message")
    assert result["agent"] == "lessons"
    assert len(result["patterns"]) >= 1
