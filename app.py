import os
import time
from datetime import datetime

import streamlit as st
import pandas as pd
import joblib

from utils.questions import questions, sections
from utils.scoring import (
    score_text_answer, score_mcq, make_final_scores, get_profile,
    recommend_fields, strength_and_weakness, get_level
)
from utils.data import save_attempt, save_answers, get_user_history, new_attempt_id, load_attempts
from utils.reports import report_text, profile_explanation

st.set_page_config(page_title="AM - Antarman", page_icon="🧠", layout="wide")

# I used simple css only to make it readable, not too fancy.
st.markdown("""
<style>
.main-title {font-size: 42px; font-weight: 800; margin-bottom: 0px;}
.sub {font-size: 18px; color: #666; margin-top: 0px;}
.small-box {padding: 15px; border-radius: 12px; background: #f5f5f5; margin-bottom: 10px;}
.score-card {padding: 15px; border: 1px solid #ddd; border-radius: 12px; margin-bottom: 12px;}
</style>
""", unsafe_allow_html=True)


def reset_test():
    st.session_state.started = False
    st.session_state.start_time = None
    st.session_state.answers = {}


def load_ml_cluster(scores):
    # This only works after running train.py
    model_path = "models/cluster_model.pkl"
    scaler_path = "models/scaler.pkl"
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        return None

    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        cols = [
            "creativity", "originality", "problem_solving", "research_aptitude",
            "invention_thinking", "pattern_recognition", "risk_taking", "innovation_score"
        ]
        row = pd.DataFrame([[scores[c] for c in cols]], columns=cols)
        x = scaler.transform(row)
        c = int(model.predict(x)[0])
        names = {
            0: "Balanced Thinkers",
            1: "Creative Starters",
            2: "Analytical Builders",
            3: "Bold Innovators"
        }
        return names.get(c, f"Cluster {c}")
    except Exception:
        return None


if "started" not in st.session_state:
    st.session_state.started = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "answers" not in st.session_state:
    st.session_state.answers = {}

st.markdown('<p class="main-title">AM — Antarman</p>', unsafe_allow_html=True)
st.markdown('<p class="sub">Decoding the DNA of Innovation</p>', unsafe_allow_html=True)

menu = st.sidebar.radio("Menu", ["Take AM Test", "Previous Attempts", "EDA & Model Results", "About Project", "Admin Data"])

