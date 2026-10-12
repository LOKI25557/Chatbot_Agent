import sys
from pathlib import Path

# Ensure Study_Agent is in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import streamlit as st
from config import is_groq_configured, verify_groq_connection, GROQ_MODEL
from models import StudentProfile
from agent import StudyAgent
from session import format_report_cli

st.set_page_config(page_title="AI Study Agent", page_icon="🎓", layout="wide")


@st.cache_data(ttl=60)
def check_groq_status():
    return verify_groq_connection()


def render_sidebar():
    with st.sidebar:
        st.title("🎓 Study Agent")
        st.caption("Interactive AI Tutor & Technical Interviewer")

        st.divider()
        st.subheader("🤖 AI Model Status")
        if is_groq_configured():
            is_live, status_msg = check_groq_status()
            if is_live:
                st.success("🟢 GROQ LLM ACTIVE")
                st.caption(f"Model: {GROQ_MODEL}")
            else:
                st.warning("🟡 GROQ CONFIGURED (OFFLINE)")
                st.caption(f"{status_msg}. Deterministic offline tutor active.")
        else:
            st.warning("🟡 DEMO / OFFLINE MODE")
            st.caption("No API key detected. Using deterministic fallback questions.")

        st.divider()
        st.subheader("💡 Interactive Commands")
        st.markdown(
            """
            Type these into the answer box or click the action buttons:
            - **`hint`**: Receive a helpful clue
            - **`skip`**: Skip current question
            - **`explain`**: Explain concept in depth
            - **`repeat`**: Re-read the current question
            - **`stop`**: End session & get report
            - **`quit`**: Exit session
            """
        )

        st.divider()
        st.caption("🔒 All session state is stored in-memory and resets on page reload.")


def init_session_state():
    if "stage" not in st.session_state:
        st.session_state.stage = "CONFIG"  # CONFIG -> CONFIRM -> INTERVIEW -> REPORT
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "profile" not in st.session_state:
        st.session_state.profile = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "final_report" not in st.session_state:
        st.session_state.final_report = None


def render_config_form():
    st.header("👋 Welcome! Set Up Your Study Session")
    st.write("Configure your personalized subject practice, exam prep, or technical interview.")

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("1. Your Name / Preferred Name", value="Student")
            edu_level = st.selectbox(
                "2. Education Level",
                options=["undergraduate", "postgraduate", "diploma", "school", "other"],
                format_func=lambda x: {
                    "undergraduate": "Undergraduate (B.Tech / B.Sc / BCA)",
                    "postgraduate": "Postgraduate (M.Tech / M.Sc / MCA)",
                    "diploma": "Diploma",
                    "school": "School (K-12)",
                    "other": "Other / Professional"
                }[x]
            )

            branch = ""
            semester = ""
            if edu_level in ("undergraduate", "postgraduate", "diploma"):
                branch = st.text_input("3. Course & Branch / Major (Optional)", placeholder="e.g. Computer Science, Mechanical")
                semester = st.text_input("4. Current Year / Semester (Optional)", placeholder="e.g. 3rd Year / 6th Semester")

            subject = st.text_input("5. Subject to Practice", value="Python", placeholder="e.g., Python, DSA, DBMS, Java, OS")

        with col2:
            topic = st.text_input("6. Specific Topic (Optional)", placeholder="e.g., OOP, Trees, Joins, Threads (Leave blank for full subject)")
            knowledge_lvl = st.select_slider("7. Current Knowledge Level", options=["beginner", "intermediate", "advanced"], value="beginner")
            purpose = st.selectbox(
                "8. Session Purpose",
                options=["general_learning", "exam_prep", "placement_interview", "technical_interview", "revision"],
                format_func=lambda x: {
                    "general_learning": "General Learning & Practice",
                    "exam_prep": "College / School Exam Preparation",
                    "placement_interview": "Campus / Placement Interview",
                    "technical_interview": "Technical Job Interview",
                    "revision": "Quick Concept Revision"
                }[x]
            )
            difficulty = st.select_slider("9. Preferred Difficulty", options=["easy", "medium", "hard"], value="medium")
            num_q = st.slider("10. Number of Questions", min_value=1, max_value=15, value=5)

        submit = st.form_submit_button("Review Session Settings", type="primary", use_container_width=True)

        if submit:
            st.session_state.profile = StudentProfile(
                name=name.strip() or "Student",
                education_level=edu_level,
                course_branch=branch.strip(),
                year_semester=semester.strip(),
                subject=subject.strip() or "Python",
                topic=topic.strip(),
                knowledge_level=knowledge_lvl,
                purpose=purpose,
                difficulty=difficulty,
                num_questions=num_q
            )
            st.session_state.stage = "CONFIRM"
            st.rerun()


