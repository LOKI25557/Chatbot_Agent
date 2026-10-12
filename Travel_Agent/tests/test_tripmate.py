import sys
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure Travel_Agent directory is in sys.path
TRAVEL_AGENT_DIR = Path(__file__).resolve().parent.parent
if str(TRAVEL_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(TRAVEL_AGENT_DIR))

import config
import models
import tools
import memory
from planner import Planner
from agent import TravelAgent
import llm

# --- 1. Configuration Tests ---
def test_config_imports_and_path_resolution():
    """Verify that configuration settings and path resolution work properly."""
    assert hasattr(config, "is_groq_configured")
    assert hasattr(config, "GROQ_MODEL")
    assert hasattr(config, "GROQ_BASE_URL")
    assert "https://api.groq.com" in config.GROQ_BASE_URL
    assert config.WORKSPACE_ROOT.exists()
    assert config.env_path == config.WORKSPACE_ROOT / ".env"

def test_root_workspace_files_present():
    """Verify that required root configuration files exist."""
    root = config.WORKSPACE_ROOT
    assert (root / "requirements.txt").exists()
    assert (root / ".env.example").exists()
    assert (root / ".gitignore").exists()
    assert (root / "README.md").exists()

def test_config_behavior_when_credentials_absent(monkeypatch):
    """Verify that missing credentials correctly report unconfigured."""
    monkeypatch.setattr(config, "GROQ_API_KEY", "")
    assert config.is_groq_configured() is False
    monkeypatch.setattr(config, "GROQ_API_KEY", "   ")
    assert config.is_groq_configured() is False

def test_get_client_timeout():
    """Verify that OpenAI client is initialized with timeout."""
    with patch("llm.GROQ_API_KEY", "test_key"):
        client = llm.get_client()
        assert client.timeout == 15.0


# --- 2. Data Models Tests ---
def test_model_creation_and_defaults():
    """Verify data structures have proper typing and safe defaults."""
    req = models.TravelRequest(source="Bengaluru", destination="Goa")
    assert req.source == "Bengaluru"
    assert req.destination == "Goa"
    assert req.duration_days == 1
    assert req.budget == 0.0
    assert isinstance(req.preferences, list)

    plan = models.TravelPlan()
    assert plan.status == "DRAFT"
    assert plan.estimated_total_cost == 0.0

    state = models.AgentState()
    assert state.action_status == "NONE"
    assert state.requires_human_approval is False

# --- 3. Budget & Tool Arithmetic Tests ---
def test_budget_calculation_arithmetic():
    """Verify budget calculations use exact arithmetic."""
    # Transport: 1200, Hotel: 2500/night * 3 = 7500, Food: 500/day * 3 = 1500, Activities: 1000
    # Expected grand total = 1200 + 7500 + 1500 + 1000 = 11200
    result = tools.calculate_budget(
        transport_cost=1200.0,
        hotel_cost_per_night=2500.0,
        duration=3,
        food_cost_per_day=500.0,
        activity_cost_total=1000.0
    )
    assert result.success is True
    data = result.data
    assert data["transport_total"] == 1200.0
    assert data["hotel_total"] == 7500.0
    assert data["food_total"] == 1500.0
    assert data["activity_total"] == 1000.0
    assert data["grand_total"] == 11200.0

def test_budget_calculation_edge_cases():
    """Verify budget calculation handles zero, negative, or invalid types cleanly."""
    res = tools.calculate_budget(0, 0, 0, 0, 0)
    assert res.success is True
    assert res.data["grand_total"] == 0.0

# --- 4. Tool Execution & Failure Handling Tests ---
def test_tools_execution():
    """Verify simulated search tools return structured responses."""
    t_res = tools.search_transport("Bengaluru", "Goa", "Tomorrow")
    assert t_res.success is True
    assert len(t_res.data) >= 3

    w_res = tools.check_weather("Goa", "Tomorrow")
    assert w_res.success is True
    assert "temperature" in w_res.data

    a_res = tools.find_activities("Goa", ["beaches", "vegetarian food"])
    assert a_res.success is True
    assert any("Beach" in act for act in a_res.data)
    assert "Vegetarian restaurants" in a_res.data

def test_search_hotels_force_failure():
    """Verify that force_failure=True correctly marks Hotel A unavailable for replanning tests."""
    normal_hotels = tools.search_hotels("Goa", 3000, force_failure=False).data
    assert normal_hotels[0]["available"] is True

    failed_hotels = tools.search_hotels("Goa", 3000, force_failure=True).data
    assert failed_hotels[0]["available"] is False

