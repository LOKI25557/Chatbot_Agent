import os
import json
from typing import Dict, Any

MEMORY_FILE_PATH = os.path.join(os.path.dirname(__file__), "data", "memory.json")

INITIAL_MEMORY = {
    "preferred_food": "vegetarian",
    "preferred_transport": "bus",
    "likes": [
        "beaches",
        "nature"
    ],
    "dislikes": [],
    "budget_preference": 15000,
    "previous_trips": []
}

def ensure_data_dir():
    os.makedirs(os.path.dirname(MEMORY_FILE_PATH), exist_ok=True)

def load_memory() -> Dict[str, Any]:
    ensure_data_dir()
    if not os.path.exists(MEMORY_FILE_PATH):
        save_memory(INITIAL_MEMORY)
        return INITIAL_MEMORY.copy()
    
    try:
        with open(MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        save_memory(INITIAL_MEMORY)
        return INITIAL_MEMORY.copy()

def save_memory(memory_data: Dict[str, Any]) -> None:
    ensure_data_dir()
    with open(MEMORY_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(memory_data, f, indent=4)


def get_preference(key: str) -> Any:
    memory = load_memory()
    return memory.get(key)

def update_preference(key: str, value: Any) -> None:
    memory = load_memory()
    memory[key] = value
    save_memory(memory)

def add_trip_history(trip_data: Dict[str, Any]) -> None:
    memory = load_memory()
    if "previous_trips" not in memory:
        memory["previous_trips"] = []
    memory["previous_trips"].append(trip_data)
    save_memory(memory)

def clear_memory() -> None:
    save_memory(INITIAL_MEMORY)
