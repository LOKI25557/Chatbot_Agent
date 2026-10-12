# 🎓 AI Study Agent & Technical Interviewer

An interactive AI-powered tutor and technical interviewer built inside `Chatbot_agent/Study_Agent/`. The Study Agent collects student information conversationally, conducts personalized subject-based question sessions one question at a time, evaluates student answers fairly on a 0–5 rubric, explains misconceptions, and produces structured performance reports.

---

## 🌟 Features

- **Conversational Profile Collection**: Welcomes the student and collects details step-by-step (name, education level, branch/semester, subject, topic, knowledge level, purpose, difficulty, and question count) with sensible defaults and educational branching (school students are not asked for college semester or branch).
- **Universal Subject Coverage**: Supports Python, Java, C/C++, Data Structures & Algorithms, DBMS/SQL, Operating Systems, Computer Networks, AI/ML, Mathematics, Web Development, Software Engineering, and any custom subject entered by the student.
- **Dynamic Question Generation**: Generates focused questions tailored to education level, difficulty, and session purpose (placement interviews emphasize conceptual depth and practical edge cases; exam prep focuses on syllabus concepts and definitions).
- **Interactive Control Commands**:
  - `hint` — Receive a subtle clue without revealing the complete solution.
  - `skip` — Skip the current question and proceed to the next topic.
  - `explain` — Receive an in-depth conceptual explanation.
  - `repeat` — Re-read the current question.
  - `stop` — End the session early and generate a partial-session report.
  - `quit` — Gracefully exit the application.
- **Fair 0–5 Evaluation Rubric**:
  - `0`: No relevant answer or completely incorrect.
  - `1`: Very limited understanding with major misconceptions.
  - `2`: Partially correct with significant gaps.
  - `3`: Mostly correct with some missing details or slight imprecision.
  - `4`: Correct and well explained.
  - `5`: Complete, accurate, and clearly explained.
- **Data-Driven Performance Report**: Generates an evidence-backed report with overall percentage, mastered concepts, topics needing improvement, detailed mistake breakdowns, revision recommendations, and suggested next steps.
- **Dual User Interface**:
  - **Terminal CLI** (`main.py`): Clean, beginner-friendly conversational command-line interface.
  - **Streamlit Web UI** (`app.py`): Full-featured interactive web app with quick action buttons, live status indicators, and collapsible feedback cards.
- **Hermetic Offline Fallback**: Includes a built-in deterministic question bank and heuristic evaluator for practice when an API key is not configured or network connectivity is unavailable.

---

## 📁 Folder Structure

```
Chatbot_agent/
│
├── Travel_Agent/                # Pre-existing travel agent (unchanged)
│
├── Study_Agent/                 # Independent Study Agent module
│   ├── main.py                  # CLI application entry point and interactive loop
│   ├── app.py                   # Streamlit web application interface
│   ├── config.py                # Environment configuration & safe Groq connectivity verification
│   ├── student_profile.py       # StudentProfile model & conversational input collection
│   ├── question_generator.py    # AI question generation & offline question bank
│   ├── answer_evaluator.py      # 0–5 answer evaluation, hint, and explanation engine
│   ├── session_manager.py       # In-memory session tracking, question advancement & command detection
│   ├── report_generator.py      # SessionReport calculation & CLI / Markdown formatters
│   ├── agent.py                 # StudyAgent orchestrator connecting modules
│   ├── commands.py              # Command detection re-exports
│   ├── evaluator.py             # Evaluation helper re-exports
│   ├── llm.py                   # Unified LLMClient interface
│   ├── models.py                # Data models with collision-safe cross-agent protection
│   ├── session.py               # Session manager re-exports
│   ├── requirements.txt         # Study Agent dependencies
│   ├── .env.example             # Safe environment variable template
│   ├── .gitignore               # Ignores .env and cache directories
│   ├── README.md                # Documentation and running instructions
│   │
│   └── tests/                   # Automated unit test suite
│       ├── test_session_manager.py
│       ├── test_evaluation.py
│       ├── test_student_profile.py
│       ├── test_question_generator.py
│       ├── test_commands.py
│       ├── test_agent.py
│       ├── test_session.py
│       └── test_evaluator.py
│
├── .env.example                 # Root environment template
└── requirements.txt             # Root requirements
```

---

## ⚙️ Prerequisites

