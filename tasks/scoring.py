from datetime import date, datetime
from typing import Dict, List, Any

DATE_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"]

def parse_date(d):
    """Try to parse a date (string or date). If None or invalid, return None."""
    if d is None:
        return None
    if isinstance(d, date):
        return d
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(d, fmt).date()
            except Exception:
                continue
    return None

def calculate_task_score(task: Dict[str, Any], all_tasks: List[Dict[str, Any]] = None) -> float:
    """
    Returns a numeric score where higher == higher priority.
    Handles:
      - missing fields
      - overdue tasks
      - dependencies (if dependency exists in list and is not done, lower priority)
    """
    score = 0.0

    # Safe field extraction with defaults
    title = task.get("title", "<untitled>")
    importance = int(task.get("importance", 5) or 5)
    estimated_hours = int(task.get("estimated_hours", 1) or 1)
    due_date_raw = task.get("due_date")
    done = bool(task.get("done", False))
    dependencies = task.get("dependencies") or []

    today = date.today()
    due_date = parse_date(due_date_raw)

    # 1) Overdue/Urgency
    if due_date is None:
        # No due date: neutral urgency, small penalty (so tasks with a due date appear ahead)
        score += 0
    else:
        days_until_due = (due_date - today).days
        if days_until_due < 0:
            # Overdue -> very high priority
            score += 200 + abs(days_until_due) * 5
        elif days_until_due == 0:
            score += 100
        elif days_until_due <= 3:
            score += 60
        elif days_until_due <= 7:
            score += 30
        else:
            # further away -> lower urgency
            score += max(0, 10 - (days_until_due / 30))  # small decreasing factor

    # 2) Importance weighting: scale 1-10 into weight
    importance = max(1, min(10, importance))
    score += importance * 8  # Importance heavily weighted

    # 3) Effort - quick wins get a small boost
    if estimated_hours <= 0:
        estimated_hours = 1
    if estimated_hours <= 2:
        score += 12
    elif estimated_hours <= 5:
        score += 5
    else:
        # For large tasks reduce small boost (but don't punish too hard)
        score += max(0, 2 - (estimated_hours / 20))

    # 4) Done flag: completed tasks should have zero priority
    if done:
        score = -9999  # ensure completed tasks sort to the bottom / ignored

    # 5) Dependencies: if dependencies exist and any are not done -> cannot start -> deprioritize
    # We expect dependencies to be either titles or ids; we'll compare with provided all_tasks if available.
    if dependencies and all_tasks:
        # build quick lookup by id or title if present
        unresolved = False
        id_map = {}
        title_map = {}
        for t in all_tasks:
            if "id" in t:
                id_map[str(t["id"])] = t
            if "title" in t:
                title_map[str(t["title"]).lower()] = t
        for dep in dependencies:
            dep_str = str(dep)
            dep_task = id_map.get(dep_str) or title_map.get(dep_str.lower())
            if dep_task:
                if not dep_task.get("done", False):
                    unresolved = True
                    break
            else:
                # if dependency not found in list, we assume it's unresolved (conservative)
                unresolved = True
                break
        if unresolved:
            # reduce priority (can't start until dependencies done)
            score -= 120

    # 6) Minor tie-breakers: shorter estimated_hours -> slightly higher
    score += max(0, (10 - estimated_hours) * 0.5)

    # 7) Safety clamp
    if score < -9000:
        return score
    return round(score, 2)
