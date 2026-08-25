import json
import os
from datetime import datetime, timedelta

def load_seen_ids(filepath: str) -> set:
    if not os.path.exists(filepath):
        return set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("seen_ids", {}).keys())
    except Exception:
        return set()

def save_seen_ids(filepath: str, new_ids_dict: dict):
    data = {"seen_ids": {}}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    seen_ids = data.get("seen_ids", {})
    seen_ids.update(new_ids_dict)

    # Remove entries older than 30 days
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    filtered_seen_ids = {}
    for j_id, date_str in seen_ids.items():
        try:
            date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if date_obj.tzinfo is not None:
                date_obj = date_obj.replace(tzinfo=None)
            if date_obj > cutoff_date:
                filtered_seen_ids[j_id] = date_str
        except Exception:
            filtered_seen_ids[j_id] = date_str

    data["seen_ids"] = filtered_seen_ids

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
