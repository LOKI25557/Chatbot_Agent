import sys
from pathlib import Path

# Ensure Study_Agent is in sys.path for direct imports
STUDY_AGENT_DIR = Path(__file__).resolve().parent
if str(STUDY_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(STUDY_AGENT_DIR))

__version__ = "1.0.0"
