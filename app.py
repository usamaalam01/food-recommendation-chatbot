from dotenv import load_dotenv
load_dotenv()

import streamlit as st

APP_NAME = "Food Recommendation Chatbot"
APP_VERSION = "v1.0.0"
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

user_input = st.chat_input("Tell me what you're in the mood for...")

if user_input:
    st.session_state.relaxed_once = False
    # Store user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

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

        with st.chat_message("assistant"):
            st.markdown(assistant_text)

    else:
        missing = missing_signals(st.session_state.preferences)

        with st.chat_message("assistant"):
            if missing:
                st.markdown(follow_up_question(missing))
            else:

                if "offset" not in st.session_state.preferences:
                    st.session_state.preferences["offset"] = 0

                # st.session_state.preferences["offset"] = st.session_state.offset

                if st.session_state.preferences.get("max_cook_time"):
                    st.caption(
                        f"⏱️ Showing recipes around {st.session_state.preferences['max_cook_time']} minutes"
                    )

                recs = recommend_foods(
                    df,
                    st.session_state.preferences,
                    st.session_state.semantic_ranker
                )



                if recs.empty:
                    if not st.session_state.relaxed_once:
                        relaxed = relax_preferences(st.session_state.preferences)

                        if relaxed != st.session_state.preferences:
                            st.session_state.preferences = relaxed
                            st.session_state.preferences["offset"] = 0
                            st.session_state.relaxed_once = True

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "I relaxed some constraints to find better matches."
                            })

                            st.rerun()
                        else:
                            st.markdown(
                                "I couldn’t find any recipes even after relaxing preferences."
                            )
                    else:
                        st.markdown(
                            "No recipes match your preferences. Try changing cuisine, time, or ingredients."
                        )

                else:
                    st.markdown("### 🍽️ Here’s what I recommend:")
                    for _, row in recs.iterrows():
                        st.image(row["imgurl"], width=220)
                        st.markdown(f"**{row['name'].title()}**")
                        st.markdown(f"⏱️ {row['total_time_minutes']} minutes")
                        st.markdown(row["summary"])

                        explanation = explain_recommendation(
                            row,
                            st.session_state.preferences
                        )

                        st.markdown(f"🧠 *Why this?* {explanation}")
                        st.divider()


                    if st.button("🔁 Show More"):
                        st.session_state.preferences["offset"] += 5

                        # st.session_state.messages.append({
                        #     "role": "assistant",
                        #     "content": "I relaxed some constraints to find better matches."
                        # })
                        
                        st.rerun()

                        # if user_input:
                        #     st.session_state.relaxed_once = False


    # st.rerun()

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