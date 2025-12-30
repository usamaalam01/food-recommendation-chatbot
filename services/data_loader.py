import pandas as pd
import hashlib
import ast
import re

REQUIRED_COLUMNS = {
    "name",
    "imgurl",
    "course",
    "cuisine",
    "keyword",
    "summary",
    "ingredients",
    "nutritions",
    "Times"
}

def generate_food_id(row) -> str:
    raw = f"{row['name']}_{row['cuisine']}_{row['course']}"
    return hashlib.md5(raw.encode()).hexdigest()

def parse_time_to_minutes(time_str: str) -> int:
    if not isinstance(time_str, str):
        return 0
    time_str = time_str.lower()
    match = re.search(r"(\d+)\s*(hour|hours|minute|minutes)", time_str)
    if not match:
        return 0
    value = int(match.group(1))
    unit = match.group(2)
    return value * 60 if "hour" in unit else value

def calculate_total_time(times_value) -> int:
    total_minutes = 0
    try:
        if isinstance(times_value, str):
            times_dict = ast.literal_eval(times_value)
        elif isinstance(times_value, dict):
            times_dict = times_value
        else:
            return 0
        for _, v in times_dict.items():
            total_minutes += parse_time_to_minutes(v)
    except Exception:
        return 0
    return total_minutes

def extract_numeric_value(value: str) -> float:
    if not isinstance(value, str):
        return 0.0
    match = re.search(r"(\d+(\.\d+)?)", value)
    return float(match.group(1)) if match else 0.0

def parse_nutrition_dict(nutrition_value) -> dict:
    result = {
        "calories_kcal": 0.0,
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 0.0
    }
    try:
        if isinstance(nutrition_value, str):
            nutrition_dict = ast.literal_eval(nutrition_value)
        elif isinstance(nutrition_value, dict):
            nutrition_dict = nutrition_value
        else:
            return result
        for k, v in nutrition_dict.items():
            key = k.lower()
            if "calorie" in key:
                result["calories_kcal"] = extract_numeric_value(v)
            elif "protein" in key:
                result["protein_g"] = extract_numeric_value(v)
            elif "carbohydrate" in key:
                result["carbs_g"] = extract_numeric_value(v)
            elif key == "fat":
                result["fat_g"] = extract_numeric_value(v)
    except Exception:
        return result
    return result

def parse_ingredients(value) -> list:
    try:
        if isinstance(value, str):
            items = ast.literal_eval(value)
        elif isinstance(value, list):
            items = value
        else:
            return []
        return [item.lower().strip() for item in items if isinstance(item, str) and item.strip()]
    except Exception:
        return []

def load_food_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing columns: {missing}")

    text_columns = ["name", "course", "cuisine", "keyword", "summary", "ingredients"]
    for col in text_columns:
        df[col] = df[col].astype(str).str.lower().str.strip()

    df["total_time_minutes"] = df["Times"].apply(calculate_total_time)
    df.dropna(subset=["name", "course"], inplace=True)
    df = df[df["total_time_minutes"] > 0]

    nutrition_df = df["nutritions"].apply(parse_nutrition_dict).apply(pd.Series)
    df = pd.concat([df, nutrition_df], axis=1)

    df["ingredients_list"] = df["ingredients"].apply(parse_ingredients)
    df["ingredients_text"] = df["ingredients_list"].apply(lambda x: ", ".join(x))

    df["food_id"] = df.apply(generate_food_id, axis=1)

    df["cuisine_tags"] = df["cuisine"].apply(parse_tags)
    df["course_tags"] = df["course"].apply(parse_tags)

    df["course_tags"] = df["course"].str.lower().str.split(",").apply(
        lambda x: [t.strip() for t in x]
    )

    return df

def build_recipe_documents(df):
    return (
        df["name"] + " " +
        df["summary"] + " " +
        df["ingredients_text"] + " " +
        df["cuisine"] + " " +
        df["course"]
    ).fillna("").tolist()

def parse_tags(value: str) -> list:
    if not isinstance(value, str):
        return []
    return [v.strip().lower() for v in value.split(",") if v.strip()]    

# df = load_food_dataset("foods_data.csv")

# print(df.columns)