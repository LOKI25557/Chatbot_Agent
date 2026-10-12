import json
import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, is_groq_configured
from student_profile import StudentProfile
from session_manager import QuestionItem

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Detailed evaluation result for a student's answer based on the 0-5 rubric."""
    score: int                             # 0 to 5
    score_label: str                       # e.g. "4/5 - Correct and well explained"
    correctness: str                       # Correct, Partially Correct, Incorrect, Ambiguous
    explanation: str                       # Why answer is correct / partial / incorrect
    missed_points: List[str] = field(default_factory=list)
    suggested_answer: str = ""             # Recommended model answer
    is_clarification: bool = False         # True if answer was ambiguous and needs clarification
    clarification_prompt: str = ""


RUBRIC_MAP = {
    0: "0/5 - No relevant answer or completely incorrect",
    1: "1/5 - Very limited understanding",
    2: "2/5 - Partially correct with significant gaps",
    3: "3/5 - Mostly correct with some missing details",
    4: "4/5 - Correct and well explained",
    5: "5/5 - Complete, accurate, and clearly explained"
}


def score_to_label(score: int) -> str:
    """Maps an integer score (0-5) to its standardized rubric label."""
    clamped = max(0, min(5, int(score)))
    return RUBRIC_MAP.get(clamped, f"{clamped}/5")


def build_evaluation_from_dict(data: Dict[str, Any]) -> EvaluationResult:
    """Builds a safe EvaluationResult dataclass instance from a dictionary."""
    try:
        raw_score = data.get("score", 0)
        score = int(raw_score)
        score = max(0, min(5, score))
    except (ValueError, TypeError):
        score = 0

    correctness = str(data.get("correctness", "Partially Correct")).strip()
    explanation = str(data.get("explanation", "Evaluation completed.")).strip()

    missed = data.get("missed_points", [])
    if isinstance(missed, str):
        missed = [missed] if missed.strip() else []
    elif not isinstance(missed, list):
        missed = []

    suggested = str(data.get("suggested_answer", "")).strip()
    is_clar = bool(data.get("is_clarification", False))
    clar_prompt = str(data.get("clarification_prompt", "")).strip()

    return EvaluationResult(
        score=score,
        score_label=score_to_label(score),
        correctness=correctness,
        explanation=explanation,
        missed_points=missed,
        suggested_answer=suggested,
        is_clarification=is_clar,
        clarification_prompt=clar_prompt
    )


def format_evaluation_summary(eval_res: EvaluationResult) -> str:
    """Formats an evaluation result for clean terminal or markdown display."""
    lines = []
    lines.append(f"Assessment: {eval_res.correctness} ({eval_res.score_label})")
    lines.append(f"\nFeedback: {eval_res.explanation}")

    if eval_res.missed_points:
        lines.append("\nKey Points Missed:")
        for pt in eval_res.missed_points:
            lines.append(f"  • {pt}")

    if eval_res.suggested_answer:
        lines.append(f"\nSuggested Model Answer:\n{eval_res.suggested_answer}")

    return "\n".join(lines)


def _clean_json_string(raw: str) -> str:
    """Strips markdown code fences from LLM output."""
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


