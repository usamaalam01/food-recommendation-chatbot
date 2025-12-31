from dotenv import load_dotenv
load_dotenv()

import streamlit as st

APP_NAME = "Food Recommendation Chatbot"
APP_VERSION = "v1.0.1"
APP_OWNER = "© 2026 All rights reserved"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from services.llm_extractor import extract_preferences_from_text
from services.preference_utils import BASE_PREFERENCES, merge_preferences
from services.recommender import recommend_foods
from services.data_loader import load_food_dataset,build_recipe_documents
from services.conversation_policy import next_action
from services.preference_utils import normalize_course
from services.semantic_ranker import SemanticRanker
from services.conversation_guard import missing_signals, follow_up_question
from services.refinement_detector import detect_refinement
from services.conversation_policy import relax_preferences
from services.explanation_engine import explain_recommendation

@st.cache_resource
def load_data():
    return load_food_dataset("data/foods_data.csv")

@st.cache_resource
def load_semantic_ranker():
    df = load_food_dataset("data/foods_data.csv")
    documents = build_recipe_documents(df)
    return SemanticRanker(documents)

if "semantic_ranker" not in st.session_state:
    st.session_state.semantic_ranker = load_semantic_ranker()

df = load_data()

if "semantic_ranker" not in st.session_state:
    st.session_state.semantic_ranker = load_semantic_ranker(df)


# @st.cache_data
# def load_documents(df):
#     return build_recipe_documents(df)

# documents = load_documents(df)
# st.session_state.semantic_ranker = SemanticRanker(documents)

# if "semantic_ranker" not in st.session_state:
#     documents = build_recipe_documents(df)
#     st.session_state.semantic_ranker = SemanticRanker(documents)

# documents = build_recipe_documents(df)
# init_semantic_ranker(documents)
# semantic_ranker = SemanticRanker(documents)

# st.write("DATA SAMPLE", df.sample(5)[["name", "course", "cuisine"]])


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    hr {
        margin: 1.5rem 0;
    }
    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# with st.sidebar:
#     # st.header("Session Controls")

#     if st.button("🔄 Start New Recommendation"):
#         st.session_state.messages = []
#         st.session_state.preferences = BASE_PREFERENCES.copy()
#         st.session_state.relaxed_once = False
#         st.rerun()

