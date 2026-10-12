from student_profile import StudentProfile
from session_manager import QuestionItem, CommandType
from answer_evaluator import EvaluationResult
from report_generator import SessionReport

# Prevent cross-agent namespace collisions when running tests from root directory
try:
    from Travel_Agent.models import ToolResult, TravelRequest, TravelPlan, AgentState
except Exception:
    pass

__all__ = [
    "StudentProfile",
    "QuestionItem",
    "EvaluationResult",
    "SessionReport",
    "CommandType",
]
