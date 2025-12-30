def explain_recommendation(row, preferences):
    reasons = []

    if preferences.get("cuisine") and preferences["cuisine"].lower() in str(row["cuisine"]).lower():
        reasons.append(f"matches your interest in {preferences['cuisine']} cuisine")

    if preferences.get("course") and preferences["course"].lower() in str(row["course"]).lower():
        reasons.append(f"fits your selected course ({preferences['course']})")

    if preferences.get("keywords"):
        matched = [
            k for k in preferences["keywords"]
            if k.lower() in str(row["summary"]).lower()
            or k.lower() in str(row["ingredients_text"]).lower()
        ]
        if matched:
            reasons.append(f"includes {', '.join(matched)}")

    if preferences.get("max_cook_time"):
        if row.get("total_time_minutes") and row["total_time_minutes"] <= preferences["max_cook_time"]:
            reasons.append("respects your time limit")

    if not reasons:
        reasons.append("is a strong overall match to your preferences")

    return " • ".join(reasons)
