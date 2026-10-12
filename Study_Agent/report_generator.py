import sys
from dataclasses import dataclass, field
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from session_manager import SessionManager


@dataclass
class SessionReport:
    """Comprehensive performance report generated at the end of a study session."""
    student_name: str
    subject: str
    topic: str
    education_level: str
    course_branch: str = ""
    year_semester: str = ""
    purpose: str = "General Learning"
    difficulty: str = "Medium"
    total_questions_planned: int = 5
    questions_attempted: int = 0
    questions_completed: int = 0
    questions_skipped: int = 0
    total_score: int = 0
    max_possible_score: int = 0
    percentage: float = 0.0
    is_partial: bool = False
    correct_concepts: List[str] = field(default_factory=list)
    improvement_topics: List[str] = field(default_factory=list)
    mistakes_summary: List[Dict[str, Any]] = field(default_factory=list)
    recommended_revision: List[str] = field(default_factory=list)
    suggested_next_session: str = ""


def build_session_report(session: "SessionManager") -> SessionReport:
    """
    Calculates strict, data-driven performance metrics from completed questions.
    Does NOT invent answers or assume mastery without supporting evidence.
    """
    completed = [q for q in session.questions if q.evaluation is not None and not q.skipped]
    skipped = [q for q in session.questions if q.skipped]
    attempted = len(completed)

    total_score = sum(q.evaluation.score for q in completed)
    max_possible_score = attempted * 5
    percentage = round((total_score / max_possible_score) * 100, 1) if max_possible_score > 0 else 0.0

    correct_concepts = []
    improvement_topics = []
    mistakes_summary = []
    recommended_revision = []

    for q in completed:
        eval_res = q.evaluation
        topic_name = q.topic or session.profile.subject
        if eval_res.score >= 4:
            concept_entry = f"{topic_name}: {q.question_text[:55]}..." if len(q.question_text) > 55 else f"{topic_name}: {q.question_text}"
            if concept_entry not in correct_concepts:
                correct_concepts.append(concept_entry)
        else:
            if topic_name not in improvement_topics:
                improvement_topics.append(topic_name)

            # Record detailed mistake and explanation
            missed_str = "; ".join(eval_res.missed_points) if eval_res.missed_points else "Key conceptual nuances"
            mistakes_summary.append({
                "question": q.question_text,
                "score": f"{eval_res.score}/5",
                "assessment": eval_res.correctness,
                "explanation": eval_res.explanation,
                "missed": missed_str
            })

            if topic_name not in recommended_revision:
                recommended_revision.append(topic_name)

    # Skipped questions must be recommended for revision
    for q in skipped:
        topic_name = f"{q.topic or session.profile.subject} (Skipped question)"
        if topic_name not in recommended_revision:
            recommended_revision.append(topic_name)

    if not recommended_revision:
        recommended_revision.append(f"Advanced deep-dive into {session.profile.subject} architecture & practical edge cases")

    # Determine next practice session advice
    if session.is_partial:
        suggested_next = f"Complete a full {session.profile.num_questions}-question session on {session.profile.subject} covering the skipped topics."
    elif percentage >= 80:
        next_diff = "hard" if session.profile.difficulty != "hard" else "expert"
        suggested_next = f"Advance to '{next_diff}' difficulty practice or technical interview simulation on {session.profile.subject}."
    elif percentage >= 50:
        top_rev = ", ".join(recommended_revision[:2])
        suggested_next = f"Revise key topics ({top_rev}) and retake a medium-level practice session."
    else:
        suggested_next = f"Focus on foundational concepts in {session.profile.subject} with beginner difficulty and practice using hints."

    return SessionReport(
        student_name=session.profile.name,
        subject=session.profile.subject,
        topic=session.profile.topic or "Comprehensive Syllabus",
        education_level=session.profile.education_level.title(),
        course_branch=session.profile.course_branch or "N/A",
        year_semester=session.profile.year_semester or "N/A",
        purpose=session.profile.purpose.replace("_", " ").title(),
        difficulty=session.profile.difficulty.title(),
        total_questions_planned=session.profile.num_questions,
        questions_attempted=attempted,
        questions_completed=len(completed),
        questions_skipped=len(skipped),
        total_score=total_score,
        max_possible_score=max_possible_score,
        percentage=percentage,
        is_partial=session.is_partial,
        correct_concepts=correct_concepts,
        improvement_topics=improvement_topics,
        mistakes_summary=mistakes_summary,
        recommended_revision=recommended_revision,
        suggested_next_session=suggested_next
    )


