import logging
from typing import Optional, Dict, Any, List

from student_profile import StudentProfile
from session_manager import SessionManager, QuestionItem, CommandType, detect_command
from question_generator import QuestionGenerator
from answer_evaluator import AnswerEvaluator, EvaluationResult
from report_generator import SessionReport

logger = logging.getLogger(__name__)


class StudyAgent:
    """
    Core AI Study Agent orchestrating interactive tutoring, questioning,
    command handling, evaluation, and session reporting.
    """

    def __init__(
        self,
        question_generator: Optional[QuestionGenerator] = None,
        answer_evaluator: Optional[AnswerEvaluator] = None,
        llm_client: Optional[Any] = None  # Backwards compatibility with test fixtures
    ):
        # If legacy llm_client was passed, wrap its methods
        if llm_client is not None:
            self.q_gen = question_generator or llm_client
            self.evaluator = answer_evaluator or llm_client
        else:
            self.q_gen = question_generator or QuestionGenerator()
            self.evaluator = answer_evaluator or AnswerEvaluator()

        self.session: Optional[SessionManager] = None
        self.current_question: Optional[QuestionItem] = None
        self.in_follow_up: bool = False
        self.current_follow_up_text: Optional[str] = None

    def start_session(self, profile: StudentProfile):
        """Starts a new study session with the given student profile."""
        self.session = SessionManager(profile)
        self.in_follow_up = False
        self.current_follow_up_text = None

    def is_session_active(self) -> bool:
        """Returns True if the session is currently ongoing."""
        return self.session is not None and self.session.is_active

    def get_progress(self) -> str:
        """Returns string like 'Question 2 of 5'."""
        if not self.session:
            return "No active session"
        return self.session.get_progress()

    def next_question(self) -> Optional[QuestionItem]:
        """
        Retrieves or generates the next question for the student.
        Returns None if all questions have been completed.
        """
        if not self.session or not self.session.is_active:
            return None

        if self.session.current_index > self.session.profile.num_questions:
            self.session.end_session(early_stop=False)
            return None

        previous_texts = [q.question_text for q in self.session.questions]

        question = self.q_gen.generate_question(
            profile=self.session.profile,
            previous_questions=previous_texts,
            current_index=self.session.current_index
        )
        self.session.add_question(question)
        self.current_question = question
        self.in_follow_up = False
        self.current_follow_up_text = None
        return question

    def process_student_input(self, user_input: str) -> Dict[str, Any]:
        """
        Processes student input during the session:
        1. Checks for interactive commands (hint, skip, explain, repeat, stop, quit).
        2. Evaluates student answers using the 0-5 rubric.
        3. Manages optional follow-ups.
        """
        if not self.session or not self.current_question:
            return {"type": "error", "message": "No active question to respond to."}

        # 1. Detect interactive commands
        cmd = detect_command(user_input)

        if cmd == CommandType.QUIT:
            self.session.end_session(early_stop=True)
            return {
                "type": "quit",
                "message": "Session exited gracefully. Thank you for practicing with Study Agent!"
            }

        if cmd == CommandType.STOP:
            self.session.end_session(early_stop=True)
            report = self.session.generate_report()
            return {
                "type": "stop",
                "message": "Session stopped early at your request. Generating your partial report...",
                "report": report
            }

        if cmd == CommandType.SKIP:
            self.session.record_skip(self.current_question)
            self.session.advance_to_next()
            return {
                "type": "skip",
                "message": f"Question #{self.current_question.index} skipped. Moving to next topic."
            }

        if cmd == CommandType.REPEAT:
            return {
                "type": "repeat",
                "message": f"📌 Question #{self.current_question.index}:\n{self.current_question.question_text}"
            }

        if cmd == CommandType.HINT:
            self.current_question.hints_used += 1
            hint_text = self.evaluator.generate_hint(
                self.session.profile,
                self.current_question,
                hint_number=self.current_question.hints_used
            )
            return {
                "type": "hint",
                "message": hint_text
            }

        if cmd == CommandType.EXPLAIN:
            self.current_question.explanation_viewed = True
            explanation = self.evaluator.explain_concept(
                self.session.profile,
                self.current_question
            )
            return {
                "type": "explain",
                "message": explanation
            }

        # 2. Handle follow-up answer if currently in follow-up mode
        if self.in_follow_up and self.current_follow_up_text:
            follow_up_eval = self.evaluator.evaluate_answer(
                profile=self.session.profile,
                question=QuestionItem(
                    index=self.current_question.index,
                    question_text=self.current_follow_up_text,
                    topic=self.current_question.topic,
                    expected_concepts=self.current_question.expected_concepts
                ),
                student_answer=user_input
            )
            self.session.record_follow_up(
                self.current_question,
                self.current_follow_up_text,
                user_input,
                follow_up_eval
            )
            self.in_follow_up = False
            self.current_follow_up_text = None
            self.session.advance_to_next()
            return {
                "type": "follow_up_evaluation",
                "evaluation": follow_up_eval,
                "message": f"Follow-up evaluated: {follow_up_eval.score_label}. Moving to next question."
            }

        # 3. Regular answer evaluation
        evaluation: EvaluationResult = self.evaluator.evaluate_answer(
            profile=self.session.profile,
            question=self.current_question,
            student_answer=user_input
        )

        # Check if answer was too ambiguous and needs clarification
        if evaluation.is_clarification and evaluation.clarification_prompt:
            return {
                "type": "clarification",
                "message": evaluation.clarification_prompt,
                "preliminary_score": evaluation.score
            }

        # Record answer and evaluation
        self.session.record_answer_and_evaluation(
            self.current_question,
            user_input,
            evaluation
        )

        # Check if a follow-up question should be triggered
        follow_up = self.evaluator.generate_follow_up(
            profile=self.session.profile,
            question=self.current_question,
            student_answer=user_input,
            evaluation=evaluation
        )

        if follow_up:
            self.in_follow_up = True
            self.current_follow_up_text = follow_up
            return {
                "type": "evaluation",
                "evaluation": evaluation,
                "follow_up": follow_up,
                "message": "Answer evaluated. Follow-up question generated."
            }

        # Advance to next question
        self.session.advance_to_next()
        return {
            "type": "evaluation",
            "evaluation": evaluation,
            "message": "Answer evaluated. Moving to next question."
        }

    def finish_session(self) -> SessionReport:
        """Finishes active session and returns the structured report."""
        if not self.session:
            raise RuntimeError("No active session to finish.")
        self.session.end_session(early_stop=False)
        return self.session.generate_report()
