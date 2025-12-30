def next_action(preferences: dict) -> dict:
    skipped = preferences.get("skipped_fields", [])

    if not preferences.get("course") and "course" not in skipped:
        return {
            "type": "ask",
            "message": "Is this for breakfast, lunch, dinner, or a snack?"
        }

    if not preferences.get("max_cook_time") and "max_cook_time" not in skipped:
        return {
            "type": "ask",
            "message": "How much time do you want to spend cooking?"
        }

    return {"type": "recommend"}

def relax_preferences(prefs):
    relaxed = prefs.copy()

    if relaxed.get("course"):
        relaxed["course"] = None
    elif relaxed.get("cuisine"):
        relaxed["cuisine"] = None
    elif relaxed.get("keywords"):
        relaxed["keywords"] = []

    return relaxed


# def relax_preferences(prefs):
#     relaxed = prefs.copy()

#     relaxed.setdefault("_relax_count", 0)

#     if relaxed["_relax_count"] >= 3:
#         return relaxed

#     relaxed["_relax_count"] += 1

#     if relaxed.get("max_cook_time"):
#         relaxed["max_cook_time"] += 15
#         return relaxed

#     if relaxed.get("keywords"):
#         relaxed["keywords"] = []
#         return relaxed

#     if relaxed.get("cuisine"):
#         relaxed["cuisine"] = None
#         return relaxed

#     if relaxed.get("course"):
#         relaxed["course"] = None
#         return relaxed

#     return relaxed