def render_confirmation():
    st.header("📋 Confirm Study Session Details")
    p = st.session_state.profile

    st.markdown(
        f"""
        - **Student Name:** {p.name}
        - **Education Level:** {p.education_level.title()} {f'({p.course_branch}, {p.year_semester})' if p.course_branch else ''}
        - **Subject & Topic:** **{p.subject}** {'- ' + p.topic if p.topic else '(Comprehensive syllabus)'}
        - **Knowledge Level:** {p.knowledge_level.title()}
        - **Session Purpose:** {p.purpose.replace('_', ' ').title()}
        - **Difficulty:** {p.difficulty.title()}
        - **Total Questions:** {p.num_questions}
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start Practice Session", type="primary", use_container_width=True):
            st.session_state.agent = StudyAgent()
            st.session_state.agent.start_session(st.session_state.profile)
            st.session_state.agent.next_question()
            st.session_state.stage = "INTERVIEW"
            st.rerun()
    with col2:
        if st.button("✏️ Modify Settings", use_container_width=True):
            st.session_state.stage = "CONFIG"
            st.rerun()


def render_interview():
    agent = st.session_state.agent
    curr_q = agent.current_question

    if not curr_q or not agent.is_session_active():
        st.session_state.final_report = agent.finish_session()
        st.session_state.stage = "REPORT"
        st.rerun()
        return

    # Header & progress
    total_q = agent.session.profile.num_questions
    curr_idx = agent.session.current_index
    progress_val = min(1.0, (curr_idx - 1) / total_q)
    st.progress(progress_val)
    st.caption(f"Progress: Question {curr_idx} of {total_q} | Topic: {curr_q.topic} | Difficulty: {curr_q.difficulty.title()}")

    # Display Question
    st.subheader(f"Question #{curr_idx}")
    st.markdown(f"### {curr_q.question_text}")

    if agent.in_follow_up and agent.current_follow_up_text:
        st.info(f"🔎 **Follow-Up Question:** {agent.current_follow_up_text}")

    # Action buttons for quick command access
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    with btn_col1:
        if st.button("💡 Get Hint", use_container_width=True):
            res = agent.process_student_input("hint")
            st.toast(res.get("message", "Hint provided"))
            st.session_state.history.append(("hint", res.get("message", "")))
    with btn_col2:
        if st.button("📖 Explain Concept", use_container_width=True):
            res = agent.process_student_input("explain")
            st.session_state.history.append(("explain", res.get("message", "")))
    with btn_col3:
        if st.button("⏭️ Skip Question", use_container_width=True):
            res = agent.process_student_input("skip")
            st.session_state.history.append(("skip", res.get("message", "")))
            agent.next_question()
            st.rerun()
    with btn_col4:
        if st.button("⏹️ End Session & Report", use_container_width=True):
            res = agent.process_student_input("stop")
            st.session_state.final_report = res.get("report")
            st.session_state.stage = "REPORT"
            st.rerun()

    # History cards (hints, explanations)
    for h_type, h_text in st.session_state.history:
        if h_type == "hint":
            st.warning(h_text)
        elif h_type == "explain":
            st.info(h_text)

    # Input form for answer
    with st.form(key=f"answer_form_{curr_idx}_{agent.in_follow_up}"):
        ans_label = "Your Follow-up Answer:" if agent.in_follow_up else "Your Answer / Solution:"
        student_ans = st.text_area(ans_label, height=120, placeholder="Type your answer or type 'hint', 'skip', 'explain', 'stop'...")
        submitted = st.form_submit_button("Submit Answer", type="primary", use_container_width=True)

        if submitted and student_ans.strip():
            result = agent.process_student_input(student_ans.strip())
            r_type = result.get("type")

            if r_type == "quit":
                st.warning("Session exited.")
                st.session_state.stage = "CONFIG"
                st.rerun()
            elif r_type == "stop":
                st.session_state.final_report = result.get("report")
                st.session_state.stage = "REPORT"
                st.rerun()
            elif r_type in ("evaluation", "evaluation_with_follow_up", "follow_up_evaluation"):
                eval_res = result.get("evaluation")
                st.session_state.last_eval = eval_res
                if r_type != "evaluation_with_follow_up":
                    agent.next_question()
                st.rerun()


def render_report():
    st.header("📊 Performance Report")
    report = st.session_state.final_report

    if not report:
        st.warning("No report generated.")
        return

    if report.is_partial:
        st.warning("⚠️ This is a partial-session report because the session ended early.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Score", f"{report.total_score} / {report.max_possible_score}")
    col2.metric("Accuracy", f"{report.percentage}%")
    col3.metric("Completed", f"{report.questions_completed} / {report.total_questions_planned}")
    col4.metric("Skipped", f"{report.questions_skipped}")

    st.divider()

    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.subheader("✅ Concepts Mastered")
        if report.correct_concepts:
            for c in report.correct_concepts:
                st.success(f"• {c}")
        else:
            st.write("No high-confidence mastery recorded.")

        st.subheader("🎯 Revision Recommendations")
        for rev in report.recommended_revision:
            st.markdown(f"- **{rev}**")

    with r_col2:
        st.subheader("⚠️ Topics Needing Improvement")
        if report.improvement_topics:
            for t in report.improvement_topics:
                st.warning(f"• {t}")
        else:
            st.write("Great work! No significant gaps recorded.")

        st.subheader("🚀 Next Practice Session")
        st.info(report.suggested_next_session)

    if report.mistakes_summary:
        st.divider()
        st.subheader("🔍 Detailed Mistake Breakdown")
        for idx, m in enumerate(report.mistakes_summary, 1):
            with st.expander(f"Question #{idx}: {m['question'][:80]}... (Score: {m['score']})"):
                st.markdown(f"**Assessment:** {m['assessment']}")
                st.markdown(f"**Explanation:** {m['explanation']}")
                st.markdown(f"**Missed Points:** {m['missed']}")

    st.divider()
    if st.button("🔄 Start New Practice Session", type="primary"):
        st.session_state.stage = "CONFIG"
        st.session_state.history = []
        st.session_state.final_report = None
        st.session_state.agent = None
        st.rerun()


def main():
    render_sidebar()
    init_session_state()

    stage = st.session_state.stage
    if stage == "CONFIG":
        render_config_form()
    elif stage == "CONFIRM":
        render_confirmation()
    elif stage == "INTERVIEW":
        render_interview()
    elif stage == "REPORT":
        render_report()


if __name__ == "__main__":
    main()
