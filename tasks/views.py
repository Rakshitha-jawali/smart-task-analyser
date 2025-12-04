from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from .scoring import calculate_task_score
from datetime import datetime

# Serve the frontend index page at "/"
def ui_index(request):
    """
    Renders frontend/templates/index.html (served at root '/')
    """
    return render(request, 'index.html')


@csrf_exempt
def analyze_tasks(request):
    """
    POST endpoint. Accepts JSON list of tasks (array) or single object with {"tasks": [...]}
    Returns tasks with their computed 'score' sorted descending.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Use POST with JSON body"}, status=405)
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    # Support {"tasks": [...]} or direct list
    if isinstance(body, dict) and "tasks" in body:
        tasks = body["tasks"]
    elif isinstance(body, list):
        tasks = body
    else:
        return HttpResponseBadRequest("Send a JSON list of tasks or {\"tasks\": [...]}")

    # compute scores
    scored = []
    for t in tasks:
        s = calculate_task_score(t, all_tasks=tasks)
        item = dict(t)  # copy
        item["score"] = s
        scored.append(item)

    # sort descending (higher score first)
    scored_sorted = sorted(scored, key=lambda x: x["score"], reverse=True)
    return JsonResponse({"results": scored_sorted}, safe=False)


@csrf_exempt
def suggest_tasks(request):
    """
    Returns top-3 tasks for 'today' with a short explanation.
    Accepts optional POST body with tasks; otherwise returns 400.
    """
    if request.method == "GET":
        return JsonResponse({"error": "Use POST with tasks list in body"}, status=405)
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    tasks = body.get("tasks") if isinstance(body, dict) else (body if isinstance(body, list) else None)
    if not tasks:
        return HttpResponseBadRequest("Provide tasks list")

    scored = []
    for t in tasks:
        s = calculate_task_score(t, all_tasks=tasks)
        item = dict(t)
        item["score"] = s
        scored.append(item)

    scored_sorted = sorted(scored, key=lambda x: x["score"], reverse=True)
    # pick top 3 non-done tasks
    top = [t for t in scored_sorted if not t.get("done", False)][:3]

    explanations = []
    for t in top:
        reason_parts = []
        if t.get("score") is None:
            reason_parts.append("Score unavailable")
        else:
            reason_parts.append(f"Score {t['score']}")
        if t.get("due_date"):
            reason_parts.append(f"Due {t['due_date']}")
        if t.get("importance"):
            reason_parts.append(f"Importance {t['importance']}")
        if t.get("estimated_hours"):
            reason_parts.append(f"Est {t['estimated_hours']}h")
        explanations.append({
            "task": t.get("title", "<untitled>"),
            "score": t["score"],
            "explanation": "; ".join(reason_parts)
        })

    return JsonResponse({"top": explanations}, safe=False)
