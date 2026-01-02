# services/llm_extractor.py

import json
import re
from typing import Dict
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from services.preference_utils import validate_preferences

# Greeting patterns
GREETING_PATTERNS = [
    r"^(hi|hello|hey|hola|howdy|greetings|good\s*(morning|afternoon|evening|day))[\s!.,?]*$",
    r"^(what'?s\s*up|sup|yo)[\s!.,?]*$",
    r"^(how\s*are\s*you|how'?s\s*it\s*going|how\s*do\s*you\s*do)[\s!.,?]*$",
]

GREETING_RESPONSES = [
    "Hello! I'm your food recommendation assistant. Tell me what you're in the mood to eat today!",
    "Hi there! Ready to help you find the perfect recipe. What kind of food are you craving?",
    "Hey! I'm here to help you discover delicious recipes. What would you like to cook today?",
]

def is_greeting(text: str) -> bool:
    """Check if the message is a greeting."""
    text = text.lower().strip()
    for pattern in GREETING_PATTERNS:
        if re.match(pattern, text, re.IGNORECASE):
            return True
    return False

def get_greeting_response() -> str:
    """Return a random greeting response."""
    import random
    return random.choice(GREETING_RESPONSES)

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

