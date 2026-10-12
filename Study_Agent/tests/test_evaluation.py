import pytest
from Study_Agent.student_profile import StudentProfile
from Study_Agent.session_manager import QuestionItem
from Study_Agent.answer_evaluator import (
    AnswerEvaluator,
    EvaluationResult,
    score_to_label,
    build_evaluation_from_dict,
    format_evaluation_summary,
    RUBRIC_MAP
)


def test_rubric_mapping():
    assert "0/5" in score_to_label(0)
    assert "1/5" in score_to_label(1)
    assert "2/5" in score_to_label(2)
    assert "3/5" in score_to_label(3)
    assert "4/5" in score_to_label(4)
    assert "5/5" in score_to_label(5)

    # Clamping out-of-range scores
    assert "0/5" in score_to_label(-5)
    assert "5/5" in score_to_label(99)


def test_build_evaluation_from_dict():
    data = {
        "score": 4,
        "correctness": "Correct",
        "explanation": "Clear explanation of immutability and memory optimization.",
        "missed_points": ["Hashability requirement for dictionary keys"],
        "suggested_answer": "Tuples cannot be changed after creation, whereas lists can.",
        "is_clarification": False
    }
    result = build_evaluation_from_dict(data)
    assert result.score == 4
    assert result.correctness == "Correct"
    assert "Hashability requirement" in result.missed_points[0]
    assert result.is_clarification is False


def test_build_evaluation_clamping_and_fallback():
    data = {
        "score": "invalid",
        "correctness": "Partially Correct",
        "missed_points": "Single string missed point"
    }
    result = build_evaluation_from_dict(data)
    assert result.score == 0
    assert result.missed_points == ["Single string missed point"]


def test_heuristic_evaluation_correct_answer():
    evaluator = AnswerEvaluator()
    profile = StudentProfile(name="Student", subject="Python")
    question = QuestionItem(
        index=1,
        question_text="What is the difference between a list and a tuple in Python?",
        topic="Data Types",
        expected_concepts=["Lists are mutable", "tuples are immutable"]
    )
    student_ans = "Lists are mutable so their items can change, while tuples are immutable and cannot be changed."
    result = evaluator._evaluate_heuristic(profile, question, student_ans)

    assert result.score >= 4
    assert result.correctness == "Correct"
    assert "explanation" in result.explanation.lower() or len(result.explanation) > 0


def test_heuristic_evaluation_partial_answer():
    evaluator = AnswerEvaluator()
    profile = StudentProfile(name="Student", subject="Python")
    question = QuestionItem(
        index=1,
        question_text="Explain Python memory management.",
        topic="Memory",
        expected_concepts=["Reference counting", "Generational cyclic garbage collector"]
    )
    student_ans = "Python uses reference counting to track object references, but it also has a cyclic garbage collector."
    result = evaluator._evaluate_heuristic(profile, question, student_ans)

    assert result.score in (3, 4, 5)
    assert result.correctness in ("Correct", "Partially Correct")


def test_heuristic_evaluation_empty_answer():
    evaluator = AnswerEvaluator()
    profile = StudentProfile(name="Student", subject="Python")
    question = QuestionItem(
        index=1,
        question_text="Explain Python memory management.",
        expected_concepts=["Reference counting"]
    )
    result = evaluator.evaluate_answer(profile, question, "")
    assert result.score == 0
    assert result.correctness == "Incorrect"


def test_hint_generation():
    evaluator = AnswerEvaluator()
    profile = StudentProfile(name="Student", subject="Python")
    question = QuestionItem(
        index=1,
        question_text="What is a decorator?",
        topic="Functions",
        hints=["Think of wrapper functions that take *args."]
    )
    hint = evaluator.generate_hint(profile, question, hint_number=1)
    assert "wrapper functions" in hint
    assert "💡" in hint


def test_concept_explanation():
    evaluator = AnswerEvaluator()
    profile = StudentProfile(name="Student", subject="Python")
    question = QuestionItem(
        index=1,
        question_text="What is a decorator?",
        topic="Functions",
        expected_concepts=["First-class functions", "Wrapper"]
    )
    explanation = evaluator.explain_concept(profile, question)
    assert "Functions" in explanation or "Python" in explanation
    assert len(explanation) > 20


def test_format_evaluation_summary():
    eval_res = EvaluationResult(
        score=3,
        score_label="3/5 - Mostly correct",
        correctness="Partially Correct",
        explanation="Understood mutable vs immutable.",
        missed_points=["Did not mention tuple hashing"],
        suggested_answer="A list uses dynamic arrays."
    )
    summary = format_evaluation_summary(eval_res)
    assert "Partially Correct" in summary
    assert "3/5 - Mostly correct" in summary
    assert "Did not mention tuple hashing" in summary
    assert "A list uses dynamic arrays." in summary