- **Python**: Version 3.10, 3.11, 3.12, or 3.13.
- **Groq API Key (Optional for Live LLM)**: Obtain a free API key at [console.groq.com](https://console.groq.com). If no key is configured, the agent runs automatically in offline demo mode.

---

## 🚀 Setup & Installation

### 1. Create and Activate Virtual Environment

#### Windows (PowerShell):
```powershell
# From the Chatbot_Agent project root:
python -m venv .venv

# Activate virtual environment:
.\.venv\Scripts\Activate.ps1
```

*(If PowerShell script execution is restricted, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

#### macOS / Linux (Bash):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 2. Install Dependencies

```bash
pip install -r Study_Agent/requirements.txt
```

---

### 3. Configure Environment Variables

Copy `.env.example` to `.env` in the project root or inside `Study_Agent/`:

#### Windows PowerShell:
```powershell
Copy-Item Study_Agent/.env.example .env
```

#### macOS / Linux:
```bash
cp Study_Agent/.env.example .env
```

Open `.env` and set your Groq API credentials:
```ini
GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

> **Security Note:** Never commit `.env` to Git. The `.gitignore` file automatically excludes `.env`.

---

## 💻 Running the Application

### Option A: Interactive Command-Line Interface (CLI)

```powershell
# From the project root:
python Study_Agent/main.py
```

#### CLI Interaction Walkthrough:
1. Greets you and displays current LLM status (Active Groq vs Offline Fallback).
2. Asks for your name, education level, branch/semester (if applicable), subject, specific topic, knowledge level, purpose, difficulty, and question count.
3. Displays a configuration summary and asks for confirmation.
4. Presents one question at a time:
   - Type your answer to receive detailed feedback, a 0–5 score, missed points, and model solutions.
   - Or type `hint`, `skip`, `explain`, `repeat`, `stop`, or `quit`.
5. Prints a performance report upon completion or early stop.

---

### Option B: Streamlit Web Interface

```powershell
# From the project root:
streamlit run Study_Agent/app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

Features in Web UI:
- **Profile Form**: Clean input controls with slider selectors and educational branching.
- **Interview View**: Progress bar ("Question 2 of 5"), question card, instant action buttons (💡 Hint, 📖 Explain, ⏭️ Skip, ⏹️ Stop), and answer text area.
- **Feedback & Report View**: Metrics cards, mastery lists, revision advice, and collapsible mistake breakdowns.

---

## 🧪 Running Automated Tests

Run the hermetic test suite with `pytest`:

```powershell
# Run Study Agent test suite (39 tests):
pytest Study_Agent/tests

# Run both Study Agent and Travel Agent test suites together (61 tests):
pytest Travel_Agent/tests Study_Agent/tests
```

All unit tests use deterministic mocked responses or the offline fallback engine, ensuring tests execute quickly without network calls or paid API usage.

---

## 🔧 Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `API key not configured (Demo Mode active)` | `GROQ_API_KEY` is empty or missing in `.env` | Add your Groq API key to `.env` in the workspace root or `Study_Agent/.env`. |
| `Authentication failed (invalid API key)` | Invalid Groq API key | Verify your key at [console.groq.com](https://console.groq.com) and update `.env`. |
| `Model not found or decommissioned` | The configured model name is outdated | In `.env`, set `GROQ_MODEL=llama-3.3-70b-versatile` or `GROQ_MODEL=llama-3.1-8b-instant`. |
| `Rate limit exceeded (429)` | Groq tier rate limit reached | The agent automatically falls back to offline questions during outages. Wait a moment or upgrade your tier. |
| `UnicodeEncodeError on Windows console` | Terminal code page does not support emojis | `main.py` automatically configures UTF-8 for `sys.stdout`. Ensure PowerShell uses UTF-8: `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`. |

---

## 📌 Architecture & Design Decisions

1. **Independent Submodule**: `Study_Agent/` has its own configurations, models, and test suite. The pre-existing `Travel_Agent` in the parent directory remains untouched and fully functional.
2. **In-Memory Session State**: Session history, answers, scores, and questions are stored strictly in-memory during execution. No database setup is required. Session data resets cleanly upon program exit.
3. **Graceful Fallback**: If network fails or no API key is supplied, the agent continues operating smoothly using an offline question bank and keyword-based evaluation engine.
4. **Collision Protection**: Data models are isolated in `student_profile.py`, `session_manager.py`, `answer_evaluator.py`, and `report_generator.py` to prevent Python `sys.modules` collisions with `Travel_Agent/models.py`.

---

## 🔮 Future Improvements

- Persistent session storage (SQLite / JSON) to track progress across multiple days.
- Interactive code execution sandbox for running Python/Java code answers in real time.
- Voice-enabled interview mode using speech-to-text and text-to-speech.
- Exporting session performance reports as downloadable PDF or JSON files.