if menu == "Take AM Test":
    st.write("AM checks creativity, originality, problem solving, research aptitude, pattern recognition and risk taking.")

    with st.form("user_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Name", placeholder="Enter your name")
        with col2:
            age = st.number_input("Age", min_value=10, max_value=80, value=20)
        with col3:
            background = st.selectbox("Background", ["Student", "Teacher", "Developer", "Researcher", "Other"])

        start = st.form_submit_button("Start Assessment")

    if start:
        if name.strip() == "":
            st.warning("Please enter your name first.")
        else:
            st.session_state.started = True
            st.session_state.start_time = time.time()
            st.session_state.answers = {}
            st.session_state.name = name.strip()
            st.session_state.age = age
            st.session_state.background = background
            st.rerun()

    if st.session_state.started:
        st.divider()
        st.subheader("AM Assessment")
        st.info("Write naturally. Short answers reduce your score because AM needs enough thinking samples.")

        with st.form("test_form"):
            for sec in sections:
                st.markdown(f"### {sec}")
                sec_questions = [q for q in questions if q["section"] == sec]
                for q in sec_questions:
                    key = q["id"]
                    st.write(f"**{q['question']}**")
                    if q["type"] == "text":
                        st.session_state.answers[key] = st.text_area("Your answer", key=f"ans_{key}", height=90, label_visibility="collapsed")
                    else:
                        st.session_state.answers[key] = st.radio("Choose one", q["options"], key=f"ans_{key}", horizontal=True, label_visibility="collapsed")
                    st.write("")

            submit = st.form_submit_button("Generate AM Report")

        if submit:
            total_time = int(time.time() - st.session_state.start_time)
            attempt_id = new_attempt_id(st.session_state.name)
            answer_rows = []
            all_text = ""

            for q in questions:
                ans = st.session_state.answers.get(q["id"], "")
                if q["type"] == "text":
                    sc = score_text_answer(ans, q["section"])
                    all_text += " " + str(ans)
                else:
                    sc = score_mcq(ans, q["answer"])

                answer_rows.append({
                    "attempt_id": attempt_id,
                    "name": st.session_state.name,
                    "question_id": q["id"],
                    "section": q["section"],
                    "question": q["question"],
                    "answer": ans,
                    "score": sc,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            scores = make_final_scores(answer_rows)
            profile = get_profile(scores)
            fields = recommend_fields(scores, all_text)

            # Growth check from old attempts
            history = get_user_history(st.session_state.name)
            growth = None
            if not history.empty and "innovation_score" in history.columns:
                try:
                    last_score = int(history.iloc[-1]["innovation_score"])
                    growth = scores["innovation_score"] - last_score
                except Exception:
                    growth = None

            cluster_name = load_ml_cluster(scores)

            row = {
                "attempt_id": attempt_id,
                "name": st.session_state.name,
                "age": st.session_state.age,
                "background": st.session_state.background,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "time_taken_sec": total_time,
                "profile": profile,
                "recommended_fields": ", ".join(fields),
                "ml_cluster": cluster_name if cluster_name else "Not trained yet",
                **scores
            }
            save_attempt(row)
            save_answers(answer_rows)

            st.success("AM Report Generated")

            c1, c2, c3 = st.columns(3)
            c1.metric("Innovation Score", scores["innovation_score"])
            c2.metric("AM Profile", profile)
            c3.metric("Level", get_level(scores["innovation_score"]))

            if growth is not None:
                st.metric("Growth from last attempt", growth)

            st.write(profile_explanation(profile))

            st.subheader("Innovation DNA")
            score_df = pd.DataFrame({
                "Area": ["Creativity", "Originality", "Problem Solving", "Research", "Invention", "Pattern", "Risk"],
                "Score": [
                    scores["creativity"], scores["originality"], scores["problem_solving"],
                    scores["research_aptitude"], scores["invention_thinking"],
                    scores["pattern_recognition"], scores["risk_taking"]
                ]
            })
            st.bar_chart(score_df.set_index("Area"))

            strength, weakness = strength_and_weakness(scores)
            colA, colB = st.columns(2)
            with colA:
                st.markdown("#### Strength")
                st.write(strength.capitalize())
            with colB:
                st.markdown("#### Needs Practice")
                st.write(weakness.capitalize())

            st.markdown("#### Recommended Fields")
            st.write(", ".join(fields))

            if cluster_name:
                st.info(f"ML Cluster after training: {cluster_name}")
            else:
                st.warning("ML cluster is not available yet. Collect some attempts and run python train.py")

            txt = report_text(st.session_state.name, scores, profile, fields, growth, cluster_name)
            st.download_button("Download Report as TXT", txt, file_name=f"AM_Report_{st.session_state.name}.txt")

            with st.expander("Show detailed answer scores"):
                st.dataframe(pd.DataFrame(answer_rows)[["section", "question_id", "score", "answer"]])

            if st.button("Take Again"):
                reset_test()
                st.rerun()

elif menu == "Previous Attempts":
    st.subheader("Previous Attempts")
    name_search = st.text_input("Enter name to check growth")
    if name_search:
        hist = get_user_history(name_search)
        if hist.empty:
            st.warning("No previous attempt found for this name.")
        else:
            st.dataframe(hist)
            if len(hist) > 1:
                chart = hist[["date", "innovation_score"]].copy()
                chart["date"] = chart["date"].astype(str)
                st.line_chart(chart.set_index("date"))

elif menu == "EDA & Model Results":
    st.subheader("EDA and Model Results")
    st.write("This section is added to match the internship ML lifecycle: EDA, model evaluation and comparison.")

    metrics_path = "results/model_metrics.csv"
    if os.path.exists(metrics_path):
        st.markdown("### Model Evaluation Metrics")
        st.dataframe(pd.read_csv(metrics_path))
    else:
        st.info("Run `python train.py` to generate model evaluation metrics.")

    eda_folder = "results/eda"
    image_files = [
        "innovation_score_distribution.png",
        "score_boxplot.png",
        "creativity_vs_innovation.png",
        "correlation_heatmap.png"
    ]
    st.markdown("### EDA Graphs")
    shown = False
    for img in image_files:
        img_path = os.path.join(eda_folder, img)
        if os.path.exists(img_path):
            st.image(img_path, caption=img.replace("_", " ").replace(".png", "").title())
            shown = True
    if not shown:
        st.info("Run `python eda.py` to generate EDA graphs.")

elif menu == "About Project":
    st.subheader("About AM — Antarman")
    st.write("AM stands for Antarman, the inner mind. The project tries to find the hidden innovation pattern of a person.")
    st.write("It is not based on any online AI. It uses questions, scoring rules, stored data and trainable ML models.")
    st.markdown("""
    **Main modules:**
    - Assessment questions
    - Feature based scoring
    - Innovation DNA report
    - Growth tracking
    - ML training using collected data
    - User clustering
    """)
    st.markdown("""
    **Why this name?**  
    Antarman means the inner mind. Innovation first appears inside a person's thinking before it becomes a product, research or invention.
    """)

elif menu == "Admin Data":
    st.subheader("Admin Data")
    df = load_attempts()
    if df.empty:
        st.info("No data collected yet.")
    else:
        st.write("Collected attempts:", len(df))
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download attempts CSV", csv, "attempts.csv")
