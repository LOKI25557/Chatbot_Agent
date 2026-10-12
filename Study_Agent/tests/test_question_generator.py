import pytest
from Study_Agent.student_profile import StudentProfile
from Study_Agent.question_generator import QuestionGenerator, OFFLINE_QUESTIONS


def test_question_generator_python_offline():
    q_gen = QuestionGenerator()
    profile = StudentProfile(name="Student", subject="Python", difficulty="medium")
    q1 = q_gen._generate_offline(profile, current_index=1)

    assert q1.index == 1
    assert "list" in q1.question_text.lower() or "tuple" in q1.question_text.lower()
    assert len(q1.expected_concepts) > 0
    assert len(q1.hints) > 0


def test_question_generator_java_offline():
    q_gen = QuestionGenerator()
    profile = StudentProfile(name="Student", subject="Java", difficulty="medium")
    q1 = q_gen._generate_offline(profile, current_index=1)

    assert q1.index == 1
    assert "jdk" in q1.question_text.lower() or "jvm" in q1.question_text.lower() or "java" in q1.question_text.lower()


def test_question_generator_dbms_offline():
    q_gen = QuestionGenerator()
    profile = StudentProfile(name="Student", subject="DBMS and SQL", difficulty="easy")
    q1 = q_gen._generate_offline(profile, current_index=1)

    assert q1.index == 1
    assert "acid" in q1.question_text.lower()


def test_question_generator_unknown_subject_fallback():
    # An arbitrary subject like Quantum Computing should fall back to general templates without crashing
    q_gen = QuestionGenerator()
    profile = StudentProfile(name="Student", subject="Quantum Computing", topic="Qubits", difficulty="hard")
    q1 = q_gen._generate_offline(profile, current_index=1)

    assert q1.index == 1
    assert len(q1.question_text) > 20
    assert q1.topic == "Qubits"
    assert q1.difficulty == "hard"


def test_question_generator_multiple_question_rotation():
    q_gen = QuestionGenerator()
    profile = StudentProfile(name="Student", subject="Python", num_questions=3)

    q1 = q_gen._generate_offline(profile, current_index=1)
    q2 = q_gen._generate_offline(profile, current_index=2)
    q3 = q_gen._generate_offline(profile, current_index=3)

    assert q1.index == 1
    assert q2.index == 2
    assert q3.index == 3
    # Ensure distinct questions
    assert q1.question_text != q2.question_text
    assert q2.question_text != q3.question_text
