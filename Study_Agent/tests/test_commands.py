import pytest
from Study_Agent.models import CommandType
from Study_Agent.commands import detect_command


def test_direct_commands():
    assert detect_command("hint") == CommandType.HINT
    assert detect_command("clue") == CommandType.HINT
    assert detect_command("skip") == CommandType.SKIP
    assert detect_command("pass") == CommandType.SKIP
    assert detect_command("explain") == CommandType.EXPLAIN
    assert detect_command("repeat") == CommandType.REPEAT
    assert detect_command("stop") == CommandType.STOP
    assert detect_command("quit") == CommandType.QUIT
    assert detect_command("exit") == CommandType.QUIT


def test_conversational_hint_phrases():
    assert detect_command("can I have a hint please?") == CommandType.HINT
    assert detect_command("give me a clue") == CommandType.HINT
    assert detect_command("I need a hint") == CommandType.HINT
    assert detect_command("any hints?") == CommandType.HINT


def test_conversational_skip_phrases():
    assert detect_command("can we skip this question") == CommandType.SKIP
    assert detect_command("I want to skip") == CommandType.SKIP
    assert detect_command("next question please") == CommandType.SKIP
    assert detect_command("I don't know") == CommandType.SKIP


def test_conversational_explain_phrases():
    assert detect_command("can you please explain the concept?") == CommandType.EXPLAIN
    assert detect_command("please explain") == CommandType.EXPLAIN
    assert detect_command("tell me more about this") == CommandType.EXPLAIN
    assert detect_command("I don't understand this concept") == CommandType.EXPLAIN


def test_conversational_repeat_phrases():
    assert detect_command("can you repeat the question?") == CommandType.REPEAT
    assert detect_command("say that again") == CommandType.REPEAT
    assert detect_command("what was the question?") == CommandType.REPEAT


def test_conversational_stop_and_quit():
    assert detect_command("stop the session") == CommandType.STOP
    assert detect_command("let's wrap up and generate report now") == CommandType.STOP
    assert detect_command("that's all for today") == CommandType.STOP
    assert detect_command("i want to exit") == CommandType.QUIT
    assert detect_command("bye") == CommandType.QUIT


def test_regular_answers_do_not_trigger_commands():
    # Technical answers containing words shouldn't mistakenly trigger commands unless intentional
    assert detect_command("A list is mutable while a tuple is immutable.") == CommandType.NONE
    assert detect_command("We can repeat string multiplication in Python with asterisks.") == CommandType.NONE
    assert detect_command("Inheritance allows child classes to reuse code.") == CommandType.NONE
    assert detect_command("") == CommandType.NONE
