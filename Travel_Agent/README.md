# ✈️ TripMate — Mini Autonomous Travel Agent

## 1. Project Title
TripMate — Mini Autonomous Travel Agent

## 2. Problem Statement
Many applications claim to be "AI Agents" but are just simple chatbots. This project demonstrates a true agentic workflow where the AI plans, uses tools, observes results, reasons about feasibility, automatically re-plans upon failure, and waits for human approval before performing an action.

## 3. Objective
Build a Python AI agent that can understand a travel request, identify goals, remember user preferences, create a travel plan, use simulated travel tools, and gracefully handle deterministic failures through reasoning and re-planning.

## 4. Architecture
```text
USER
  ↓
STREAMLIT UI
  ↓
TRAVEL AGENT / AGENT CONTROLLER
  ├── Goal Identification
  ├── Memory
  ├── GROQ LLM (via OpenAI SDK)
  ├── Planner
  ├── Tool Selection
  ├── Tool Execution
  ├── Observation
  ├── Reasoning
  ├── Re-planning
  ├── Human Approval
  └── Action
  ↓
UPDATE MEMORY
```

## 5. Components
- `models.py`: Data structures using `dataclasses` (TravelRequest, ToolResult, TravelPlan, AgentState).
- `config.py`: Environment variable loading.
- `llm.py`: Groq LLM integration and fallback logic.
- `memory.py`: Persistent JSON-based memory.
- `tools.py`: Simulated determinisitic tools for transport, hotels, weather, activities, and budget calculation.
- `planner.py`: Orchestrates tools to create and validate plans.
- `agent.py`: The main controller coordinating the state and lifecycle.
- `app.py`: Streamlit User Interface.

## 6. Agent Lifecycle
1. **RECEIVE REQUEST**: Get input from UI.
2. **IDENTIFY GOAL**: Parse request to `TravelRequest`.
3. **LOAD MEMORY**: Fetch user preferences.
4. **CREATE PLAN**: Call tools to search transport and hotels.
5. **OBSERVE & REASON**: Check if the plan violates constraints (like hotel unavailability or budget overflow).
6. **RE-PLAN (if needed)**: Search alternative options and recalculate.
7. **HUMAN APPROVAL**: Pause for user confirmation.
8. **ACTION**: Simulate booking upon approval.
9. **UPDATE MEMORY**: Save trip history.

## 7. Folder Structure
```text
Chatbot_Agent/
│
├── .venv/                          # Root virtual environment (Python 3.13)
├── .env                            # Root environment file (not committed)
├── .env.example                    # Clean placeholder template
├── .gitignore                      # Workspace-level ignore rules
├── requirements.txt                # Workspace root dependency manifest
├── README.md                       # Workspace root overview
│
└── Travel_Agent/
    ├── app.py                      # Streamlit UI & entrypoint
    ├── agent.py                    # TravelAgent orchestrator & lifecycle
    ├── planner.py                  # Itinerary planner & replanner
    ├── memory.py                   # Persistent memory (data/memory.json)
    ├── tools.py                    # Simulated travel tools
    ├── models.py                   # Dataclasses & contracts
    ├── llm.py                      # Groq client & reasoning engine
    ├── config.py                   # Configuration & .env path resolver
    ├── requirements.txt            # Local agent requirements
    ├── README.md                   # Travel Agent documentation
    ├── data/
    │   └── memory.json             # Persistent trip memory (JSON)
    └── tests/
        ├── __init__.py
        └── test_tripmate.py        # 22 automated tests
```

## 8. Virtual Environment Setup
TripMate shares the root virtual environment at `Chatbot_Agent/.venv/`. Do not create a separate `.venv` inside `Travel_Agent/`.

From the project root (`Chatbot_Agent/`):

```powershell
# Activate the root virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Or run commands directly with the root python interpreter:
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 9. Groq API Setup & Environment Variables
Create or edit `.env` in the workspace root (`Chatbot_Agent/.env`):

```dotenv
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

*Note on models: Groq has decommissioned older models such as `llama3-8b-8192`. Use a supported model such as `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, or `openai/gpt-oss-20b`.*

## 10. Running the Application
From the workspace root (`Chatbot_Agent/`):

```powershell
.\.venv\Scripts\python.exe -m streamlit run .\Travel_Agent\app.py
```

The application will be accessible in your web browser at `http://localhost:8501`.

## 11. Running Automated Tests
From the workspace root (`Chatbot_Agent/`):

```powershell
.\.venv\Scripts\python.exe -m pytest .\Travel_Agent -q
```

## 12. Troubleshooting

