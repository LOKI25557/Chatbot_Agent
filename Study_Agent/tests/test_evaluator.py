import pytest
from Study_Agent.evaluator import score_to_label, build_evaluation_from_dict, format_evaluation_summary
from Study_Agent.models import EvaluationResult


def test_score_to_label():
    assert "0/5" in score_to_label(0)
    assert "3/5" in score_to_label(3)
    assert "5/5" in score_to_label(5)
    # Clamping
    assert "0/5" in score_to_label(-2)
    assert "5/5" in score_to_label(10)


def test_build_evaluation_from_dict():
    raw_data = {
        "score": 4,
        "correctness": "Correct",
        "explanation": "Clear and accurate definition of immutability.",
        "missed_points": ["Memory efficiency comparison"],
        "suggested_answer": "Tuples are immutable sequences in Python.",
        "is_clarification": False
    }
    result = build_evaluation_from_dict(raw_data)
    assert result.score == 4
    assert result.correctness == "Correct"
    assert "Memory efficiency comparison" in result.missed_points
    assert result.is_clarification is False


def test_build_evaluation_clamping_and_types():
    raw_data = {
        "score": "invalid",
        "missed_points": "Single string missed point",
        "explanation": "Test explanation"
    }
    result = build_evaluation_from_dict(raw_data)
    assert result.score == 0
    assert result.missed_points == ["Single string missed point"]


def test_format_evaluation_summary():
    eval_res = EvaluationResult(
        score=3,
        score_label="3/5 - Mostly correct",
        correctness="Partially Correct",
        explanation="Understood mutable vs immutable.",
        missed_points=["Did not mention tuple hashing"],
        suggested_answer="A list uses dynamic arrays."
    )
    text = format_evaluation_summary(eval_res)
    assert "Partially Correct" in text
    assert "3/5 - Mostly correct" in text
    assert "Did not mention tuple hashing" in text
    assert "A list uses dynamic arrays." in text
