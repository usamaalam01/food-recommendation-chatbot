def missing_signals(preferences: dict) -> list:
    missing = []
    skipped = preferences.get("skipped_fields", [])

    if not preferences.get("cuisine") and "cuisine" not in skipped:
        missing.append("cuisine")

    if not preferences.get("course") and "course" not in skipped:
        missing.append("course")

    if not preferences.get("keywords") and "keywords" not in skipped:
        missing.append("keyword")

    return missing

def follow_up_question(missing: list) -> str:
    if "cuisine" in missing:
        return "Which cuisine are you in the mood for? (e.g., Pakistani, Italian, Chinese)"

    if "course" in missing:
        return "What kind of dish do you want? Main course, appetizer, or dessert?"

    if "keyword" in missing:
        return "Any specific ingredient or craving you have in mind?"

    return "Tell me a bit more about what you'd like to cook."