import json
import os
from datetime import date
from typing import List, Dict, Any
from models.user_profile import UserProfile

DATA_FILE = "study_data.json"

def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_data(data: Dict[str, Any]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_profile(profile: UserProfile):
    data = load_data()
    data["profile"] = profile.to_dict()
    save_data(data)

def get_user_profile():
    data = load_data()
    profile_data = data.get("profile")
    if profile_data:
        return UserProfile.from_dict(profile_data)
    return None

def get_today_tasks_status() -> List[Dict]:
    data = load_data()
    today_str = str(date.today())
    current_tasks = data.get("current_tasks", {})
    if current_tasks.get("date") == today_str:
        return current_tasks.get("items", [])
    return []

def save_today_tasks_status(tasks: List[Dict]):
    data = load_data()
    data["current_tasks"] = {
        "date": str(date.today()),
        "items": tasks
    }
    save_data(data)

def save_daily_history(entry: Dict):
    data = load_data()
    if "history" not in data:
        data["history"] = []
    
    today_str = str(date.today())
    existing_index = next((i for i, item in enumerate(data["history"]) if item["date"] == today_str), -1)
    
    if existing_index != -1:
        data["history"][existing_index] = entry
    else:
        data["history"].append(entry)
        
    save_data(data)

def get_history() -> List[Dict]:
    data = load_data()
    return data.get("history", [])