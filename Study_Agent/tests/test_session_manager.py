import pytest
from Study_Agent.student_profile import StudentProfile
from Study_Agent.session_manager import SessionManager, QuestionItem, CommandType
from Study_Agent.answer_evaluator import EvaluationResult
from Study_Agent.report_generator import build_session_report, format_report_cli


def test_session_manager_initialization():
    profile = StudentProfile(name="Aria", subject="Python", num_questions=3)
    sm = SessionManager(profile)

    assert sm.profile.name == "Aria"
    assert sm.is_active is True
    assert sm.is_partial is False
    assert sm.current_index == 1
    assert sm.get_progress() == "Question 1 of 3"
    assert sm.get_current_question() is None


def test_session_manager_progression_and_scoring():
    profile = StudentProfile(name="Lokesh", subject="Python", topic="Data Structures", num_questions=3)
    sm = SessionManager(profile)

    # Question 1: Answered with score 4
    q1 = QuestionItem(index=1, question_text="What is a list?", topic="Data Structures")
    sm.add_question(q1)
    eval1 = EvaluationResult(
        score=4,
        score_label="4/5",
        correctness="Correct",
        explanation="Accurate definition",
        missed_points=[]
    )
    sm.record_answer_and_evaluation(q1, "A mutable ordered collection.", eval1)
    sm.advance_to_next()

    assert sm.get_progress() == "Question 2 of 3"

    # Question 2: Skipped
    q2 = QuestionItem(index=2, question_text="What is a dict?", topic="Hash Tables")
    sm.add_question(q2)
    sm.record_skip(q2)
    sm.advance_to_next()

    assert sm.get_progress() == "Question 3 of 3"

    # Question 3: Answered with score 2
    q3 = QuestionItem(index=3, question_text="What is a set?", topic="Hash Sets")
    sm.add_question(q3)
    eval3 = EvaluationResult(
        score=2,
        score_label="2/5",
        correctness="Partially Correct",
        explanation="Partially correct",
        missed_points=["Unordered uniqueness"]
    )
    sm.record_answer_and_evaluation(q3, "A collection without duplicates.", eval3)
    sm.advance_to_next()

    sm.end_session(early_stop=False)
    report = sm.generate_report()

    # 2 questions attempted, 1 skipped
    assert report.questions_attempted == 2
    assert report.questions_completed == 2
    assert report.questions_skipped == 1
    # Total score = 4 + 2 = 6 out of 10
    assert report.total_score == 6
    assert report.max_possible_score == 10
    assert report.percentage == 60.0
    assert report.is_partial is False
    assert len(report.mistakes_summary) == 1

    cli_text = format_report_cli(report)
    assert "FINAL PERFORMANCE REPORT" in cli_text
    assert "Lokesh" in cli_text
    assert "6 / 10" in cli_text
    assert "60.0%" in cli_text


def test_session_manager_early_stop():
    profile = StudentProfile(name="Alex", subject="DBMS", num_questions=5)
    sm = SessionManager(profile)

    q1 = QuestionItem(index=1, question_text="What is ACID?", topic="Transactions")
    sm.add_question(q1)
    eval1 = EvaluationResult(
        score=5,
        score_label="5/5",
        correctness="Correct",
        explanation="Perfect explanation",
        missed_points=[]
    )
    sm.record_answer_and_evaluation(q1, "Atomicity, Consistency, Isolation, Durability", eval1)

    # Student stops at Question 1
    sm.end_session(early_stop=True)
    report = sm.generate_report()

    assert report.is_partial is True
    assert report.questions_completed == 1
    assert report.total_score == 5
    assert report.max_possible_score == 5
    assert report.percentage == 100.0

    cli_text = format_report_cli(report)
    assert "PARTIAL-SESSION PERFORMANCE REPORT" in cli_text


def test_session_manager_empty_session():
    profile = StudentProfile(name="Sam", subject="Java", num_questions=5)
    sm = SessionManager(profile)
    sm.end_session(early_stop=True)
    report = sm.generate_report()

    assert report.questions_attempted == 0
    assert report.total_score == 0
    assert report.max_possible_score == 0
    assert report.percentage == 0.0
    assert report.is_partial is True
