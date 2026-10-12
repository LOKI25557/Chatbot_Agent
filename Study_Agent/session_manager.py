import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from student_profile import StudentProfile
    from answer_evaluator import EvaluationResult
    from report_generator import SessionReport


class CommandType(str, Enum):
    HINT = "hint"
    SKIP = "skip"
    EXPLAIN = "explain"
    REPEAT = "repeat"
    STOP = "stop"
    QUIT = "quit"
    NONE = "none"


# Precise regex patterns to detect intentional commands without matching technical answers
HINT_PATTERNS = [
    r"^(?:please\s+)?hints?(?:\s+please)?$",
    r"^(?:please\s+)?clues?(?:\s+please)?$",
    r"\b(?:give\s+me|need|can\s+i\s+(?:have|get)|could\s+you\s+give|provide|want)\s+(?:a\s+)?(?:hint|clue)\b",
    r"\b(?:any\s+hints?|hints?\s+please|clues?\s+please)\b",
]

SKIP_PATTERNS = [
    r"^(?:please\s+)?skip(?:\s+this|\s+question)?(?:\s+please)?$",
    r"\b(?:i\s+want\s+to\s+|can\s+we\s+|let\'?s\s+)?skip(?:\s+this\s+question|\s+it)?\b",
    r"^(?:pass|next|next\s+question)(?:\s+please)?$",
    r"\bnext\s+question(?:\s+please)?\b",
    r"\b(?:don\'?t\s+know|no\s+idea|i\s+pass|skip\s+this)\b",
]

EXPLAIN_PATTERNS = [
    r"^(?:please\s+)?explain(?:\s+this|\s+concept)?(?:\s+please)?$",
    r"\b(?:can\s+you\s+(?:please\s+)?|could\s+you\s+(?:please\s+)?|please\s+)explain(?:\s+the\s+concept|\s+this|\s+more|\s+in\s+detail)?\b",
    r"\bexplain\s+(?:the\s+concept|this|more|in\s+detail)\b",
    r"\b(?:tell\s+me\s+more(?:\s+about\s+this)?|teach\s+me\s+this|what\s+does\s+this\s+mean)\b",
    r"\b(?:i\s+don\'?t\s+understand\s+this\s+concept)\b",
]

REPEAT_PATTERNS = [
    r"^(?:please\s+)?repeat(?:\s+the\s+question|\s+question)?(?:\s+please)?$",
    r"\b(?:can\s+you\s+|could\s+you\s+|please\s+)repeat\s+(?:the\s+question|it)\b",
    r"\brepeat\s+the\s+question\b",
    r"\b(?:what\s+was\s+the\s+question|say\s+that\s+again|show\s+question\s+again)\b",
]

STOP_PATTERNS = [
    r"^(?:stop|finish|end)(?:\s+the\s+session|\s+session|\s+here|\s+now)?$",
    r"\b(?:stop\s+(?:the\s+)?session|end\s+(?:the\s+)?session|finish\s+(?:the\s+)?session)\b",
    r"\b(?:that\'?s\s+all(?:\s+for\s+today)?|let\'?s\s+wrap\s+up|wrap\s+up|generate\s+report\s+now|stop\s+here)\b",
]

QUIT_PATTERNS = [
    r"^(?:quit|exit|bye|goodbye|close)$",
    r"\b(?:quit\s+(?:the\s+)?session|exit\s+(?:the\s+)?session|i\s+want\s+to\s+exit|i\s+want\s+to\s+quit)\b",
]