with st.sidebar:
    # st.markdown("### 🛠️ Session Controls")

    if st.button("🔄 Start New Recommendation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.preferences = BASE_PREFERENCES.copy()
        st.session_state.relaxed_once = False
        st.rerun()

    # st.markdown("---")
    # st.markdown(f"**Version:** {APP_VERSION}")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "preferences" not in st.session_state:
    st.session_state.preferences = BASE_PREFERENCES.copy()

if "relaxed_once" not in st.session_state:
    st.session_state.relaxed_once = False    


st.markdown(
    f"""
    ## 🍽️ What Should I Cook Today?
    *AI-powered recipe recommendations tailored to your taste*
    
    ---
    """,
)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Display recipes if present in the message
        if "recipes" in msg:
            for recipe in msg["recipes"]:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(recipe["imgurl"], width=200)
                with col2:
                    st.markdown(f"**{recipe['name'].title()}**")
                    st.markdown(f"⏱️ {recipe['total_time_minutes']} minutes")
                    st.markdown(recipe["summary"])
                    # Ingredients
                    if "ingredients" in recipe and recipe["ingredients"]:
                        ingredients_list = recipe["ingredients"]
                        st.markdown("**Ingredients**")
                        ingredients_text = ", ".join([ing.title() for ing in ingredients_list[:10]])
                        if len(ingredients_list) > 10:
                            ingredients_text += f" *and {len(ingredients_list) - 10} more...*"
                        st.markdown(ingredients_text)
                    # Nutrition table
                    if "nutrition" in recipe:
                        nutrition = recipe["nutrition"]
                        st.markdown("**Nutrition Facts**")
                        nutrition_html = f"""
                        <table style="width:100%; border-collapse: collapse; font-size: 14px;">
                            <tr style="background-color: #f8f9fa;">
                                <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>Calories</strong></td>
                                <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>Protein</strong></td>
                                <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>Carbs</strong></td>
                                <td style="padding: 8px; border: 1px solid #dee2e6;"><strong>Fat</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border: 1px solid #dee2e6;">{nutrition['Calories']}</td>
                                <td style="padding: 8px; border: 1px solid #dee2e6;">{nutrition['Protein']}</td>
                                <td style="padding: 8px; border: 1px solid #dee2e6;">{nutrition['Carbs']}</td>
                                <td style="padding: 8px; border: 1px solid #dee2e6;">{nutrition['Fat']}</td>
                            </tr>
                        </table>
                        """
                        st.markdown(nutrition_html, unsafe_allow_html=True)
                st.markdown(f"🧠 *Why this?* {recipe['explanation']}")
                st.divider()

user_input = st.chat_input("Tell me what you're in the mood for...")

if user_input:
    st.session_state.relaxed_once = False
    # Store user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Extract preferences using LLM
    new_prefs = extract_preferences_from_text(user_input)
    refinements = detect_refinement(user_input)

    new_prefs = {**new_prefs, **refinements}

    if new_prefs.get("course"):
        new_prefs["course"] = normalize_course(new_prefs["course"])

    # Merge into session memory
    st.session_state.preferences = merge_preferences(
        st.session_state.preferences,
        new_prefs
    )

    # Get recommendations
    decision = next_action(st.session_state.preferences)

    if decision["type"] == "ask":
        assistant_text = decision["message"]

        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_text}
        )
        st.rerun()

    else:
        missing = missing_signals(st.session_state.preferences)

        if missing:
            assistant_text = follow_up_question(missing)
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_text
            })
        else:
            if "offset" not in st.session_state.preferences:
                st.session_state.preferences["offset"] = 0

            recs, time_relaxed = recommend_foods(
                df,
                st.session_state.preferences,
                st.session_state.semantic_ranker
            )

            # If no results, try relaxing preferences once
            relaxed_message = ""
            if recs.empty and not st.session_state.relaxed_once:
                relaxed = relax_preferences(st.session_state.preferences)

                if relaxed != st.session_state.preferences:
                    st.session_state.preferences = relaxed
                    st.session_state.preferences["offset"] = 0
                    st.session_state.relaxed_once = True
                    relaxed_message = "I relaxed some constraints to find better matches.\n\n"

                    # Retry with relaxed preferences
                    recs, time_relaxed = recommend_foods(
                        df,
                        st.session_state.preferences,
                        st.session_state.semantic_ranker
                    )

            # Add message if time constraint was relaxed
            if time_relaxed and not relaxed_message:
                relaxed_message = "No recipes found within your time limit. Showing closest matches.\n\n"

            if recs.empty:
                if relaxed_message:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": relaxed_message + "Unfortunately, I still couldn't find any matching recipes. Try changing cuisine, time, or ingredients."
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "No recipes match your preferences. Try changing cuisine, time, or ingredients."
                    })

            else:
                # Build recommendation message with recipe data
                recipe_data = []
                for _, row in recs.iterrows():
                    explanation = explain_recommendation(row, st.session_state.preferences)
                    recipe_data.append({
                        "imgurl": row["imgurl"],
                        "name": row["name"],
                        "total_time_minutes": row["total_time_minutes"],
                        "summary": row["summary"],
                        "explanation": explanation,
                        "ingredients": row.get("ingredients_list", []),
                        "nutrition": {
                            "Calories": f"{row.get('calories_kcal', 0):.0f} kcal",
                            "Protein": f"{row.get('protein_g', 0):.1f} g",
                            "Carbs": f"{row.get('carbs_g', 0):.1f} g",
                            "Fat": f"{row.get('fat_g', 0):.1f} g"
                        }
                    })

                time_note = ""
                if st.session_state.preferences.get("max_cook_time"):
                    time_note = f"⏱️ Showing recipes around {st.session_state.preferences['max_cook_time']} minutes\n\n"

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": relaxed_message + time_note + "### 🍽️ Here's what I recommend:",
                    "recipes": recipe_data
                })

        st.rerun()

with st.expander("🔍 Current Preferences"):
    prefs = st.session_state.preferences
    lines = []

    if prefs["course"]:
        lines.append(f"• Course: {prefs['course'].title()}")
    if prefs["cuisine"]:
        lines.append(f"• Cuisine: {prefs['cuisine'].title()}")
    if prefs["keywords"]:
        lines.append(f"• Keywords: {', '.join(prefs['keywords'])}")
    if prefs["max_cook_time"]:
        lines.append(f"• Max Cook Time: {prefs['max_cook_time']} minutes")
    if prefs["selected_ingredients"]:
        lines.append(f"• Include: {', '.join(prefs['selected_ingredients'])}")
    if prefs["excluded_ingredients"]:
        lines.append(f"• Exclude: {', '.join(prefs['excluded_ingredients'])}")

    

    st.markdown("\n".join(lines) if lines else "No preferences yet.")                

    st.markdown("---")

# st.markdown(
#     f"""
#     <div style="text-align: center; color: gray; font-size: 0.85rem;">
#         {APP_NAME} · {APP_VERSION}<br>
#         {APP_OWNER}
#     </div>
#     """,
#     unsafe_allow_html=True
# )

st.markdown(
    f"""
    <style>
    .app-footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        text-align: center;
        padding: 6px;
        font-size: 12px;
        color: gray;
        border-top: 1px solid #eee;
        z-index: 999;
    }}
    </style>

    <div class="app-footer">
        {APP_NAME} · {APP_VERSION} · {APP_OWNER}
    </div>
    """,
    unsafe_allow_html=True
)