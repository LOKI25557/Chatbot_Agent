from dataclasses import dataclass, field
from typing import Tuple, Optional


VALID_EDUCATION_LEVELS = ("school", "diploma", "undergraduate", "postgraduate", "other")
VALID_KNOWLEDGE_LEVELS = ("beginner", "intermediate", "advanced")
VALID_PURPOSES = (
    "general_learning",
    "exam_prep",
    "placement_interview",
    "technical_interview",
    "revision"
)
VALID_DIFFICULTIES = ("easy", "medium", "hard")


@dataclass
class StudentProfile:
    """
    Holds student preferences and context for a personalized study session.
    All state is stored in-memory during execution.
    """
    name: str = "Student"
    education_level: str = "undergraduate"  # school, diploma, undergraduate, postgraduate, other
    course_branch: str = ""                # e.g., "Computer Science", "Electrical"
    year_semester: str = ""                # e.g., "3rd Year / 5th Semester"
    subject: str = "Python"                # Any subject entered by student
    topic: str = ""                        # Optional specific topic
    knowledge_level: str = "beginner"      # beginner, intermediate, advanced
    purpose: str = "general_learning"      # exam_prep, placement_interview, technical_interview, revision, general_learning
    difficulty: str = "medium"             # easy, medium, hard
    num_questions: int = 5                 # Reasonable default: 5

    def validate(self) -> Tuple[bool, str]:
        """Validates student profile fields for reasonable ranges and values."""
        if not self.name or not self.name.strip():
            self.name = "Student"

        if not self.subject or not self.subject.strip():
            return False, "Subject cannot be empty."

        if self.education_level not in VALID_EDUCATION_LEVELS:
            self.education_level = "undergraduate"

        if self.knowledge_level not in VALID_KNOWLEDGE_LEVELS:
            self.knowledge_level = "beginner"

        if self.purpose not in VALID_PURPOSES:
            self.purpose = "general_learning"

        if self.difficulty not in VALID_DIFFICULTIES:
            self.difficulty = "medium"

        if not isinstance(self.num_questions, int) or self.num_questions < 1:
            return False, "Number of questions must be at least 1."

        if self.num_questions > 20:
            return False, "Number of questions cannot exceed 20 per session."

        return True, "Valid"

    def summary(self) -> str:
        """User-friendly summary of the session settings."""
        edu_details = [self.education_level.title()]
        if self.course_branch:
            edu_details.append(self.course_branch)
        if self.year_semester:
            edu_details.append(self.year_semester)
        edu_str = " - ".join(edu_details)

        topic_str = self.topic if self.topic else "Comprehensive / All Core Topics"

        return (
            f"👤 Student Name:      {self.name}\n"
            f"🎓 Education Level:   {edu_str}\n"
            f"📚 Subject:           {self.subject}\n"
            f"🎯 Specific Topic:    {topic_str}\n"
            f"🧠 Knowledge Level:   {self.knowledge_level.title()}\n"
            f"🎯 Session Purpose:   {self.purpose.replace('_', ' ').title()}\n"
            f"⚡ Difficulty:        {self.difficulty.title()}\n"
            f"🔢 Total Questions:   {self.num_questions}"
        )


