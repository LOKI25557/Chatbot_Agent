import json
import logging
import re
from typing import List, Optional, Dict, Any

from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, is_groq_configured
from session_manager import QuestionItem
from student_profile import StudentProfile

logger = logging.getLogger(__name__)


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


# Comprehensive offline question bank organized by subject
OFFLINE_QUESTIONS: Dict[str, List[Dict[str, Any]]] = {
    "python": [
        {
            "question_text": "What is the difference between a list and a tuple in Python, and when would you use each?",
            "topic": "Data Types & Mutability",
            "difficulty": "easy",
            "question_type": "conceptual",
            "expected_concepts": ["Lists are mutable, tuples are immutable", "Tuples use less memory / can be dictionary keys", "Lists for collections that change"],
            "hints": ["Think about whether elements can be modified after creation."]
        },
        {
            "question_text": "How does memory management work in Python? Mention reference counting and garbage collection.",
            "topic": "Memory Management",
            "difficulty": "medium",
            "question_type": "conceptual",
            "expected_concepts": ["Reference counting mechanism", "Generational cyclic garbage collector", "Memory deallocation when ref count reaches 0"],
            "hints": ["Python tracks how many references point to each object."]
        },
        {
            "question_text": "What are Python decorators, and how would you implement a simple timing or logging decorator?",
            "topic": "Decorators & Higher-Order Functions",
            "difficulty": "medium",
            "question_type": "coding",
            "expected_concepts": ["First-class functions", "Wrapper function accepting *args and **kwargs", "functools.wraps preservation"],
            "hints": ["A decorator takes a function as argument and returns an augmented wrapper function."]
        },
        {
            "question_text": "Explain Python's Global Interpreter Lock (GIL) and how it affects CPU-bound vs I/O-bound multi-threaded programs.",
            "topic": "Concurrency & GIL",
            "difficulty": "hard",
            "question_type": "conceptual",
            "expected_concepts": ["GIL allows only one native thread to execute Python bytecode at a time", "CPU-bound tasks require multiprocessing", "I/O-bound tasks still benefit from threading or asyncio"],
            "hints": ["Consider why CPU-bound threads fight for execution locks rather than running in true parallel."]
        },
        {
            "question_text": "What is the difference between '==' and 'is' in Python? Provide an example where their results differ.",
            "topic": "Equality vs Identity",
            "difficulty": "easy",
            "question_type": "conceptual",
            "expected_concepts": ["'==' checks value equality", "'is' checks memory object identity", "Example with two distinct lists containing identical elements"],
            "hints": ["One compares content, while the other checks if both point to the exact same memory address."]
        }
    ],
    "java": [
        {
            "question_text": "Explain the difference between JDK, JRE, and JVM in Java.",
            "topic": "Java Architecture",
            "difficulty": "easy",
            "question_type": "conceptual",
            "expected_concepts": ["JVM executes bytecode", "JRE contains JVM plus core class libraries", "JDK contains JRE plus development tools (javac)"],
            "hints": ["Think of them as nested layers from runtime to complete development toolkit."]
        },
        {
            "question_text": "What is the difference between checked and unchecked exceptions in Java? Give examples of each.",
            "topic": "Exception Handling",
            "difficulty": "medium",
            "question_type": "conceptual",
            "expected_concepts": ["Checked exceptions are verified at compile time (e.g. IOException)", "Unchecked exceptions inherit from RuntimeException (e.g. NullPointerException)", "Checked require try-catch or throws clause"],
            "hints": ["One type is enforced by the compiler; the other happens during program execution due to programming logic bugs."]
        },
        {
            "question_text": "How does HashMap work internally in Java? What happens during a hash collision?",
            "topic": "Collections & Internals",
            "difficulty": "hard",
            "question_type": "conceptual",
            "expected_concepts": ["Array of Node buckets", "hashCode() calculates bucket index", "equals() resolves collision in linked list or red-black tree (Java 8+)"],
            "hints": ["Think about hashing, array indexing, and how entries are chained inside a single bucket."]
        }
    ],
    "c and c++": [
        {
            "question_text": "What is the difference between pass-by-value, pass-by-reference, and pass-by-pointer in C++?",
            "topic": "Pointers & References",
            "difficulty": "easy",
            "question_type": "conceptual",
            "expected_concepts": ["Pass-by-value copies the argument", "Pass-by-reference passes an alias", "Pass-by-pointer passes the memory address"],
            "hints": ["Consider overhead, syntax differences, and whether the original variable can be modified."]
        },
        {
            "question_text": "Explain the concept of RAII (Resource Acquisition Is Initialization) in C++ and why it is important.",
            "topic": "Memory & RAII",
            "difficulty": "medium",
            "question_type": "conceptual",
            "expected_concepts": ["Resources tied to object lifetime", "Constructor acquires resource", "Destructor releases resource automatically on scope exit", "Prevents memory leaks in exceptions"],
            "hints": ["Smart pointers like std::unique_ptr rely entirely on this idiom."]
        },
        {
            "question_text": "How do virtual functions and the vtable mechanism work in C++ to enable runtime polymorphism?",
            "topic": "Polymorphism & vtables",
            "difficulty": "hard",
            "question_type": "conceptual",
            "expected_concepts": ["vtable is a table of function pointers created for classes with virtual functions", "vptr pointer points to the vtable", "Dynamic dispatch at runtime"],
            "hints": ["How does the compiler know which overridden method to call when using a base class pointer?"]
        }
    ],
    "data structures and algorithms": [
        {
            "question_text": "Compare an Array and a Linked List in terms of memory layout and time complexity for search, insertion, and deletion.",
            "topic": "Linear Data Structures",
            "difficulty": "easy",
            "question_type": "conceptual",
            "expected_concepts": ["Array: contiguous memory, O(1) random access, O(n) insert/delete", "Linked List: non-contiguous, O(n) access, O(1) insert/delete if pointer known", "Cache locality"],
            "hints": ["Focus on how elements are stored in memory and accessing elements by index."]
        },
        {
            "question_text": "What is the difference between QuickSort and MergeSort? Discuss their time complexities, space complexities, and stability.",
            "topic": "Sorting Algorithms",
            "difficulty": "medium",
            "question_type": "conceptual",
            "expected_concepts": ["MergeSort: O(n log n) worst/best, O(n) auxiliary space, stable", "QuickSort: O(n log n) average, O(n^2) worst case, O(log n) in-place space, usually unstable"],
            "hints": ["One divides by index and merges; the other partitions by a pivot value."]
        },
        {
            "question_text": "How would you detect a cycle in a linked list? Explain Floyd's Tortoise and Hare algorithm.",
            "topic": "Algorithms & Pointers",
            "difficulty": "medium",
            "question_type": "coding",
            "expected_concepts": ["Slow pointer moves 1 step, fast pointer moves 2 steps", "If fast meets slow, a cycle exists", "O(n) time, O(1) auxiliary space"],
            "hints": ["Imagine two runners running around a circular track at different speeds."]
        }
    ],
    "dbms and sql": [
        {
            "question_text": "Explain ACID properties in database management systems with a concrete banking transfer example.",
            "topic": "Transactions",
            "difficulty": "easy",
            "question_type": "conceptual",
            "expected_concepts": ["Atomicity (all or nothing)", "Consistency (valid state transitions)", "Isolation (concurrent transactions don't interfere)", "Durability (committed data survives crashes)"],
            "hints": ["Think about transferring $100 from Account A to Account B."]
        },
        {
            "question_text": "What is the difference between clustered and non-clustered indexes in SQL?",
            "topic": "Indexing",
            "difficulty": "medium",
            "question_type": "conceptual",
            "expected_concepts": ["Clustered index defines the physical order of table data (only 1 per table)", "Non-clustered index creates a separate B-Tree pointing to data rows (multiple allowed)"],
            "hints": ["Think of a dictionary (clustered) vs an index section at the back of a textbook (non-clustered)."]
        },
        {
            "question_text": "What is Database Normalization? Explain the difference between 1NF, 2NF, and 3NF.",
            "topic": "Normalization",
            "difficulty": "medium",
            "question_type": "conceptual",
            "expected_concepts": ["Reduces redundancy and dependency", "1NF: Atomic values, unique rows", "2NF: 1NF + no partial dependency on composite key", "3NF: 2NF + no transitive dependency"],
            "hints": ["Each normal form progressively removes certain types of anomalies and dependencies."]
        }
    ],
    "operating systems": [
        {
            "question_text": "What is the fundamental difference between a Process and a Thread? How do they differ in memory sharing?",
            "topic": "Processes & Threads",
            "difficulty": "easy",
            "question_type": "conceptual",
            "expected_concepts": ["Process is an independent program in execution with separate address space", "Thread is a lightweight unit within a process sharing heap, code, data", "Threads have their own stack"],
            "hints": ["Think about whether memory is isolated or shared between execution units."]
        },
        {
            "question_text": "What are the four necessary conditions for a Deadlock to occur in an operating system?",
            "topic": "Deadlocks",
            "difficulty": "medium",
            "question_type": "conceptual",
            "expected_concepts": ["Mutual Exclusion", "Hold and Wait", "No Preemption", "Circular Wait"],
            "hints": ["All four conditions must hold simultaneously for a deadlock to exist."]
        },
        {
            "question_text": "Explain how Virtual Memory and Paging work, including the Page Table and Translation Lookaside Buffer (TLB).",
            "topic": "Memory Management",
            "difficulty": "hard",
            "question_type": "conceptual",
            "expected_concepts": ["Virtual address split into page number and offset", "Page Table maps virtual to physical frames", "TLB acts as a hardware cache for rapid translation", "Page faults"],
            "hints": ["Think about how virtual pages are translated into physical frames by the MMU."]
        }
    ],
    "computer networks": [
        {
            "question_text": "Compare TCP and UDP. Explain when you would choose one over the other.",
            "topic": "Transport Layer",
            "difficulty": "easy",
            "question_type": "conceptual",
            "expected_concepts": ["TCP is connection-oriented, reliable, ordered, flow/congestion controlled", "UDP is connectionless, lightweight, low-latency, no guarantee", "Use TCP for web/email; UDP for gaming/video streaming"],
            "hints": ["Consider reliability vs speed and whether dropped packets must be retransmitted."]
        },
        {
            "question_text": "Explain what happens step-by-step from when a user types 'https://example.com' into a browser until the page renders.",
            "topic": "Web Protocols & DNS",
            "difficulty": "medium",
            "question_type": "conceptual",
            "expected_concepts": ["DNS resolution (browser, OS, resolver)", "TCP 3-way handshake", "TLS handshake for HTTPS", "HTTP GET request and response", "Browser DOM parsing and rendering"],
            "hints": ["Follow the packet journey: Name resolution -> Connection -> Security -> Content transfer."]
        }
    ],
    "artificial intelligence": [
        {
            "question_text": "What is the difference between Supervised, Unsupervised, and Reinforcement Learning?",
            "topic": "ML Paradigms",
            "difficulty": "easy",
            "question_type": "conceptual",
            "expected_concepts": ["Supervised uses labeled data", "Unsupervised finds hidden patterns in unlabeled data", "Reinforcement learns via trial, error, reward feedback"],
            "hints": ["Think about the kind of feedback or labels the model receives during training."]
        },
        {
            "question_text": "Explain the Bias-Variance tradeoff in machine learning and how it relates to underfitting and overfitting.",
            "topic": "Model Evaluation",
            "difficulty": "medium",
            "question_type": "conceptual",
            "expected_concepts": ["High bias causes underfitting (model too simple)", "High variance causes overfitting (model memorizes noise)", "Total error = Bias^2 + Variance + Irreducible error"],
            "hints": ["How does model complexity affect generalization on unseen test data?"]
        }
    ],
    "general": [
        {
            "question_text": "Explain the fundamental concepts of this subject and give a practical real-world scenario where it is applied.",
            "topic": "Core Fundamentals",
            "difficulty": "easy",
            "question_type": "conceptual",
            "expected_concepts": ["Clear definition of core principles", "Practical real-world application", "Relevance in current industry"],
            "hints": ["Start with a clean definition, then illustrate with an everyday example."]
        },
        {
            "question_text": "What are the key trade-offs, advantages, and limitations to consider when working in this domain?",
            "topic": "Design & Trade-offs",
            "difficulty": "medium",
            "question_type": "conceptual",
            "expected_concepts": ["Main advantages", "Key bottlenecks or limitations", "Decision criteria for choosing approaches"],
            "hints": ["Consider performance, resource consumption, maintainability, and scalability."]
        },
        {
            "question_text": "Describe a common pitfall or misconception beginners encounter here, and explain how to troubleshoot or prevent it.",
            "topic": "Troubleshooting & Best Practices",
            "difficulty": "hard",
            "question_type": "scenario",
            "expected_concepts": ["Common mistake identified", "Root cause explanation", "Effective preventative technique"],
            "hints": ["Think about edge cases or assumptions that fail in production."]
        }
    ]
}