def format_report_cli(report: SessionReport) -> str:
    """Formats the performance report for clear, portable terminal display without Unicode crashes."""
    lines = []
    width = 72
    header_title = "PARTIAL-SESSION PERFORMANCE REPORT" if report.is_partial else "FINAL PERFORMANCE REPORT"

    lines.append("\n" + "=" * width)
    lines.append(f"  {header_title.center(width - 4)}  ")
    lines.append("=" * width)

    lines.append(f"  Student Name:        {report.student_name}")
    lines.append(f"  Education:           {report.education_level} (Branch: {report.course_branch})")
    lines.append(f"  Subject / Topic:     {report.subject} ({report.topic})")
    lines.append(f"  Session Purpose:     {report.purpose}")
    lines.append(f"  Difficulty Level:    {report.difficulty}")
    lines.append("-" * width)

    lines.append(f"  Questions Planned:   {report.total_questions_planned}")
    lines.append(f"  Questions Attempted: {report.questions_attempted}")
    lines.append(f"  Questions Completed: {report.questions_completed}")
    lines.append(f"  Questions Skipped:   {report.questions_skipped}")
    lines.append(f"  Total Score:         {report.total_score} / {report.max_possible_score}")
    lines.append(f"  Overall Percentage:  {report.percentage}%")

    if report.is_partial:
        lines.append("\n  [!] Note: This is a partial report as the session ended before finishing.")

    lines.append("-" * width)

    # Mastered concepts
    lines.append("  [+] CONCEPTS DEMONSTRATING GOOD UNDERSTANDING (Score 4-5):")
    if report.correct_concepts:
        for c in report.correct_concepts:
            lines.append(f"     - {c}")
    else:
        lines.append("     - None verified during this session.")

    # Improvement topics
    lines.append("\n  [!] TOPICS REQUIRING IMPROVEMENT (Score < 4):")
    if report.improvement_topics:
        for t in report.improvement_topics:
            lines.append(f"     - {t}")
    else:
        lines.append("     - No major weak areas detected on attempted questions.")

    # Mistakes & explanations
    if report.mistakes_summary:
        lines.append("\n  [?] MISTAKES & CONCEPTUAL GAPS IDENTIFIED:")
        for idx, m in enumerate(report.mistakes_summary, start=1):
            q_short = m['question'][:60] + "..." if len(m['question']) > 60 else m['question']
            lines.append(f"     [{idx}] Question: {q_short}")
            lines.append(f"         Score: {m['score']} ({m['assessment']})")
            lines.append(f"         Feedback: {m['explanation']}")
            lines.append(f"         Missed Points: {m['missed']}")

    # Revision
    lines.append("\n  [*] RECOMMENDED TOPICS FOR REVISION:")
    for rev in report.recommended_revision:
        lines.append(f"     - {rev}")

    # Next session
    lines.append(f"\n  [>] SUGGESTED NEXT PRACTICE SESSION:\n     {report.suggested_next_session}")
    lines.append("=" * width + "\n")

    return "\n".join(lines)


def format_report_markdown(report: SessionReport) -> str:
    """Formats the performance report as Markdown for web UI display."""
    md = []
    title = "Partial-Session Performance Report" if report.is_partial else "Final Performance Report"
    md.append(f"### {title}\n")
    md.append(f"- **Student:** {report.student_name}")
    md.append(f"- **Education:** {report.education_level} ({report.course_branch})")
    md.append(f"- **Subject & Topic:** {report.subject} ({report.topic})")
    md.append(f"- **Purpose:** {report.purpose} | **Difficulty:** {report.difficulty}")
    md.append(f"- **Questions:** {report.questions_completed} completed, {report.questions_skipped} skipped (out of {report.total_questions_planned} planned)")
    md.append(f"- **Score:** **{report.total_score} / {report.max_possible_score}** ({report.percentage}%)\n")

    md.append("#### Concepts Mastered")
    if report.correct_concepts:
        for c in report.correct_concepts:
            md.append(f"- {c}")
    else:
        md.append("- *No mastered concepts verified in this session.*")

    md.append("\n#### Topics Requiring Improvement")
    if report.improvement_topics:
        for t in report.improvement_topics:
            md.append(f"- {t}")
    else:
        md.append("- *No significant weak areas identified.*")

    if report.mistakes_summary:
        md.append("\n#### Mistakes & Explanations")
        for idx, m in enumerate(report.mistakes_summary, start=1):
            md.append(f"**{idx}. {m['question']}**")
            md.append(f"- **Score:** {m['score']} ({m['assessment']})")
            md.append(f"- **Explanation:** {m['explanation']}")
            md.append(f"- **Missed:** {m['missed']}")

    md.append("\n#### Recommended Topics for Revision")
    for r in report.recommended_revision:
        md.append(f"- {r}")

    md.append(f"\n#### Next Practice Session\n{report.suggested_next_session}")
    return "\n".join(md)