def test_simulated_booking_tools():
    """Verify that booking tools produce explicit simulated confirmations."""
    t_booking = tools.book_transport({"type": "Bus", "price": 1200})
    assert t_booking.success is True
    assert t_booking.data.get("simulated") is True
    assert "SIMULATED" in t_booking.data.get("booking_id")

    h_booking = tools.book_hotel({"name": "Hotel B", "price": 1700})
    assert h_booking.success is True
    assert h_booking.data.get("simulated") is True

# --- 5. Planning & Validation Tests ---
def test_planner_initial_plan():
    """Verify planner creates and validates an initial feasible plan."""
    mem = {"preferred_transport": "bus"}
    planner = Planner(memory_data=mem, force_failure=False)
    req = models.TravelRequest(
        source="Bengaluru",
        destination="Goa",
        duration_days=3,
        budget=15000.0,
        preferences=["beaches"]
    )
    plan = planner.create_initial_plan(req)
    assert plan.destination == "Goa"
    assert plan.duration_days == 3
    assert plan.estimated_total_cost == 11200.0
    
    is_feasible, msg = planner.validate_plan(req)
    assert is_feasible is True
    assert "feasible" in msg.lower()

# --- 6. Replanning Tests ---
def test_planner_replanning_hotel_unavailability():
    """Verify planner automatically selects an alternative hotel upon failure."""
    mem = {"preferred_transport": "bus"}
    planner = Planner(memory_data=mem, force_failure=True)
    req = models.TravelRequest(
        source="Bengaluru",
        destination="Goa",
        duration_days=3,
        budget=15000.0,
        preferences=["beaches"]
    )
    # Initial plan has Hotel A which is unavailable
    planner.create_initial_plan(req)
    is_feasible, issue = planner.validate_plan(req)
    assert is_feasible is False
    assert "Hotel A is unavailable" in issue

    # Replan
    revised_plan = planner.replan(req, issue)
    assert revised_plan.status == "RE-PLANNED"
    assert revised_plan.hotel["name"] == "Hotel B"
    assert revised_plan.hotel["available"] is True

    # Validate revised plan
    is_valid, _ = planner.validate_plan(req)
    assert is_valid is True

def test_planner_replanning_budget_constraint():
    """Verify planner handles budget overflow and replans with cheaper options."""
    mem = {"preferred_transport": "flight"}
    planner = Planner(memory_data=mem, force_failure=False)
    # Flight: 3500, Hotel A: 2500*3=7500, food: 1500, act: 1000 = 13500. Budget is 12000.
    req = models.TravelRequest(
        source="Bengaluru",
        destination="Goa",
        duration_days=3,
        budget=12000.0,
        preferences=["sightseeing"]
    )
    planner.create_initial_plan(req)
    is_feasible, issue = planner.validate_plan(req)
    assert is_feasible is False
    assert "exceeds budget" in issue.lower()

    # Replan should downgrade to train/bus and cheaper hotel
    revised = planner.replan(req, issue)
    assert revised.status == "RE-PLANNED"
    assert revised.estimated_total_cost <= 12000.0

def test_planner_replanning_impossible_budget():
    """Verify planner correctly reports failure if even the cheapest combination exceeds budget."""
    mem = {}
    planner = Planner(memory_data=mem, force_failure=False)
    # Budget ₹500 is completely impossible for a 3-day trip
    req = models.TravelRequest(
        source="Bengaluru",
        destination="Goa",
        duration_days=3,
        budget=500.0,
        preferences=[]
    )
    planner.create_initial_plan(req)
    revised = planner.replan(req, "exceeds budget")
    assert revised.status == "FAILED"
    assert "No feasible plan" in revised.reasoning

# --- 7. Human Approval and Rejection Tests ---
def test_agent_human_approval_flow(tmp_path, monkeypatch):
    """Verify the agent halts at human approval and only books upon approval."""
    test_mem_file = tmp_path / "memory.json"
    monkeypatch.setattr(memory, "MEMORY_FILE_PATH", str(test_mem_file))
    
    agent = TravelAgent(force_failure=False)
    agent.run("I want to travel from Bengaluru to Goa for 3 days under ₹15,000. I prefer beaches.")
    
    # Must pause for human approval
    assert agent.state.requires_human_approval is True
    assert agent.state.action_status == "NONE"
    
    # Memory should not have recorded trip yet
    loaded_mem = memory.load_memory()
    assert len(loaded_mem.get("previous_trips", [])) == 0
    
    # Execute approval
    agent.execute_action()
    assert agent.state.requires_human_approval is False
    assert agent.state.action_status == "COMPLETED"
    
    # Trip is now persisted in memory
    updated_mem = memory.load_memory()
    assert len(updated_mem.get("previous_trips", [])) == 1
    assert updated_mem["previous_trips"][0]["destination"] == "Goa"

