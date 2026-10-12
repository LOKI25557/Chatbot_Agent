from typing import List, Optional, Dict, Any

from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, is_groq_configured
from student_profile import StudentProfile
from session_manager import QuestionItem
from answer_evaluator import EvaluationResult, AnswerEvaluator
from question_generator import QuestionGenerator, OFFLINE_QUESTIONS


class LLMClient:
    """
    Unified AI client interface coordinating question generation and answer evaluation.
    Provides backwards compatibility for test mocks.
    """

    def __init__(self):
        self.q_gen = QuestionGenerator()
        self.evaluator = AnswerEvaluator()

    def generate_question(
        self,
        profile: StudentProfile,
        previous_questions: List[str],
        current_index: int
    ) -> QuestionItem:
        return self.q_gen.generate_question(profile, previous_questions, current_index)

    def evaluate_answer(
        self,
        profile: StudentProfile,
        question: QuestionItem,
        student_answer: str
    ) -> EvaluationResult:
        return self.evaluator.evaluate_answer(profile, question, student_answer)

    def generate_hint(
        self,
        profile: StudentProfile,
        question: QuestionItem,
        hint_number: int = 1
    ) -> str:
        return self.evaluator.generate_hint(profile, question, hint_number)

    def explain_concept(
        self,
        profile: StudentProfile,
        question: QuestionItem
    ) -> str:
        return self.evaluator.explain_concept(profile, question)

    def generate_follow_up(
        self,
        profile: StudentProfile,
        question: QuestionItem,
        student_answer: str,
        evaluation: EvaluationResult
    ) -> Optional[str]:
        return self.evaluator.generate_follow_up(profile, question, student_answer, evaluation)
