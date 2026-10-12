from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class TravelRequest:
    source: str = ""
    destination: str = ""
    duration_days: int = 1
    budget: float = 0.0
    travel_date: str = "Flexible"
    preferences: List[str] = field(default_factory=list)
    travelers: int = 1


@dataclass
class ToolResult:
    tool_name: str
    success: bool
    data: Any
    message: str

@dataclass
class TravelPlan:
    destination: str = ""
    duration_days: int = 0
    transport: Dict[str, Any] = field(default_factory=dict)
    hotel: Dict[str, Any] = field(default_factory=dict)
    activities: List[str] = field(default_factory=list)
    weather: Dict[str, Any] = field(default_factory=dict)
    estimated_food_cost: float = 0.0
    estimated_activity_cost: float = 0.0
    estimated_total_cost: float = 0.0
    status: str = "DRAFT"
    reasoning: str = ""

@dataclass
class AgentState:
    user_request: str = ""
    goal: Optional[TravelRequest] = None
    memory: Dict[str, Any] = field(default_factory=dict)
    plan: Optional[TravelPlan] = None
    observations: List[str] = field(default_factory=list)
    execution_log: List[Dict[str, str]] = field(default_factory=list)
    current_step: str = "INITIALIZED"
    requires_human_approval: bool = False
    action_status: str = "NONE"
