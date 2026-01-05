# Technical Documentation

## Food Recommendation Chatbot - System Architecture & Design

**Version:** 1.0.1
**Last Updated:** January 2026

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Data Flow](#data-flow)
4. [Components](#components)
5. [Preference Schema](#preference-schema)
6. [Recommendation Pipeline](#recommendation-pipeline)
7. [API Integration](#api-integration)
8. [Data Structure](#data-structure)
9. [Installation & Setup](#installation--setup)
10. [Configuration](#configuration)
11. [Extending the System](#extending-the-system)

---

## System Overview

The Food Recommendation Chatbot is a conversational AI application built with Streamlit that uses natural language processing to understand user preferences and recommend recipes from a CSV dataset.

### Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| LLM Provider | Groq (LLaMA 3.1 8B) |
| NLP Framework | LangChain |
| Semantic Search | scikit-learn (TF-IDF) |
| Data Processing | Pandas |
| Configuration | python-dotenv |

### Key Features

- Natural language preference extraction
- Multi-stage recommendation pipeline
- Semantic search with TF-IDF
- Progressive constraint relaxation
- Conversational state management
- Explainable recommendations

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│                      (app.py - Streamlit)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Chat UI      │  │ Recipe Cards │  │ Preferences  │          │
│  │              │  │              │  │ Panel        │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                         │
│                      (services/)                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Conversation Management                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │conversation │  │conversation │  │ refinement  │       │  │
│  │  │_policy.py   │  │_guard.py    │  │ _detector.py│       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Preference Processing                    │  │
│  │  ┌─────────────┐  ┌─────────────┐                        │  │
│  │  │llm_extractor│  │preference   │                        │  │
│  │  │.py          │  │_utils.py    │                        │  │
│  │  └─────────────┘  └─────────────┘                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Recommendation Engine                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │recommender  │  │semantic     │  │explanation  │       │  │
│  │  │.py          │  │_ranker.py   │  │_engine.py   │       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌─────────────┐  ┌─────────────────────────────────────────┐  │
│  │data_loader  │  │ data/foods_data.csv                     │  │
│  │.py          │  │ (121 recipes)                           │  │
│  └─────────────┘  └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    EXTERNAL SERVICES                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Groq API (LLaMA 3.1 8B)                    │   │
│  │              - Preference extraction                     │   │
│  │              - Natural language understanding            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Request Processing Flow

```
User Input
    │
    ▼
┌───────────────────┐
│ Greeting Check    │──── Yes ──▶ Return greeting response
│ (is_greeting)     │
└───────────────────┘
    │ No
    ▼
┌───────────────────┐
│ LLM Extraction    │
│ (Groq LLaMA 3.1)  │
└───────────────────┘
    │
    ▼
┌───────────────────┐
│ Refinement        │
│ Detection         │
└───────────────────┘
    │
    ▼
┌───────────────────┐
│ Preference        │
│ Merging           │
└───────────────────┘
    │
    ▼
┌───────────────────┐
│ Policy Decision   │
│ (next_action)     │
└───────────────────┘
    │
    ├─── "ask" ──▶ Return clarifying question
    │
    ▼ "recommend"
┌───────────────────┐
│ Missing Signals   │──── Found ──▶ Return follow-up question
│ Check             │
└───────────────────┘
    │ None
    ▼
┌───────────────────┐
│ Recommendation    │
│ Pipeline          │
└───────────────────┘
    │
    ├─── Empty ──▶ Relax preferences ──▶ Retry
    │
    ▼
┌───────────────────┐
│ Generate          │
│ Explanations      │
└───────────────────┘
    │
    ▼
Display Results
```

---

## Components

### 1. app.py - Main Application

**Purpose:** Streamlit UI and conversation loop management

**Responsibilities:**
- Session state initialization and management
- User input handling
- Message history display
- Recipe card rendering with images and nutrition
- Sidebar controls

**Session State Variables:**

| Variable | Type | Description |
|----------|------|-------------|
| `messages` | List[Dict] | Conversation history |
| `preferences` | Dict | Current user preferences |
| `relaxed_once` | bool | Constraint relaxation flag |
| `semantic_ranker` | SemanticRanker | Cached TF-IDF instance |

---

### 2. llm_extractor.py - NLP Processing

**Purpose:** Extract structured preferences from natural language

**Functions:**

```python
def is_greeting(text: str) -> bool:
    """Detect greeting messages using regex patterns."""

def get_greeting_response() -> str:
    """Return random greeting response."""

def extract_preferences_from_text(user_message: str) -> dict:
    """Extract structured preferences using Groq LLaMA 3.1."""
```

**LLM Configuration:**
- Model: `llama-3.1-8b-instant`
- Temperature: 0 (deterministic)
- Output: Structured JSON

---

### 3. preference_utils.py - Preference Management

**Purpose:** Define schema, merge preferences, normalize values

**Functions:**

```python
BASE_PREFERENCES = {
    "course": None,
    "cuisine": None,
    "keywords": [],
    "max_cook_time": None,
    "selected_ingredients": [],
    "excluded_ingredients": [],
    "diet": None,
    "offset": 0,
    "skipped_fields": []
}

def normalize_course(course: str) -> str:
    """Map course aliases to standard values."""

def merge_preferences(old: dict, new: dict) -> dict:
    """Accumulate preferences across conversation turns."""
```

---

### 4. recommender.py - Recommendation Engine

**Purpose:** Multi-stage filtering and ranking pipeline

**Main Function:**

```python
def recommend_foods(
    df: pd.DataFrame,
    preferences: dict,
    semantic_ranker: SemanticRanker,
    top_k: int = 5
) -> Tuple[pd.DataFrame, bool]:
    """
    Execute recommendation pipeline.

    Returns:
        - DataFrame of top-k recipes
        - Boolean indicating if constraints were relaxed
    """
```

**Pipeline Stages:**
1. Semantic retrieval (top 100 candidates)
2. Hard filters (course, cuisine)
3. Ingredient matching
4. Keyword matching
5. Cook time filtering
6. Soft scoring
7. Final ranking and pagination

---

### 5. semantic_ranker.py - TF-IDF Search

**Purpose:** Semantic similarity ranking

**Class:**

```python
class SemanticRanker:
    def __init__(self, documents: List[str]):
        """Initialize TF-IDF vectorizer with documents."""

    def rank(self, query: str, top_k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Return top-k indices and similarity scores."""
```

**Algorithm:**
- TF-IDF vectorization with English stop words
- Cosine similarity computation
- Returns indices sorted by score (descending)

---

### 6. data_loader.py - Data Processing

**Purpose:** Load and preprocess CSV dataset

**Functions:**

```python
def load_food_dataset(filepath: str) -> pd.DataFrame:
    """Load CSV and apply preprocessing pipeline."""

def build_recipe_documents(df: pd.DataFrame) -> List[str]:
    """Build searchable document strings for TF-IDF."""

def calculate_total_time(time_dict: dict) -> int:
    """Parse time strings and calculate total minutes."""

def parse_nutrition_dict(nutrition: dict) -> dict:
    """Extract nutrition values from JSON."""

def parse_ingredients(ingredients: str) -> Tuple[List, str]:
    """Parse ingredients into list and text formats."""
```

---

### 7. conversation_policy.py - Decision Logic

**Purpose:** Determine conversation flow

**Functions:**

```python
def next_action(preferences: dict) -> dict:
    """
    Determine next action based on preferences.

    Returns:
        {"type": "ask"/"recommend", "message": "..."}
    """

def relax_preferences(prefs: dict) -> dict:
    """Progressively loosen constraints."""
```

---

### 8. conversation_guard.py - Missing Signals

**Purpose:** Identify incomplete preferences

**Functions:**

```python
def missing_signals(preferences: dict) -> List[str]:
    """Return list of missing preference fields."""

def follow_up_question(missing: List[str]) -> str:
    """Generate contextual follow-up question."""
```

---

### 9. refinement_detector.py - Special Requests

**Purpose:** Detect pagination and preference updates

**Function:**

```python
def detect_refinement(text: str) -> dict:
    """
    Detect special commands in user input.

    Detects:
        - Pagination ("next", "more")
        - Time updates ("faster", "quick")
        - Diet changes ("vegetarian")
        - Exclusions ("exclude X")
    """
```

---

### 10. explanation_engine.py - Reasoning

**Purpose:** Generate human-readable explanations

**Function:**

```python
def explain_recommendation(row: pd.Series, preferences: dict) -> str:
    """Generate explanation for why recipe matches preferences."""
```

---

## Preference Schema

```python
{
    # Meal type filter
    "course": str | None,  # "breakfast", "lunch", "dinner", "snack", "dessert"

    # Cuisine filter
    "cuisine": str | None,  # "indian", "italian", "mexican", etc.

    # Search keywords
    "keywords": List[str],  # ["spicy", "healthy", "creamy"]

    # Time constraint (minutes)
    "max_cook_time": int | None,  # 30, 60, etc.

    # Ingredient preferences
    "selected_ingredients": List[str],  # ["chicken", "rice"]
    "excluded_ingredients": List[str],  # ["peanuts", "shellfish"]

    # Dietary restriction
    "diet": str | None,  # "vegetarian", "vegan", etc.

    # Pagination offset
    "offset": int,  # 0, 5, 10, etc.

    # Fields user explicitly doesn't care about
    "skipped_fields": List[str]  # ["course", "cuisine"]
}
```

---

## Recommendation Pipeline

### Stage 1: Semantic Retrieval

```python
# Build query from preferences
query = build_query_from_prefs(preferences)

# Get top 100 semantically similar recipes
indices, scores = semantic_ranker.rank(query, top_k=100)
candidates = df.iloc[indices].copy()
candidates['semantic_score'] = scores
```

### Stage 2: Hard Filters

```python
# Course filter (exact substring match)
if preferences.get("course"):
    candidates = candidates[
        candidates['course'].str.contains(preferences['course'], case=False)
    ]

# Cuisine filter (exact substring match)
if preferences.get("cuisine"):
    candidates = candidates[
        candidates['cuisine'].str.contains(preferences['cuisine'], case=False)
    ]
```

### Stage 3: Ingredient Matching

```python
# Strict matching first
if preferences.get("selected_ingredients"):
    strict = candidates[
        candidates['ingredients_text'].apply(
            lambda x: all(ing in x for ing in preferences['selected_ingredients'])
        )
    ]
    if not strict.empty:
        candidates = strict
    else:
        relaxed = True  # Mark as relaxed
```

### Stage 4: Keyword Matching

```python
# Search keywords in name, summary, keyword field
for kw in preferences.get("keywords", []):
    matches = candidates[
        (candidates['name'].str.contains(kw, case=False)) |
        (candidates['summary'].str.contains(kw, case=False)) |
        (candidates['keyword'].str.contains(kw, case=False))
    ]
    if not matches.empty:
        candidates = matches
```

### Stage 5: Cook Time Filtering

```python
max_time = preferences.get("max_cook_time")
if max_time:
    # Three-tier tolerance
    strict = candidates[candidates['total_time_minutes'] <= max_time * 1.2]
    if strict.empty:
        relaxed_tier = candidates[candidates['total_time_minutes'] <= max_time * 2]
        if relaxed_tier.empty:
            more_relaxed = candidates[candidates['total_time_minutes'] <= max_time * 3]
```

### Stage 6: Soft Scoring

```python
def compute_score(row, preferences):
    score = row['semantic_score']

    # Keyword bonus
    for kw in preferences.get('keywords', []):
        if kw in row['keyword']:
            score += 2
        elif kw in row['summary']:
            score += 1

    # Ingredient bonus
    for ing in preferences.get('selected_ingredients', []):
        if ing in row['ingredients_text']:
            score += 1.5

    # Time bonus/penalty
    max_time = preferences.get('max_cook_time')
    if max_time:
        if row['total_time_minutes'] <= max_time:
            score += 0.5
        else:
            penalty = (row['total_time_minutes'] - max_time) * 0.05
            score -= min(penalty, 1.0)

    return score

candidates['final_score'] = candidates.apply(
    lambda row: compute_score(row, preferences), axis=1
)
```

### Stage 7: Ranking & Pagination

```python
# Sort by final score
candidates = candidates.sort_values('final_score', ascending=False)

# Apply pagination
offset = preferences.get('offset', 0)
results = candidates.iloc[offset:offset + 5]
```

---

## API Integration

### Groq LLM Configuration

```python
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)
```

### Prompt Template

```python
EXTRACTION_PROMPT = """
You are a food preference extraction assistant. Extract structured preferences
from the user's message.

User message: {user_message}

Return a JSON object with these fields:
- course: breakfast, lunch, dinner, snack, or dessert (null if not mentioned)
- cuisine: type of cuisine (null if not mentioned)
- keywords: list of flavor/ingredient hints
- max_cook_time: cooking time in minutes (null if not mentioned)
- selected_ingredients: ingredients to include
- excluded_ingredients: ingredients to exclude
- skipped_fields: fields the user doesn't care about

Return ONLY valid JSON, no explanation.
"""
```

---

## Data Structure

### CSV Schema (foods_data.csv)

| Column | Type | Description |
|--------|------|-------------|
| name | string | Recipe name |
| imgurl | string | Image URL |
| course | string | Meal type (e.g., "Dinner Recipes") |
| cuisine | string | Cuisine type (e.g., "Indian, Pakistani") |
| keyword | string | Search keywords |
| summary | string | Recipe description |
| ingredients | string (JSON list) | Ingredient list |
| nutritions | string (JSON dict) | Nutrition facts |
| Times | string (JSON dict) | Prep/cook times |

### Processed DataFrame Columns

| Column | Type | Source |
|--------|------|--------|
| total_time_minutes | int | Calculated from Times |
| calories_kcal | float | Extracted from nutritions |
| protein_g | float | Extracted from nutritions |
| carbs_g | float | Extracted from nutritions |
| fat_g | float | Extracted from nutritions |
| ingredients_list | list | Parsed from ingredients |
| ingredients_text | string | Joined ingredients |
| food_id | string | MD5 hash of name |

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- Groq API key

### Installation Steps

```bash
# Clone repository
git clone <repository-url>
cd food-recommendation-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "GROQ_API_KEY='your_api_key_here'" > .env

# Run application
streamlit run app.py
```

### Dependencies

```
pandas
streamlit
langchain
langchain_groq
langchain-core
langchain-community
python-dotenv
scikit-learn
```

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| GROQ_API_KEY | Yes | Groq API key for LLM access |

### Streamlit Configuration

Located in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

---

## Extending the System

### Adding New Recipes

1. Add rows to `data/foods_data.csv` with required columns
2. Restart application to reload data

### Adding New Preference Fields

1. Update `BASE_PREFERENCES` in `preference_utils.py`
2. Update extraction prompt in `llm_extractor.py`
3. Update filtering logic in `recommender.py`
4. Update UI in `app.py` if needed

### Adding New Cuisines/Courses

1. Add recipes with new values to CSV
2. Update `normalize_course()` in `preference_utils.py` if aliases needed
3. No other changes required (values are data-driven)

### Changing LLM Provider

1. Install appropriate LangChain integration
2. Update import in `llm_extractor.py`
3. Update LLM initialization with new provider

---

## Performance Considerations

### Caching

- `@st.cache_resource`: Used for data loading and TF-IDF initialization
- Session state: Maintains semantic ranker across requests

### Optimization Tips

- TF-IDF vectors are computed once at startup
- Increase `top_k` in semantic search for larger datasets
- Consider chunking for datasets > 10,000 recipes

### Memory Usage

| Component | Approximate Size |
|-----------|------------------|
| CSV dataset | ~50 MB |
| TF-IDF vectors | ~100 MB |
| Session state | ~5 MB per user |

---

## Troubleshooting

### Common Issues

**"GROQ_API_KEY not found"**
- Ensure `.env` file exists in project root
- Verify key format: `GROQ_API_KEY='your_key'`

**"No recipes found"**
- Check if preferences are too restrictive
- Verify data loaded correctly with `st.write(df.head())`

**Slow response times**
- Groq API latency varies (1-2s typical)
- Consider caching LLM responses for repeated queries

---

*This documentation is intended for developers and technical users working with the Food Recommendation Chatbot system.*
