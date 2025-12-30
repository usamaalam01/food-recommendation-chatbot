from copy import deepcopy

BASE_PREFERENCES = {
    "course": None,
    "cuisine": None,
    "keywords": [],
    "max_cook_time": None,
    "selected_ingredients": [],
    "excluded_ingredients": [],
    "diet": None,
    "offset": 0
}

COURSE_ALIASES = {
    "dinner": "dinner recipes",
    "lunch": "dinner recipes",
    "main": "main course",
    "snack": "energy snack",
    "dessert": "sweet"
}

def normalize_course(course: str | None):
    if not course:
        return None

    course = course.lower().strip()

    if "dinner" in course:
        return "dinner"
    if "lunch" in course:
        return "dinner"  # lunch maps to dinner recipes in dataset
    if "breakfast" in course:
        return "breakfast"
    if "snack" in course:
        return "snack"
    if "dessert" in course:
        return "dessert"
    if "main" in course:
        return "main course"
    if "appetizer" in course:
        return "appetizer"
    if "soup" in course:
        return "soup"
    if "side" in course:
        return "side dish"

    return course  # return original if no mapping found

def validate_preferences(prefs: dict) -> dict:
    validated = deepcopy(BASE_PREFERENCES)

    for key in validated:
        if key in prefs and prefs[key] not in [None, [], {}]:
            validated[key] = prefs[key]

    return validated


def merge_preferences(old: dict, new: dict) -> dict:
    merged = old.copy()

    for key, value in new.items():
        if value is None:
            continue

        if key == "keywords":
            merged["keywords"] = list(set(merged["keywords"] + value))

        elif key in ["selected_ingredients", "excluded_ingredients"]:
            merged[key] = list(set(merged[key] + value))

        elif key == "offset":
            merged["offset"] += value

        else:
            merged[key] = value

    return merged