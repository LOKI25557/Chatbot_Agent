import pytest
from Study_Agent.models import StudentProfile, QuestionItem, EvaluationResult
from Study_Agent.llm import LLMClient
from Study_Agent.agent import StudyAgent


class MockLLM(LLMClient):
    """Deterministic Mock LLM for hermetic unit testing without network or API keys."""

    def __init__(self):
        super().__init__()

    def generate_question(self, profile, previous_questions, current_index):
        return QuestionItem(
            index=current_index,
            question_text=f"Mock Question #{current_index} for {profile.subject}",
            topic=profile.topic or "Fundamentals",
            difficulty=profile.difficulty,
            question_type="conceptual",
            expected_concepts=["Key concept A", "Key concept B"],
            hints=["Think about concept A", "Consider concept B"]
        )

    def evaluate_answer(self, profile, question, student_answer):
        return EvaluationResult(
            score=4,
            score_label="4/5 - Correct and well explained",
            correctness="Correct",
            explanation="Good explanation of concept.",
            missed_points=["Minor detail"],
            suggested_answer="A complete answer involves concept A and B."
        )

    def generate_hint(self, profile, question, hint_number=1):
        return f"Mock hint #{hint_number} for {question.topic}"

    def explain_concept(self, profile, question):
        return f"Mock detailed explanation for {question.topic}"

    def generate_follow_up(self, profile, question, student_answer, evaluation):
        return None


def test_agent_full_flow():
    profile = StudentProfile(
        name="Tester",
        subject="Python",
        topic="OOP",
        difficulty="medium",
        num_questions=2
    )
    agent = StudyAgent(llm_client=MockLLM())
    agent.start_session(profile)

    assert agent.is_session_active() is True
    assert agent.get_progress() == "Question 1 of 2"

    # Fetch Q1
    q1 = agent.next_question()
    assert q1 is not None
    assert q1.index == 1
    assert "Mock Question #1" in q1.question_text

    # Student requests a hint
    hint_res = agent.process_student_input("can you give me a hint?")
    assert hint_res["type"] == "hint"
    assert "Mock hint #1" in hint_res["message"]

    # Student requests an explanation
    expl_res = agent.process_student_input("please explain this")
    assert expl_res["type"] == "explain"
    assert "Mock detailed explanation" in expl_res["message"]

    # Student requests repetition
    repeat_res = agent.process_student_input("repeat")
    assert repeat_res["type"] == "repeat"
    assert q1.question_text in repeat_res["message"]

    # Student answers Q1
    ans_res = agent.process_student_input("Classes are blueprints for objects.")
    assert ans_res["type"] == "evaluation"
    assert ans_res["evaluation"].score == 4

    # Fetch Q2
    q2 = agent.next_question()
    assert q2 is not None
    assert q2.index == 2

    # Student skips Q2
    skip_res = agent.process_student_input("skip this question")
    assert skip_res["type"] == "skip"

    # Finish session
    report = agent.finish_session()
    assert report.questions_attempted == 1
    assert report.questions_skipped == 1
    assert report.total_score == 4
    assert report.max_possible_score == 5
    assert report.percentage == 80.0


def test_agent_early_stop():
    profile = StudentProfile(name="EarlyBird", subject="SQL", num_questions=5)
    agent = StudyAgent(llm_client=MockLLM())
    agent.start_session(profile)

    agent.next_question()
    stop_res = agent.process_student_input("stop the session")
    assert stop_res["type"] == "stop"
    assert stop_res["report"].is_partial is True
    assert agent.is_session_active() is False


def test_agent_quit():
    profile = StudentProfile(name="Quitter", subject="Java", num_questions=3)
    agent = StudyAgent(llm_client=MockLLM())
    agent.start_session(profile)

    agent.next_question()
    quit_res = agent.process_student_input("quit")
    assert quit_res["type"] == "quit"
    assert agent.is_session_active() is False
