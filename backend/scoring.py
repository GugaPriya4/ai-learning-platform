import json
from pathlib import Path

PROGRESS_FILE = "../progress.json"

def load_progress():
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"current_level": "Beginner", "topics": {}}

def save_progress(progress: dict):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

def update_mastery(topic_id: str, correct: int, total: int):
    progress = load_progress()
    score = round((correct / total) * 100)
    progress["topics"][topic_id] = score
    save_progress(progress)
    return score

def get_mastery_band(score: int) -> str:
    if score >= 80:
        return "Mastered"
    elif score >= 60:
        return "Needs Revision"
    else:
        return "Weak"

def get_all_mastery(curriculum: dict, level: str) -> dict:
    progress = load_progress()
    result = {}
    for lvl in curriculum["levels"]:
        if lvl["level"] == level:
            for topic in lvl["topics"]:
                tid = topic["id"]
                score = progress["topics"].get(tid, 0)
                result[tid] = {
                    "name": topic["name"],
                    "score": score,
                    "band": get_mastery_band(score)
                }
    return result

def get_weak_topics(curriculum: dict, level: str) -> list:
    mastery = get_all_mastery(curriculum, level)
    weak = [
        {"id": tid, "name": data["name"], "score": data["score"]}
        for tid, data in mastery.items()
        if data["band"] in ["Weak", "Needs Revision"]
    ]
    return sorted(weak, key=lambda x: x["score"])

def get_next_level_topics(curriculum: dict, current_level: str) -> list:
    levels = [l["level"] for l in curriculum["levels"]]
    if current_level not in levels:
        return []
    idx = levels.index(current_level)
    if idx + 1 >= len(levels):
        return []
    next_level = curriculum["levels"][idx + 1]
    return [{"id": t["id"], "name": t["name"]} for t in next_level["topics"]]

def build_adaptive_quiz_topics(curriculum: dict, level: str) -> list:
    weak = get_weak_topics(curriculum, level)
    next_topics = get_next_level_topics(curriculum, level)
    weak_count = 8
    next_count = 2
    selected = weak[:weak_count]
    selected_ids = [t["id"] for t in selected]
    for t in next_topics[:next_count]:
        if t["id"] not in selected_ids:
            selected.append(t)
    return selected

def check_level_gate(curriculum: dict, level: str) -> bool:
    mastery = get_all_mastery(curriculum, level)
    if not mastery:
        return False
    scores = [data["score"] for data in mastery.values()]
    avg = sum(scores) / len(scores)
    return avg >= 85

def advance_level(curriculum: dict) -> str:
    progress = load_progress()
    current = progress.get("current_level", "Beginner")
    levels = [l["level"] for l in curriculum["levels"]]
    idx = levels.index(current)
    if idx + 1 < len(levels):
        progress["current_level"] = levels[idx + 1]
        save_progress(progress)
        return levels[idx + 1]
    return current