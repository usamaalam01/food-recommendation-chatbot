def detect_refinement(text: str) -> dict:
    text = text.lower()

    refinements = {}

    if "another" in text or "next" in text:
        refinements["offset"] = 3

    if "faster" in text or "quick" in text:
        refinements["max_cook_time"] = 30

    if "vegetarian" in text:
        refinements["diet"] = "vegetarian"

    if "exclude" in text:
        words = text.split()
        if "chicken" in words:
            refinements.setdefault("excluded_ingredients", []).append("chicken")

    return refinements