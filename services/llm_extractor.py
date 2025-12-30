# services/llm_extractor.py

import json
from typing import Dict
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from services.preference_utils import validate_preferences

PREFERENCE_SCHEMA = {
    "course": None,
    "cuisine": None,
    "keywords": [],
    "max_cook_time": None,
    "nutrition_filters": {},
    "selected_ingredients": [],
    "excluded_ingredients": [],
    "skipped_fields": []
}

SYSTEM_PROMPT = """
You are a food recommendation assistant.

Your task is to extract structured food preferences from user messages.

Rules:
- Output VALID JSON ONLY
- Follow this schema exactly:
{
  "course": null,
  "cuisine": null,
  "keywords": [],
  "max_cook_time": null,
  "nutrition_filters": {},
  "selected_ingredients": [],
  "excluded_ingredients": [],
  "skipped_fields": []
}
- Do NOT guess values
- If a field is not mentioned, keep it null or empty
- max_cook_time must be an integer in minutes
- No explanations, no markdown

IMPORTANT - Detecting user indifference:
If the user expresses indifference or doesn't care about a specific criteria, add that field name to "skipped_fields".
Examples of indifference phrases: "I don't care", "doesn't matter", "no preference", "anything is fine",
"I'm open to anything", "no issue", "whatever", "any", "not important", "skip", "don't mind".

Field mapping for skipped_fields:
- Time/cooking time related indifference → add "max_cook_time"
- Cuisine related indifference → add "cuisine"
- Course/meal type related indifference → add "course"
- Ingredient related indifference → add "keywords"

Example: "I don't care about cooking time" → {"skipped_fields": ["max_cook_time"], ...}
Example: "Any cuisine is fine" → {"skipped_fields": ["cuisine"], ...}
"""

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

def normalize_preferences(prefs: dict) -> dict:
    for k, v in prefs.items():
        if isinstance(v, str):
            prefs[k] = v.lower().strip()
        if isinstance(v, list):
            prefs[k] = [i.lower().strip() for i in v]
    return prefs

def extract_preferences_from_text(user_message: str) -> Dict:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    parsed = json.loads(raw)
    normalized = normalize_preferences(parsed)
    return validate_preferences(normalized)

