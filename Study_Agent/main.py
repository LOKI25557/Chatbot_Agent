import sys
from pathlib import Path

# Ensure Study_Agent directory is in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Ensure Windows PowerShell and cmd handle UTF-8 cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import is_groq_configured, verify_groq_connection, GROQ_MODEL
from student_profile import StudentProfile, collect_student_profile_interactive
from agent import StudyAgent
from report_generator import format_report_cli
from answer_evaluator import format_evaluation_summary


def print_banner():
    banner = r"""
======================================================================
           🎓 AI STUDY AGENT & TECHNICAL INTERVIEWER 🎓           
======================================================================
  Interactive AI Tutor for Subjects, Exams & Interview Preparation
----------------------------------------------------------------------
"""
    print(banner)


def display_provider_status():
    if is_groq_configured():
        ok, msg = verify_groq_connection()
        if ok:
            print(f"🟢 LLM Provider: Active (Groq - {GROQ_MODEL})")
        else:
            print(f"🟡 LLM Provider: Configured but offline ({msg}). Using deterministic fallback.")
    else:
        print("🟡 LLM Provider: Demo / Offline Mode active (GROQ_API_KEY not found in .env).")
    print("----------------------------------------------------------------------\n")


def print_command_cheat_sheet():
    print("\n💡 Interactive Commands during practice:")
    print("   • 'hint'     : Get a clue without revealing the answer")
    print("   • 'skip'     : Skip current question and continue")
    print("   • 'explain'  : Deep explanation of the relevant concept")
    print("   • 'repeat'   : Re-read the current question")
    print("   • 'stop'     : End session early and generate partial report")
    print("   • 'quit'     : Exit the session immediately")
    print("-" * 70 + "\n")


def run_session_loop(agent: StudyAgent):
    """Conducts the interview loop question by question."""
    print("\n🚀 Starting your study session! Best of luck.\n")
    print_command_cheat_sheet()

    while agent.is_session_active():
        question = agent.next_question()
        if not question:
            break

        # Display Question header
        print("=" * 70)
        progress = agent.get_progress()
        print(f"📌 {progress} | Topic: {question.topic} | Difficulty: {question.difficulty.title()}")
        print("-" * 70)
        print(f"\n{question.question_text}\n")
        print("-" * 70)

        # Inner loop for the current question (handles multiple hints/explains before answering)
        while True:
            try:
                user_input = input("✍️ Your Answer (or type a command): ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\nSession interrupted by user.")
                agent.session.end_session(early_stop=True)
                report = agent.session.generate_report()
                print(format_report_cli(report))
                return

            if not user_input:
                print("⚠️ Please provide an answer or type a command like 'hint', 'skip', or 'stop'.")
                continue

            result = agent.process_student_input(user_input)
            res_type = result.get("type")

            if res_type == "quit":
                print(f"\n👋 {result.get('message')}")
                return

            if res_type == "stop":
                print(f"\n⏹️ {result.get('message')}")
                report = result.get("report")
                if report:
                    print(format_report_cli(report))
                return

            if res_type == "skip":
                print(f"\n⏭️ {result.get('message')}\n")
                break

            if res_type == "hint":
                print(f"\n{result.get('message')}\n")
                continue

            if res_type == "explain":
                print(f"\n{result.get('message')}\n")
                continue

            if res_type == "repeat":
                print(f"\n{result.get('message')}\n")
                continue

            if res_type == "clarification":
                print(f"\n🤔 Clarification: {result.get('message')}")
                continue

            if res_type == "evaluation":
                evaluation = result.get("evaluation")
                print("\n" + "-" * 70)
                print("📊 EVALUATION FEEDBACK:")
                print(format_evaluation_summary(evaluation))
                print("-" * 70)

                # Check if follow-up question was triggered
                follow_up = result.get("follow_up")
                if follow_up:
                    print(f"\n🎯 Follow-up Question:\n{follow_up}\n")
                    follow_up_input = input("✍️ Your Follow-up Answer: ").strip()
                    if follow_up_input:
                        fu_result = agent.process_student_input(follow_up_input)
                        fu_eval = fu_result.get("evaluation")
                        if fu_eval:
                            print(f"\n📊 Follow-up Assessment: {fu_eval.score_label}")
                            print(f"Feedback: {fu_eval.explanation}\n")
                break

            if res_type == "error":
                print(f"⚠️ Error: {result.get('message')}")
                break

    # Session completed normally
    report = agent.finish_session()
    print(format_report_cli(report))


def main():
    print_banner()
    display_provider_status()

    # Step 1: Collect student profile conversationally
    profile = collect_student_profile_interactive()
    if not profile:
        print("\n👋 Goodbye! Have a great day.\n")
        return

    # Step 2: Initialize Agent and start session
    agent = StudyAgent()
    agent.start_session(profile)

    # Step 3: Run interactive interview flow
    run_session_loop(agent)


if __name__ == "__main__":
    main()
