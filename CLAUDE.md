# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A conversational food recommendation chatbot built with Streamlit that uses natural language processing to understand user preferences and recommend recipes from a CSV dataset.

## Commands

### Run the Application
```bash
streamlit run app.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Environment Setup

Requires a `.env` file with `GROQ_API_KEY` for the Groq LLM service (used for preference extraction).

## Architecture

### Data Flow
1. User message → LLM extracts structured preferences (llm_extractor.py)
2. Conversation policy determines if more info needed or ready to recommend (conversation_policy.py)
3. If recommending: semantic search retrieves candidates → hard filters applied → soft scoring → ranked results

### Key Components

**app.py** - Streamlit UI and main conversation loop. Manages session state for messages, preferences, and pagination.

**services/llm_extractor.py** - Uses Groq's Llama 3.1 to parse natural language into structured preference JSON (course, cuisine, keywords, max_cook_time, ingredients).

**services/recommender.py** - Core recommendation logic:
- `build_query_from_prefs()` - Converts preferences to search query
- `recommend_foods()` - Orchestrates semantic retrieval → hard filters (course/cuisine) → soft scoring (keywords, cook time, ingredients) → pagination

**services/semantic_ranker.py** - TF-IDF based semantic search using scikit-learn. Ranks recipe documents by cosine similarity to query.

**services/data_loader.py** - Loads and preprocesses the CSV dataset. Parses time strings to minutes, extracts nutrition values, normalizes text fields.

**services/conversation_policy.py** - State machine logic: `next_action()` determines whether to ask clarifying questions or proceed to recommendations. `relax_preferences()` progressively loosens filters when no results found.

**services/preference_utils.py** - `BASE_PREFERENCES` schema, `merge_preferences()` for accumulating preferences across conversation turns, `normalize_course()` for mapping aliases.

**services/conversation_guard.py** - Identifies missing preference signals and generates follow-up questions.

### Preference Schema
```python
{
    "course": None,      # breakfast, lunch, dinner, snack, dessert
    "cuisine": None,     # e.g., "indian", "italian"
    "keywords": [],      # flavor/ingredient hints
    "max_cook_time": None,  # minutes (integer)
    "selected_ingredients": [],
    "excluded_ingredients": [],
    "diet": None,
    "offset": 0          # pagination
}
```

### Data
- **data/Foods_data.csv** - Recipe dataset with columns: name, imgurl, course, cuisine, keyword, summary, ingredients, nutritions, Times
