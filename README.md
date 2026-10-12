# TripMate — Autonomous Travel Agent

TripMate is an autonomous AI travel planning agent featuring goal identification, memory retrieval, deterministic and LLM planning, simulated tool execution, reasoning, dynamic replanning upon constraint failures, and a strict human-in-the-loop approval gate.

## Quick Start

From the workspace root:

```powershell
# Run the automated test suite
.\.venv\Scripts\python.exe -m pytest .\Travel_Agent -q

# Launch the Streamlit application
.\.venv\Scripts\python.exe -m streamlit run .\Travel_Agent\app.py
```