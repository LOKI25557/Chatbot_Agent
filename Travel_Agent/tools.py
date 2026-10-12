from models import ToolResult
from typing import Dict, Any, List

def search_transport(source: str, destination: str, travel_date: str) -> ToolResult:
    """Mock transport search with input validation."""
    src = str(source).strip() if source else "Bengaluru"
    dst = str(destination).strip() if destination else "Goa"
    
    data = [
        {"type": "Bus", "price": 1200.0, "duration": "12 hours", "available": True},
        {"type": "Train", "price": 900.0, "duration": "13 hours", "available": True},
        {"type": "Flight", "price": 3500.0, "duration": "1.5 hours", "available": True}
    ]
    return ToolResult(
        tool_name="search_transport",
        success=True,
        data=data,
        message=f"Found transport options from {src} to {dst}"
    )

def search_hotels(destination: str, budget_per_night: float, force_failure: bool = False) -> ToolResult:
    """Mock hotel search. Deterministic failure mode built-in."""
    dst = str(destination).strip() if destination else "Goa"
    safe_budget = max(0.0, float(budget_per_night)) if budget_per_night is not None else 3000.0
    
    # Force failure makes Hotel A unavailable for testing replanning
    data = [
        {"name": "Hotel A", "price": 2500.0, "rating": 4.2, "available": not force_failure},
        {"name": "Hotel B", "price": 1700.0, "rating": 4.0, "available": True},
        {"name": "Hotel C", "price": 1300.0, "rating": 3.8, "available": True}
    ]
    return ToolResult(
        tool_name="search_hotels",
        success=True,
        data=data,
        message=f"Found hotels in {dst} (budget/night: ₹{safe_budget:.0f})"
    )

def check_weather(destination: str, travel_date: str) -> ToolResult:
    """Mock weather check."""
    dst = str(destination).strip() if destination else "Goa"
    return ToolResult(
        tool_name="check_weather",
        success=True,
        data={
            "condition": "Sunny",
            "temperature": 31,
            "suitable_for_outdoor": True
        },
        message=f"Weather in {dst} is Sunny"
    )

def find_activities(destination: str, preferences: List[str]) -> ToolResult:
    """Mock activity finder."""
    dst = str(destination).strip() if destination else "Goa"
    safe_prefs = [str(p).lower() for p in (preferences or [])]
    
    activities = ["Local sightseeing", "Museum"]
    if any("beach" in p for p in safe_prefs):
        activities.extend(["Baga Beach", "Fort Aguada", "Nature activities"])
    if any("vegetarian" in p for p in safe_prefs):
        activities.append("Vegetarian restaurants")
    
    return ToolResult(
        tool_name="find_activities",
        success=True,
        data=activities,
        message=f"Found activities based on preferences in {dst}"
    )

def calculate_budget(transport_cost: float, hotel_cost_per_night: float, duration: int, 
                     food_cost_per_day: float, activity_cost_total: float) -> ToolResult:
    """Calculate budget using exact Python arithmetic with input validation."""
    try:
        t_cost = max(0.0, float(transport_cost or 0.0))
        h_cost = max(0.0, float(hotel_cost_per_night or 0.0))
        days = max(1, int(duration or 1))
        f_cost = max(0.0, float(food_cost_per_day or 0.0))
        a_cost = max(0.0, float(activity_cost_total or 0.0))
    except (ValueError, TypeError):
        t_cost, h_cost, days, f_cost, a_cost = 0.0, 0.0, 1, 0.0, 0.0

    transport_total = t_cost
    hotel_total = h_cost * days
    food_total = f_cost * days
    activity_total = a_cost
    grand_total = transport_total + hotel_total + food_total + activity_total
    
    return ToolResult(
        tool_name="calculate_budget",
        success=True,
        data={
            "transport_total": transport_total,
            "hotel_total": hotel_total,
            "food_total": food_total,
            "activity_total": activity_total,
            "grand_total": grand_total
        },
        message="Calculated estimated budget"
    )

def book_transport(transport_details: Dict[str, Any]) -> ToolResult:
    """Simulated booking action (Demo / Sandbox)."""
    return ToolResult(
        tool_name="book_transport",
        success=True,
        data={"booking_id": "SIMULATED-BUS-001", "status": "CONFIRMED", "simulated": True},
        message="Simulated transport booking confirmed (no real funds charged)"
    )

def book_hotel(hotel_details: Dict[str, Any]) -> ToolResult:
    """Simulated booking action (Demo / Sandbox)."""
    return ToolResult(
        tool_name="book_hotel",
        success=True,
        data={"booking_id": "SIMULATED-HOTEL-002", "status": "CONFIRMED", "simulated": True},
        message="Simulated hotel booking confirmed (no real funds charged)"
    )