def collect_student_profile_interactive() -> Optional[StudentProfile]:
    """
    Conversationally collects student details step-by-step with sensible defaults,
    educational branching (skipping branch/semester for school students),
    and confirmation before starting.
    Returns StudentProfile or None if user quits during setup.
    """
    print("\n👋 Welcome to Study Agent! Let's set up your personalized study session.\n")
    print("💡 Tip: Press [Enter] on any question to accept the suggested default value.\n")

    profile = StudentProfile()

    # 1. Name
    name_in = input("1. What is your name or preferred name? [Student]: ").strip()
    if name_in.lower() in ("quit", "exit"):
        return None
    profile.name = name_in if name_in else "Student"

    # 2. Education level
    print("\n2. What is your current education level?")
    print("   [1] School (K-12)")
    print("   [2] Diploma")
    print("   [3] Undergraduate (B.Tech, B.Sc, BCA, etc.)")
    print("   [4] Postgraduate (M.Tech, M.Sc, MCA, etc.)")
    print("   [5] Other / Professional")
    edu_choice = input("   Select (1-5) [3]: ").strip()
    if edu_choice.lower() in ("quit", "exit"):
        return None
    edu_map = {
        "1": "school",
        "2": "diploma",
        "3": "undergraduate",
        "4": "postgraduate",
        "5": "other"
    }
    profile.education_level = edu_map.get(edu_choice, "undergraduate")

    # 3 & 4. Branch and semester (skipped for school students)
    if profile.education_level in ("undergraduate", "postgraduate", "diploma"):
        branch_in = input("\n3. Course and branch / specialization (e.g., Computer Science, Electrical) [Optional - Enter to skip]: ").strip()
        if branch_in.lower() in ("quit", "exit"):
            return None
        profile.course_branch = branch_in

        sem_in = input("4. Current year or semester (e.g., 3rd Year / 6th Sem) [Optional - Enter to skip]: ").strip()
        if sem_in.lower() in ("quit", "exit"):
            return None
        profile.year_semester = sem_in
    else:
        profile.course_branch = ""
        profile.year_semester = ""

    # 5. Subject
    print("\n5. Which subject would you like to practice today?")
    print("   (Examples: Python, Java, C++, DSA, DBMS, OS, Computer Networks, AI/ML, Mathematics, Web Dev, etc.)")
    subj_in = input("   Enter subject [Python]: ").strip()
    if subj_in.lower() in ("quit", "exit"):
        return None
    profile.subject = subj_in if subj_in else "Python"

    # 6. Specific topic within subject
    topic_in = input(f"\n6. Any specific topic within {profile.subject}? (Press Enter for comprehensive coverage) [Optional]: ").strip()
    if topic_in.lower() in ("quit", "exit"):
        return None
    profile.topic = topic_in

    # 7. Knowledge level
    print(f"\n7. What is your current knowledge level in {profile.subject}?")
    print("   [1] Beginner")
    print("   [2] Intermediate")
    print("   [3] Advanced")
    lvl_choice = input("   Select (1-3) [1]: ").strip()
    if lvl_choice.lower() in ("quit", "exit"):
        return None
    lvl_map = {"1": "beginner", "2": "intermediate", "3": "advanced"}
    profile.knowledge_level = lvl_map.get(lvl_choice, "beginner")

    # 8. Purpose
    print("\n8. What is the primary purpose of this study session?")
    print("   [1] General Learning & Practice")
    print("   [2] College / School Exam Preparation")
    print("   [3] Placement / Campus Interview")
    print("   [4] Technical Job Interview")
    print("   [5] Revision & Self-Assessment")
    purpose_choice = input("   Select (1-5) [1]: ").strip()
    if purpose_choice.lower() in ("quit", "exit"):
        return None
    purpose_map = {
        "1": "general_learning",
        "2": "exam_prep",
        "3": "placement_interview",
        "4": "technical_interview",
        "5": "revision"
    }
    profile.purpose = purpose_map.get(purpose_choice, "general_learning")

    # 9. Difficulty
    print("\n9. Preferred question difficulty?")
    print("   [1] Easy")
    print("   [2] Medium")
    print("   [3] Hard")
    diff_choice = input("   Select (1-3) [2]: ").strip()
    if diff_choice.lower() in ("quit", "exit"):
        return None
    diff_map = {"1": "easy", "2": "medium", "3": "hard"}
    profile.difficulty = diff_map.get(diff_choice, "medium")

    # 10. Number of questions
    q_count_in = input("\n10. How many questions would you like to practice? [5]: ").strip()
    if q_count_in.lower() in ("quit", "exit"):
        return None
    try:
        q_count = int(q_count_in) if q_count_in else 5
        profile.num_questions = max(1, min(20, q_count))
    except ValueError:
        profile.num_questions = 5

    # Confirmation step
    while True:
        print("\n" + "=" * 55)
        print("📋 SESSION CONFIGURATION SUMMARY")
        print("=" * 55)
        print(profile.summary())
        print("=" * 55)

        confirm = input("\nReady to begin this session? ([Y]es / [C]hange subject / [Q]uit) [Y]: ").strip().lower()
        if confirm in ("", "y", "yes", "confirm", "start"):
            return profile
        elif confirm in ("q", "quit", "exit"):
            return None
        elif confirm in ("c", "change", "edit"):
            new_subj = input(f"Enter new subject [{profile.subject}]: ").strip()
            if new_subj:
                profile.subject = new_subj
            new_topic = input(f"Enter specific topic [{profile.topic or 'None'}]: ").strip()
            profile.topic = new_topic
            new_diff = input(f"Enter difficulty (easy/medium/hard) [{profile.difficulty}]: ").strip().lower()
            if new_diff in VALID_DIFFICULTIES:
                profile.difficulty = new_diff
            new_q = input(f"Enter question count [{profile.num_questions}]: ").strip()
            if new_q.isdigit():
                profile.num_questions = max(1, min(20, int(new_q)))
        else:
            print("Please enter 'yes' to start, 'change' to edit, or 'quit' to exit.")
