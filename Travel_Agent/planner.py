from models import TravelRequest, TravelPlan
import tools

class Planner:
    def __init__(self, memory_data: dict, force_failure: bool = False):
        self.memory = memory_data
        self.force_failure = force_failure
        self.plan = TravelPlan()

    def create_initial_plan(self, request: TravelRequest) -> TravelPlan:
        """Create a plan based on the request and memory."""
        self.plan.destination = request.destination
        self.plan.duration_days = max(1, int(request.duration_days or 1))

        # Search Tools
        safe_duration = max(1, self.plan.duration_days)
        budget_per_night = (request.budget / safe_duration) if request.budget > 0 else 3000.0
        transports = tools.search_transport(request.source, request.destination, request.travel_date).data
        hotels = tools.search_hotels(request.destination, budget_per_night, force_failure=self.force_failure).data
        weather = tools.check_weather(request.destination, request.travel_date).data
        activities = tools.find_activities(request.destination, request.preferences).data

        # Select transport (prioritize preferred transport or cheapest)
        pref_transport = str(self.memory.get("preferred_transport", "bus")).lower()
        selected_transport = next((t for t in transports if t["type"].lower() == pref_transport and t["available"]), transports[0])
        
        # Select hotel (pick first one for initial plan)
        selected_hotel = hotels[0]

        self.plan.transport = selected_transport
        self.plan.hotel = selected_hotel
        self.plan.weather = weather
        self.plan.activities = activities
        
        # Calculate budget
        self._calculate_and_set_budget(request)
        return self.plan

    def _calculate_and_set_budget(self, request: TravelRequest):
        # Assume estimated baseline costs
        food_cost_per_day = 500.0
        activity_cost_total = 1000.0
        budget_res = tools.calculate_budget(
            transport_cost=self.plan.transport.get("price", 0.0),
            hotel_cost_per_night=self.plan.hotel.get("price", 0.0),
            duration=self.plan.duration_days,
            food_cost_per_day=food_cost_per_day,
            activity_cost_total=activity_cost_total
        )
        
        self.plan.estimated_food_cost = budget_res.data["food_total"]
        self.plan.estimated_activity_cost = budget_res.data["activity_total"]
        self.plan.estimated_total_cost = budget_res.data["grand_total"]

    def validate_plan(self, request: TravelRequest) -> tuple[bool, str]:
        """Check if plan is feasible based on availability and budget."""
        if not self.plan.transport.get("available", False):
            return False, "Transport is unavailable."
        
        if not self.plan.hotel.get("available", False):
            return False, f"Hotel {self.plan.hotel.get('name')} is unavailable."

        if self.plan.estimated_total_cost > request.budget:
            return False, f"Estimated cost (₹{self.plan.estimated_total_cost:.0f}) exceeds budget (₹{request.budget:.0f})."
        
        return True, "Plan is feasible."

    def replan(self, request: TravelRequest, issue: str) -> TravelPlan:
        """Handle replanning logic when validation fails."""
        safe_duration = max(1, self.plan.duration_days)
        budget_per_night = (request.budget / safe_duration) if request.budget > 0 else 3000.0

        if "Hotel" in issue and "unavailable" in issue:
            # Replan by selecting a different hotel
            hotels = tools.search_hotels(request.destination, budget_per_night, force_failure=False).data
            available_hotels = [h for h in hotels if h["available"] and h["name"] != self.plan.hotel.get("name")]
            if available_hotels:
                self.plan.hotel = available_hotels[0]
                self.plan.reasoning = f"Switched to {self.plan.hotel['name']} due to previous hotel unavailability."
            else:
                self.plan.status = "FAILED"
                self.plan.reasoning = "No alternative hotels available."
                return self.plan

        if "budget" in issue.lower() or "exceeds" in issue.lower():
            # Fallback to cheaper transport and hotel
            transports = tools.search_transport(request.source, request.destination, request.travel_date).data
            available_transports = [t for t in transports if t["available"]]
            if available_transports:
                cheapest_transport = min(available_transports, key=lambda x: x["price"])
                self.plan.transport = cheapest_transport

            hotels = tools.search_hotels(request.destination, budget_per_night, force_failure=False).data
            available_hotels = [h for h in hotels if h["available"]]
            if available_hotels:
                cheapest_hotel = min(available_hotels, key=lambda x: x["price"])
                self.plan.hotel = cheapest_hotel

            self.plan.reasoning = "Switched to lowest-cost transport and hotel to fit budget."

        # Recalculate
        self._calculate_and_set_budget(request)
        
        # Check if plan now fits budget
        if self.plan.estimated_total_cost > request.budget:
            self.plan.status = "FAILED"
            self.plan.reasoning = f"No feasible plan: estimated cost ₹{self.plan.estimated_total_cost:.0f} exceeds budget ₹{request.budget:.0f} even after selecting lowest-cost options."
        else:
            self.plan.status = "RE-PLANNED"

        return self.plan


    def generate_itinerary(self) -> str:
        """Generate a simple day-by-day itinerary string."""
        itinerary = f"DAY 1\n- Transport to {self.plan.destination}\n- {self.plan.hotel.get('name', 'Hotel')} check-in\n"
        if self.plan.activities:
            itinerary += f"- {self.plan.activities[0]}\n"
        
        for day in range(2, self.plan.duration_days):
            itinerary += f"\nDAY {day}\n"
            acts = self.plan.activities[1:] if len(self.plan.activities) > 1 else self.plan.activities
            for act in acts:
                itinerary += f"- {act}\n"
        
        itinerary += f"\nDAY {self.plan.duration_days}\n- Morning sightseeing\n- Return transport\n"
        return itinerary