### `ImportError: cannot import name 'is_groq_configured' from 'config'`
- **Cause**: Running from the root directory when `Travel_Agent/` was not in `sys.path`, or running with a stale cached Streamlit process.
- **Fix**: [app.py](file:///c:/Users/Lokesh/OneDrive/Desktop/Projects/Chatbot_Agent/Travel_Agent/app.py) explicitly inserts its containing directory into `sys.path` on line 1, ensuring all local modules import cleanly regardless of the launch working directory.

### `BadRequestError: The model has been decommissioned`
- **Cause**: `.env` specifies an older model (e.g. `llama3-8b-8192`) that Groq no longer hosts.
- **Fix**: Update `GROQ_MODEL=llama-3.3-70b-versatile` in `.env`. TripMate automatically detects decommissioned models, logs the status in the UI, and falls back to deterministic Demo Mode without crashing.

## 13. Demo Mode vs. Groq LLM Mode
- **🟡 DEMO MODE**: Active when no API key is set, or if an API failure/decommissioned model is encountered. Uses deterministic parsing and rules so the agent remains 100% functional offline.
- **🟢 GROQ LLM MODE**: Active when a valid Groq API key and supported model are configured. Employs Groq LLM for natural language extraction and reasoning.

## 15. Tools
Tools in `tools.py` are strictly simulated.
- `search_transport()`, `search_hotels()`, `check_weather()`, `find_activities()`
- `calculate_budget()`: Uses precise Python arithmetic. LLM is NOT used for math.
- `book_transport()`, `book_hotel()`: Simulated actions. No real money or endpoints involved.

## 16. Memory
JSON-based memory (`data/memory.json`) persists user preferences (like vegetarian food, preferred transport) and previous trip history.

## 17. Planning
The `Planner` in `planner.py` evaluates tools to assemble a `TravelPlan` respecting budget and duration.

## 18. Reasoning
The agent observes validation results. If a failure occurs, it formulates a reasoning step to explain why it must adjust its approach.

## 19. Observations
The agent explicitly logs what happens when a tool is called (e.g., "Hotel A unavailable").

## 20. Re-planning
If the observation is negative, the agent executes `replan()`, selecting alternative parameters (like switching to Hotel B).

## 21. Human-in-the-loop
The agent will NEVER autonomously perform a booking. It halts execution, presenting the final itinerary and estimated budget to the human for a definitive `APPROVE` or `CANCEL` decision.

## 22. Successful Execution
**How to test:**
1. Click **PLAN MY TRIP**.
2. The agent will execute flawlessly, finding transport and hotels, calculating budget, and halting at the Approval step.
3. Click **APPROVE BOOKING** to complete the simulated action.

## 23. Failure/Re-planning Execution
**How to test:**
1. Click **RUN FAILURE / RE-PLANNING DEMO**.
2. The agent is forced into a scenario where the first selected hotel (Hotel A) is strictly unavailable.
3. Observe the log: It will identify the failure, reason about the issue, select a different hotel (Hotel B), recalculate the budget, and finally ask for Human Approval.

## 24. Limitations
- Tools are simulated.
- Fallback natural language parsing in Demo Mode is very rudimentary.

## 25. Future Improvements
- Connect to real flight/hotel APIs.
- Enhance multi-step reasoning with LangChain/LangGraph (omitted here for educational clarity).

---

## How TripMate satisfies the Class Activity

**Required Concepts Mapped:**
- **Goal:** Travel objective extracted from user request.
- **LLM:** Groq LLM for natural-language understanding and reasoning via OpenAI SDK.
- **Memory:** Persistent user preferences and trip history (`memory.json`).
- **Planning:** Transport + hotel + activity + budget planning orchestrated in `planner.py`.
- **Reasoning:** Feasibility and constraint checking (budget limit, availability).
- **Tools:** Transport, hotel, weather, activity, and budget tools.
- **Actions:** Simulated booking.
- **Observations:** Tool results (success or failure).
- **Re-planning:** Alternative plan selection after tool failure (e.g., Hotel A unavailable).
- **Human Approval:** Strict approval step before booking execution.

**8 Required Deliverables:**
1. **Agent architecture diagram:** Defined in README Section 4.
2. **Python implementation:** Completed using Python 3 without heavy abstractions.
3. **Tool definitions:** Structured in `tools.py`.
4. **Memory design:** JSON persistence implemented in `memory.py`.
5. **Agent lifecycle flow:** Represented functionally in `agent.py`.
6. **One successful execution:** Demonstrable via "PLAN MY TRIP".
7. **One failure/re-planning example:** Demonstrable via "RUN FAILURE / RE-PLANNING DEMO".
8. **Human-in-the-loop safety rule:** Implemented before any `book_*` tool can be called.