class AnswerEvaluator:
    """
    Evaluates student answers, generates hints, explanations, and follow-ups
    using Groq LLM or deterministic fallback algorithms.
    """

    def evaluate_answer(
        self,
        profile: StudentProfile,
        question: QuestionItem,
        student_answer: str
    ) -> EvaluationResult:
        """Evaluates student answer against question concepts and 0-5 rubric."""
        if not student_answer or not student_answer.strip():
            return EvaluationResult(
                score=0,
                score_label=score_to_label(0),
                correctness="Incorrect",
                explanation="No answer provided.",
                missed_points=list(question.expected_concepts),
                suggested_answer="A complete response should address: " + ", ".join(question.expected_concepts)
            )

        if is_groq_configured():
            try:
                res = self._evaluate_with_groq(profile, question, student_answer)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"Groq evaluation failed ({e}); falling back to heuristic evaluation.")

        return self._evaluate_heuristic(profile, question, student_answer)

    def _evaluate_with_groq(
        self,
        profile: StudentProfile,
        question: QuestionItem,
        student_answer: str
    ) -> Optional[EvaluationResult]:
        """Calls Groq API to perform a fair, constructive evaluation using 0-5 rubric."""
        from openai import OpenAI
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url=GROQ_BASE_URL,
            timeout=18.0
        )

        expected_str = "\n- ".join(question.expected_concepts) if question.expected_concepts else "Core subject principles"

        prompt = f"""You are an expert AI tutor evaluating a student's answer.

QUESTION ASKED:
{question.question_text}
Topic: {question.topic} | Difficulty: {question.difficulty} | Type: {question.question_type}

KEY CONCEPTS EXPECTED:
- {expected_str}

STUDENT'S ANSWER:
\"\"\"{student_answer}\"\"\"

STUDENT CONTEXT:
Education Level: {profile.education_level} (Branch: {profile.course_branch or 'N/A'})
Purpose: {profile.purpose} | Knowledge Level: {profile.knowledge_level}

EVALUATION RUBRIC (0-5 scale):
0: No relevant answer or completely incorrect
1: Very limited understanding with major misconceptions
2: Partially correct with significant gaps
3: Mostly correct with some missing details or slight imprecision
4: Correct and well explained
5: Complete, accurate, and clearly explained (including edge cases or complexity if coding)

RULES:
1. Be fair and constructive. Do NOT penalize merely for different wording if the concept is correct.
2. If the answer is completely ambiguous or vague (e.g., 'maybe something with memory'), set is_clarification=true and provide a clarification_prompt.
3. If coding or algorithmic, consider correctness, logic, and complexity.
4. Return ONLY a valid JSON object with these EXACT keys:
{{
  "score": integer from 0 to 5,
  "correctness": "Correct" or "Partially Correct" or "Incorrect" or "Ambiguous",
  "explanation": "Constructive explanation of why this score was awarded and what was good",
  "missed_points": ["Important concept 1 missed", "Important concept 2 missed"],
  "suggested_answer": "Clear, concise ideal model answer or solution",
  "is_clarification": boolean,
  "clarification_prompt": "Optional question if the response was ambiguous"
}}"""

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a fair, expert tutor who grades constructively and outputs ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=650,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content or ""
        cleaned = _clean_json_string(content)
        data = json.loads(cleaned)
        return build_evaluation_from_dict(data)

    def _evaluate_heuristic(
        self,
        profile: StudentProfile,
        question: QuestionItem,
        student_answer: str
    ) -> EvaluationResult:
        """Deterministic offline evaluation checking length, keywords, and concept coverage."""
        ans_lower = student_answer.lower()
        matched = []
        for c in question.expected_concepts:
            words = [w.lower() for w in re.findall(r"\w+", c) if len(w) > 3]
            if any(w in ans_lower for w in words):
                matched.append(c)

        ratio = len(matched) / max(1, len(question.expected_concepts))
        word_count = len(ans_lower.split())

        if word_count < 3:
            score = 1
            correctness = "Partially Correct"
            explanation = "Your answer is very brief. Try elaborating on the underlying mechanism."
        elif ratio >= 0.7:
            score = 4 if word_count < 20 else 5
            correctness = "Correct"
            explanation = "Excellent explanation covering the key concepts accurately."
        elif ratio >= 0.4:
            score = 3
            correctness = "Partially Correct"
            explanation = "Good attempt! You understood the general idea but missed some important nuances."
        elif ratio > 0.1:
            score = 2
            correctness = "Partially Correct"
            explanation = "Partially correct, though significant conceptual gaps remain."
        else:
            score = 1
            correctness = "Incorrect"
            explanation = "The response did not clearly address the core concepts of the question."

        missed = [c for c in question.expected_concepts if c not in matched]

        return EvaluationResult(
            score=score,
            score_label=score_to_label(score),
            correctness=correctness,
            explanation=explanation,
            missed_points=missed,
            suggested_answer=f"A complete answer should cover: {', '.join(question.expected_concepts)}."
        )

    def generate_hint(
        self,
        profile: StudentProfile,
        question: QuestionItem,
        hint_number: int = 1
    ) -> str:
        """Provides a helpful clue without revealing the complete answer."""
        if question.hints:
            idx = min(hint_number - 1, len(question.hints) - 1)
            return f"💡 Hint {idx + 1}: {question.hints[idx]}"

        if is_groq_configured():
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=GROQ_API_KEY,
                    base_url=GROQ_BASE_URL,
                    timeout=10.0
                )
                prompt = f"Give a subtle, helpful hint (1-2 sentences) for this question WITHOUT revealing the complete answer:\nQuestion: {question.question_text}\nTopic: {question.topic}"
                resp = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=120,
                    temperature=0.5
                )
                hint_text = resp.choices[0].message.content.strip()
                return f"💡 Hint: {hint_text}"
            except Exception as e:
                logger.warning(f"Groq hint generation failed ({e})")

        return f"💡 Hint: Think about how {question.topic or profile.subject} operates under the hood and where memory or state is handled."

    def explain_concept(
        self,
        profile: StudentProfile,
        question: QuestionItem
    ) -> str:
        """Explains the relevant concept in detail when requested."""
        if is_groq_configured():
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=GROQ_API_KEY,
                    base_url=GROQ_BASE_URL,
                    timeout=15.0
                )
                prompt = f"""Explain this concept clearly and educationally for a {profile.education_level} student:
Question: {question.question_text}
Topic: {question.topic}
Subject: {profile.subject}
Keep it concise (3-4 bullet points or short paragraphs) and highlight practical examples."""
                resp = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400,
                    temperature=0.5
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"Groq concept explanation failed ({e})")

        # Fallback offline explanation
        concepts_str = ", ".join(question.expected_concepts) if question.expected_concepts else "fundamental design and syntax"
        return (
            f"📖 Concept Overview for {question.topic or profile.subject}:\n"
            f"This topic revolves around {concepts_str}.\n"
            f"In real-world applications, understanding this enables developers to avoid common bugs, "
            f"optimize memory and CPU performance, and build maintainable software architecture."
        )

    def generate_follow_up(
        self,
        profile: StudentProfile,
        question: QuestionItem,
        student_answer: str,
        evaluation: EvaluationResult
    ) -> Optional[str]:
        """
        Generates a short follow-up question when useful
        (e.g., if student gave a partial answer or scored 3-4 and an edge case is relevant).
        """
        # Only ask follow-ups for placement or technical interviews and when score is 2, 3, or 4
        if profile.purpose not in ("placement_interview", "technical_interview"):
            return None
        if evaluation.score not in (2, 3, 4):
            return None

        if is_groq_configured():
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=GROQ_API_KEY,
                    base_url=GROQ_BASE_URL,
                    timeout=10.0
                )
                prompt = f"""Generate ONE short, focused follow-up question to test deeper understanding or a relevant edge case.
Question: {question.question_text}
Student's answer: {student_answer}
Score: {evaluation.score}/5
Return ONLY the follow-up question string."""
                resp = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.5
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"Groq follow-up generation failed ({e})")

        return None
