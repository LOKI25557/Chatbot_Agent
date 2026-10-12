import pytest
from Study_Agent.student_profile import StudentProfile


def test_student_profile_defaults():
    profile = StudentProfile()
    assert profile.name == "Student"
    assert profile.education_level == "undergraduate"
    assert profile.course_branch == ""
    assert profile.year_semester == ""
    assert profile.subject == "Python"
    assert profile.topic == ""
    assert profile.knowledge_level == "beginner"
    assert profile.purpose == "general_learning"
    assert profile.difficulty == "medium"
    assert profile.num_questions == 5

    valid, msg = profile.validate()
    assert valid is True


def test_student_profile_validation():
    # Empty name should default to 'Student'
    p1 = StudentProfile(name="", subject="Java")
    valid, _ = p1.validate()
    assert valid is True
    assert p1.name == "Student"

    # Empty subject should fail
    p2 = StudentProfile(subject="")
    valid, msg = p2.validate()
    assert valid is False
    assert "Subject cannot be empty" in msg

    # Invalid question count should fail
    p3 = StudentProfile(subject="C++", num_questions=0)
    valid, msg = p3.validate()
    assert valid is False

    p4 = StudentProfile(subject="C++", num_questions=25)
    valid, msg = p4.validate()
    assert valid is False

    # Out-of-bounds difficulty defaults to medium
    p5 = StudentProfile(subject="SQL", difficulty="super_hard")
    valid, _ = p5.validate()
    assert valid is True
    assert p5.difficulty == "medium"


def test_student_profile_summary():
    profile = StudentProfile(
        name="Vikram",
        education_level="undergraduate",
        course_branch="Computer Science",
        year_semester="3rd Year",
        subject="DBMS",
        topic="Transactions & Concurrency",
        knowledge_level="intermediate",
        purpose="placement_interview",
        difficulty="hard",
        num_questions=7
    )
    summary = profile.summary()
    assert "Vikram" in summary
    assert "Computer Science" in summary
    assert "3rd Year" in summary
    assert "DBMS" in summary
    assert "Transactions & Concurrency" in summary
    assert "Placement Interview" in summary
    assert "Hard" in summary
    assert "7" in summary


def test_school_student_profile_skips_college_fields():
    profile = StudentProfile(
        name="Ananya",
        education_level="school",
        course_branch="",
        year_semester="",
        subject="Physics",
        topic="Mechanics",
        difficulty="easy",
        num_questions=3
    )
    valid, _ = profile.validate()
    assert valid is True
    summary = profile.summary()
    assert "Ananya" in summary
    assert "School" in summary
    assert "Physics" in summary
