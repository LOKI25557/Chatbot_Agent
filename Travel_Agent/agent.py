import time
import memory
from models import TravelRequest, AgentState
from planner import Planner
from llm import parse_travel_request, generate_reasoning
import tools

class TravelAgent:
    def __init__(self, force_failure: bool = False):
        self.state = AgentState()
        self.force_failure = force_failure
        self.planner = None
    
    def log_execution(self, step: str, message: str):
        self.state.execution_log.append({"step": step, "message": message})
        self.state.current_step = step
    
    def run(self, user_request_text: str):
        """Execute the main agent lifecycle up to human approval."""
        self.state.user_request = user_request_text
        
        # 1. Goal Identification
        self.identify_goal(user_request_text)
        
        # 2. Load Memory
        self.load_memory()
        
        # 3. Create Plan (includes tool execution for search)
        self.create_plan()
        
        # 4. Observe and Validate
        self.observe_and_reason()
        
        # 5. Request Human Approval
        self.request_human_approval()
    
    def identify_goal(self, text: str):
        self.log_execution("GOAL", f"Extracting goal from: '{text}'")
        parsed = parse_travel_request(text)
        
        try:
            dur = max(1, int(parsed.get("duration_days", 1)))
        except (ValueError, TypeError):
            dur = 1

        try:
            bud = max(0.0, float(parsed.get("budget", 0.0)))
        except (ValueError, TypeError):
            bud = 0.0

        try:
            num_trav = max(1, int(parsed.get("travelers", 1)))
        except (ValueError, TypeError):
            num_trav = 1

        self.state.goal = TravelRequest(
            source=str(parsed.get("source", "Bengaluru")),
            destination=str(parsed.get("destination", "Goa")),
            duration_days=dur,
            budget=bud,
            travel_date=str(parsed.get("travel_date", "Next Week")),
            preferences=list(parsed.get("preferences", [])),
            travelers=num_trav
        )
        self.log_execution("GOAL", f"{self.state.goal.duration_days}-day {self.state.goal.destination} trip under ₹{self.state.goal.budget:.0f}")

    def load_memory(self):
        mem = memory.load_memory()
        self.state.memory = mem
        prefs = f"Prefers {mem.get('preferred_transport')}, {mem.get('preferred_food')} food"
        self.log_execution("MEMORY", prefs)

    def create_plan(self):
        self.log_execution("PLANNING", "Creating initial travel plan")
        self.planner = Planner(self.state.memory, force_failure=self.force_failure)
        
        # Simulate tool selection and execution visually in logs
        self.log_execution("TOOL", "search_transport()")
        self.log_execution("OBSERVATION", "Transport options found")
        
        self.log_execution("TOOL", "search_hotels()")
        if self.force_failure:
            self.log_execution("OBSERVATION", "Hotel A unavailable")
        else:
            self.log_execution("OBSERVATION", "Hotels found")
            
        self.state.plan = self.planner.create_initial_plan(self.state.goal)

    def observe_and_reason(self):
        is_feasible, issue = self.planner.validate_plan(self.state.goal)
        
        if not is_feasible:
            self.log_execution("OBSERVATION", issue)
            
            # Reasoning
            explanation = generate_reasoning("Initial plan validation failed", issue)
            self.log_execution("REASONING", explanation)
            
            # Re-planning
            self.log_execution("RE-PLANNING", "Searching alternatives")
            self.state.plan = self.planner.replan(self.state.goal, issue)
            
            is_feasible, new_issue = self.planner.validate_plan(self.state.goal)
            if is_feasible:
                self.log_execution("NEW PLAN", f"Selected {self.state.plan.hotel.get('name')} (Feasible)")
            else:
                self.state.plan.status = "FAILED"
                self.log_execution("RE-PLANNING FAILED", f"No feasible plan found: {new_issue}")
            
        self.log_execution("BUDGET", f"₹{self.state.plan.estimated_total_cost:.0f}")

    def request_human_approval(self):
        if self.state.plan and self.state.plan.status == "FAILED":
            self.state.requires_human_approval = False
            self.state.action_status = "ABORTED_INFEASIBLE"
            self.log_execution("TERMINATION", "Halting execution: Plan is infeasible and cannot be booked.")
            return

        self.state.requires_human_approval = True
        self.log_execution("HUMAN APPROVAL", "Waiting for user confirmation")

    def reject_action(self, reason: str = "User rejected the plan."):
        """Handle human rejection of the proposed plan."""
        self.state.requires_human_approval = False
        self.state.action_status = "REJECTED"
        self.log_execution("HUMAN REJECTION", f"Booking cancelled: {reason}")

    def execute_action(self):
        """Execute final simulated actions after human approval."""
        if not self.state.requires_human_approval and self.state.action_status != "NONE":
            return
            
        self.log_execution("ACTION", "User approved. Executing simulated bookings...")
        
        t_res = tools.book_transport(self.state.plan.transport)
        self.log_execution("TOOL", f"{t_res.tool_name}() -> {t_res.data.get('status')} ({t_res.data.get('booking_id')})")
        
        h_res = tools.book_hotel(self.state.plan.hotel)
        self.log_execution("TOOL", f"{h_res.tool_name}() -> {h_res.data.get('status')} ({h_res.data.get('booking_id')})")
        
        self.state.requires_human_approval = False
        self.state.action_status = "COMPLETED"
        self.update_memory()
        
    def update_memory(self):
        # Save trip to history
        trip_data = {
            "destination": self.state.goal.destination,
            "date": self.state.goal.travel_date,
            "cost": self.state.plan.estimated_total_cost
        }
        memory.add_trip_history(trip_data)
        self.log_execution("MEMORY UPDATE", f"Saved {self.state.goal.destination} trip to persistent history.")