class QuestionGenerator:
    """
    Generates subject-based interview questions dynamically using Groq LLM,
    tailored to student profile, with reliable offline question bank fallback.
    """

    def __init__(self):
        self._offline_indices: Dict[str, int] = {}

    def generate_question(
        self,
        profile: StudentProfile,
        previous_questions: List[str],
        current_index: int
    ) -> QuestionItem:
        """
        Generates the next question for the student.
        Tries Groq LLM first if configured; falls back gracefully to offline question bank.
        """
        if is_groq_configured():
            try:
                question = self._generate_with_groq(profile, previous_questions, current_index)
                if question:
                    return question
            except Exception as e:
                logger.warning(f"Groq question generation failed ({e}); switching to offline fallback.")

        return self._generate_offline(profile, current_index)

    def _generate_with_groq(
        self,
        profile: StudentProfile,
        previous_questions: List[str],
        current_index: int
    ) -> Optional[QuestionItem]:
        """Calls Groq API to generate a tailored interview question in JSON format."""
        from openai import OpenAI
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url=GROQ_BASE_URL,
            timeout=18.0
        )

        # Context-dependent instructions based on purpose
        purpose_instructions = {
            "placement_interview": "Emphasize conceptual clarity, edge cases, practical application, and algorithmic or design thinking typical of campus placement interviews.",
            "technical_interview": "Focus on deep systems understanding, trade-offs, scalability, code correctness, and practical industry challenges.",
            "exam_prep": "Focus on syllabus definitions, theoretical foundations, textbook concepts, and standard academic explanations.",
            "revision": "Target core principles and test for common gaps or misconceptions.",
            "general_learning": "Provide an accessible, clear, and thought-provoking question suitable for step-by-step learning."
        }.get(profile.purpose, "Provide an engaging and educational interview question.")

        avoid_list = "\n- ".join(previous_questions[-5:]) if previous_questions else "None yet"

        prompt = f"""You are an expert AI Technical Interviewer and Study Tutor.
Generate question #{current_index} for the following student:

STUDENT PROFILE:
- Name: {profile.name}
- Education Level: {profile.education_level.title()} (Branch: {profile.course_branch or 'N/A'}, Year/Sem: {profile.year_semester or 'N/A'})
- Subject: {profile.subject}
- Specific Topic: {profile.topic or 'Any core topic in ' + profile.subject}
- Knowledge Level: {profile.knowledge_level.title()}
- Purpose: {profile.purpose.replace('_', ' ').title()}
- Difficulty: {profile.difficulty.title()}

SESSION GOAL:
{purpose_instructions}

QUESTIONS ALREADY ASKED (DO NOT DUPLICATE OR CLOSELY REPEAT):
- {avoid_list}

REQUIREMENTS:
1. Provide ONE clear, focused question appropriate for {profile.difficulty.title()} difficulty.
2. If this is a coding question or technical subject, ask for explanation or logic without requiring huge boilerplate.
3. Return ONLY a valid JSON object with these EXACT keys:
{{
  "question_text": "The exact question to ask the student",
  "topic": "The specific subtopic (e.g. Memory Management, Joins)",
  "difficulty": "{profile.difficulty}",
  "question_type": "conceptual" or "coding" or "scenario" or "theory",
  "expected_concepts": ["Key concept 1 that must be mentioned", "Key concept 2"],
  "hints": ["A subtle clue that helps without giving away the full answer", "A second more specific clue"]
}}"""

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a professional educational interviewer that outputs ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content or ""
        cleaned = _clean_json_string(content)
        data = json.loads(cleaned)

        q_text = str(data.get("question_text", "")).strip()
        if not q_text:
            return None

        topic = str(data.get("topic", profile.topic or profile.subject)).strip()
        diff = str(data.get("difficulty", profile.difficulty)).strip()
        q_type = str(data.get("question_type", "conceptual")).strip()
        concepts = data.get("expected_concepts", [])
        if isinstance(concepts, str):
            concepts = [concepts]
        hints = data.get("hints", [])
        if isinstance(hints, str):
            hints = [hints]

        return QuestionItem(
            index=current_index,
            question_text=q_text,
            topic=topic,
            difficulty=diff,
            question_type=q_type,
            expected_concepts=concepts,
            hints=hints
        )

    def _generate_offline(self, profile: StudentProfile, current_index: int) -> QuestionItem:
        """Picks a deterministic question from the offline question bank."""
        subject_key = profile.subject.lower().strip()

        # Find matching key in OFFLINE_QUESTIONS
        matched_key = "general"
        for k in OFFLINE_QUESTIONS:
            if k in subject_key or subject_key in k:
                matched_key = k
                break

        bank = OFFLINE_QUESTIONS[matched_key]
        idx = (current_index - 1) % len(bank)
        template = bank[idx]

        topic = template["topic"]
        if profile.topic and matched_key == "general":
            topic = profile.topic

        return QuestionItem(
            index=current_index,
            question_text=template["question_text"],
            topic=topic,
            difficulty=profile.difficulty or template.get("difficulty", "medium"),
            question_type=template.get("question_type", "conceptual"),
            expected_concepts=list(template.get("expected_concepts", [])),
            hints=list(template.get("hints", ["Think about the core definitions and real-world trade-offs."]))
        )