def detect_command(text: str) -> CommandType:
    """
    Analyzes student input to check if it's an interactive control command
    (hint, skip, explain, repeat, stop, quit).
    Returns CommandType enum value or CommandType.NONE if it's an answer.
    """
    if not text:
        return CommandType.NONE

    cleaned = text.strip().lower()

    # Direct short commands
    if cleaned in ("hint", "clue"):
        return CommandType.HINT
    if cleaned in ("skip", "pass", "next"):
        return CommandType.SKIP
    if cleaned in ("explain", "explanation"):
        return CommandType.EXPLAIN
    if cleaned in ("repeat", "again"):
        return CommandType.REPEAT
    if cleaned in ("stop", "finish", "end"):
        return CommandType.STOP
    if cleaned in ("quit", "exit", "bye", "goodbye"):
        return CommandType.QUIT

    # Conversational phrases - check in priority order
    for pat in QUIT_PATTERNS:
        if re.search(pat, cleaned):
            return CommandType.QUIT

    for pat in STOP_PATTERNS:
        if re.search(pat, cleaned):
            return CommandType.STOP

    for pat in REPEAT_PATTERNS:
        if re.search(pat, cleaned):
            return CommandType.REPEAT

    for pat in EXPLAIN_PATTERNS:
        if re.search(pat, cleaned):
            return CommandType.EXPLAIN

    for pat in SKIP_PATTERNS:
        if re.search(pat, cleaned):
            return CommandType.SKIP

    for pat in HINT_PATTERNS:
        if re.search(pat, cleaned):
            return CommandType.HINT

    return CommandType.NONE


@dataclass
class QuestionItem:
    """Represents a single interview question and its interactive lifecycle state."""
    index: int
    question_text: str
    topic: str = ""
    difficulty: str = "medium"
    question_type: str = "conceptual"     # conceptual, coding, scenario, theory
    expected_concepts: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    student_answer: Optional[str] = None
    evaluation: Optional[Any] = None       # EvaluationResult
    follow_up_question: Optional[str] = None
    follow_up_answer: Optional[str] = None
    follow_up_evaluation: Optional[Any] = None
    skipped: bool = False
    hints_used: int = 0
    explanation_viewed: bool = False


class SessionManager:
    """
    Manages in-memory state and progress for an active study session.
    NOTE: All state is kept strictly in-memory during execution. No database is used.
    """

    def __init__(self, profile: "StudentProfile"):
        self.profile = profile
        self.questions: List[QuestionItem] = []
        self.current_index: int = 1
        self.is_active: bool = True
        self.is_partial: bool = False

    def add_question(self, question: QuestionItem):
        """Appends a new question to the session."""
        self.questions.append(question)

    def get_current_question(self) -> Optional[QuestionItem]:
        """Returns the current active QuestionItem or None."""
        if 0 < self.current_index <= len(self.questions):
            return self.questions[self.current_index - 1]
        return None

    def record_skip(self, question: QuestionItem):
        """Marks the current question as skipped without recording an evaluation score."""
        question.skipped = True
        question.student_answer = "[Skipped by student]"

    def record_answer_and_evaluation(
        self,
        question: QuestionItem,
        answer: str,
        evaluation: "EvaluationResult"
    ):
        """Records student answer and its evaluation."""
        question.student_answer = answer
        question.evaluation = evaluation
        question.skipped = False

    def record_follow_up(
        self,
        question: QuestionItem,
        follow_up_q: str,
        follow_up_a: str,
        follow_up_eval: Optional["EvaluationResult"] = None
    ):
        """Records follow-up question and answer."""
        question.follow_up_question = follow_up_q
        question.follow_up_answer = follow_up_a
        question.follow_up_evaluation = follow_up_eval

    def advance_to_next(self):
        """Increments current question index."""
        self.current_index += 1

    def end_session(self, early_stop: bool = False):
        """Finalizes the session, marking whether it was stopped early."""
        self.is_active = False
        if early_stop:
            self.is_partial = True
        elif self.current_index <= self.profile.num_questions:
            self.is_partial = True

    def get_progress(self) -> str:
        """Returns string like 'Question 2 of 5'."""
        idx = min(self.current_index, self.profile.num_questions)
        return f"Question {idx} of {self.profile.num_questions}"

    def generate_report(self) -> "SessionReport":
        """Builds the final performance report using report_generator."""
        from report_generator import build_session_report
        return build_session_report(self)
