import pandas as pd

def score_row(row, prefs: dict) -> float:
    score = 0.0

    for kw in prefs.get("keywords", []):
        if kw in row["keyword"]:
            score += 2
        if kw in row["summary"]:
            score += 1

    if prefs.get("max_cook_time"):
        score += max(
            0,
            (prefs["max_cook_time"] - row["total_time_minutes"])
            / prefs["max_cook_time"]
        )

    for ing in prefs.get("selected_ingredients", []):
        if ing in row["ingredients_list"]:
            score += 1.5

    return score

def cook_time_penalty(row, max_time):
    if not max_time or pd.isna(row["total_time_minutes"]):
        return 0

    diff = row["total_time_minutes"] - max_time
    return -max(0, diff) * 0.05   # gentle penalty


def build_query_from_prefs(prefs: dict):
    parts = []

    if prefs.get("cuisine"):
        parts.append(prefs["cuisine"])
    if prefs.get("course"):
        parts.append(prefs["course"])
    if prefs.get("keywords"):
        parts.extend(prefs["keywords"])

    return " ".join(parts)

def recommend_foods(df, preferences, semantic_ranker, top_k=5):
    query = build_query_from_prefs(preferences)

    # 1️⃣ Broad semantic retrieval
    indices, scores = semantic_ranker.rank(
        query,
        top_k=min(len(df), 100)
    )

    ranked = df.iloc[indices].copy()
    ranked["semantic_score"] = scores

    # 2️⃣ HARD filters (using substring match for flexibility)
    if preferences.get("course"):
        ranked = ranked[ranked["course"].str.contains(preferences["course"], case=False, na=False)]

    if preferences.get("cuisine"):
        ranked = ranked[ranked["cuisine"].str.contains(preferences["cuisine"], case=False, na=False)]

    if ranked.empty:
        return ranked, False

    # 3️⃣ Cook time handling - try strict first, then soft
    max_time = preferences.get("max_cook_time")
    time_relaxed = False

    if max_time:
        # First try: strict filter with some tolerance (20% buffer)
        time_tolerance = max_time * 1.2
        strict_filtered = ranked[ranked["total_time_minutes"] <= time_tolerance]

        if not strict_filtered.empty:
            ranked = strict_filtered
        else:
            # No recipes within time limit, will show longer recipes
            time_relaxed = True

    # Soft cook time scoring (applies to whatever results we have)
    def cook_time_bonus(row):
        if not max_time or pd.isna(row["total_time_minutes"]):
            return 0.0
        diff = row["total_time_minutes"] - max_time
        return -max(0, diff) / max_time  # penalize overruns softly

    ranked["final_score"] = (
        ranked["semantic_score"]
        + ranked.apply(lambda r: score_row(r, preferences), axis=1)
        + ranked.apply(cook_time_bonus, axis=1)
    )

    ranked = ranked.sort_values("final_score", ascending=False)

    # 4️⃣ Pagination
    offset = preferences.get("offset", 0)
    return ranked.iloc[offset : offset + top_k], time_relaxed