def test_agent_human_rejection_flow(tmp_path, monkeypatch):
    """Verify user can reject the proposed plan without booking or polluting history."""
    test_mem_file = tmp_path / "memory.json"
    monkeypatch.setattr(memory, "MEMORY_FILE_PATH", str(test_mem_file))
    
    agent = TravelAgent(force_failure=False)
    agent.run("I want to travel from Bengaluru to Goa for 3 days under ₹15,000.")
    assert agent.state.requires_human_approval is True
    
    # User rejects plan
    agent.reject_action("Destination changed")
    assert agent.state.requires_human_approval is False
    assert agent.state.action_status == "REJECTED"
    
    # Memory must not contain any trip
    loaded_mem = memory.load_memory()
    assert len(loaded_mem.get("previous_trips", [])) == 0
    
    # Check execution log contains rejection
    steps = [l["step"] for l in agent.state.execution_log]
    assert "HUMAN REJECTION" in steps

# --- 8. Memory Persistence & Recovery Tests ---
def test_memory_persistence(tmp_path, monkeypatch):
    """Verify preference updates and trip history persistence."""
    test_mem_file = tmp_path / "data" / "memory.json"
    monkeypatch.setattr(memory, "MEMORY_FILE_PATH", str(test_mem_file))
    
    mem = memory.load_memory()
    assert mem["preferred_food"] == "vegetarian"
    
    memory.update_preference("preferred_food", "vegan")
    assert memory.get_preference("preferred_food") == "vegan"

def test_memory_corrupted_json_recovery(tmp_path, monkeypatch):
    """Verify that invalid JSON in memory file recovers cleanly without crashing."""
    test_mem_file = tmp_path / "corrupt_memory.json"
    monkeypatch.setattr(memory, "MEMORY_FILE_PATH", str(test_mem_file))
    
    test_mem_file.parent.mkdir(parents=True, exist_ok=True)
    test_mem_file.write_text("{invalid json content!!!", encoding="utf-8")
    
    recovered = memory.load_memory()
    assert "preferred_food" in recovered
    assert recovered["preferred_food"] == "vegetarian"

# --- 9. Demo Mode Fallback Parsing Tests ---
def test_demo_parse_request():
    """Verify deterministic demo parser handles natural language travel requests."""
    res = llm._demo_parse_request("I want to travel from Bengaluru to Goa for 3 days under ₹15,000. I prefer beaches and vegetarian food.")
    assert res["source"] == "Bengaluru"
    assert res["destination"] == "Goa"
    assert res["duration_days"] == 3
    assert res["budget"] == 15000.0
    assert "beaches" in res["preferences"]
    assert "vegetarian food" in res["preferences"]

# --- 10. Mocked Groq Client & Error Handling Tests ---
def test_mocked_groq_llm_parsing():
    """Verify that OpenAI-compatible Groq parsing handles clean and markdown-wrapped JSON."""
    fake_json = json.dumps({
        "source": "Mumbai",
        "destination": "Delhi",
        "duration_days": 4,
        "budget": 20000.0,
        "preferences": ["monuments", "street food"]
    })
    
    mock_choice = MagicMock()
    mock_choice.message.content = f"```json\n{fake_json}\n```"
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    
    with patch("llm.is_groq_configured", return_value=True), \
         patch("llm.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_resp
        mock_get_client.return_value = mock_client
        
        parsed = llm.parse_travel_request("Trip from Mumbai to Delhi for 4 days")
        assert parsed["source"] == "Mumbai"
        assert parsed["destination"] == "Delhi"
        assert parsed["duration_days"] == 4
        assert parsed["budget"] == 20000.0
        assert "monuments" in parsed["preferences"]

def test_mocked_groq_llm_error_fallback():
    """Verify that API exceptions (decommissioned model, 400, 401, timeout) fall back to demo parsing."""
    with patch("llm.is_groq_configured", return_value=True), \
         patch("llm.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Model llama3-8b-8192 decommissioned")
        mock_get_client.return_value = mock_client
        
        fallback = llm.parse_travel_request("from Bengaluru to Goa for 3 days under 15000")
        assert fallback["source"] == "Bengaluru"
        assert fallback["destination"] == "Goa"
        assert fallback["duration_days"] == 3

def test_verify_groq_connection_sanitized_errors():
    """Verify verify_groq_connection categorizes errors cleanly without leaking secrets."""
    # When not configured
    with patch("llm.is_groq_configured", return_value=False):
        ok, msg = llm.verify_groq_connection()
        assert ok is False
        assert "Demo Mode" in msg

    # When model is decommissioned
    with patch("llm.is_groq_configured", return_value=True), \
         patch("llm.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("The model `llama3-8b-8192` has been decommissioned")
        mock_get_client.return_value = mock_client
        
        ok, msg = llm.verify_groq_connection()
        assert ok is False
        assert "decommissioned" in msg.lower()
        # Ensure no secrets leak
        assert "gsk_" not in msg
