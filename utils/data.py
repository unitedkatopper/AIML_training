import os
import pandas as pd
from datetime import datetime

DATA_FILE = "data/attempts.csv"
ANSWER_FILE = "data/answers.csv"


def make_dirs():
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)


def save_attempt(row):
    make_dirs()
    df = pd.DataFrame([row])
    if os.path.exists(DATA_FILE):
        old = pd.read_csv(DATA_FILE)
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)


def save_answers(rows):
    make_dirs()
    df = pd.DataFrame(rows)
    if os.path.exists(ANSWER_FILE):
        old = pd.read_csv(ANSWER_FILE)
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(ANSWER_FILE, index=False)


def load_attempts():
    make_dirs()
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()


def get_user_history(name):
    df = load_attempts()
    if df.empty or "name" not in df.columns:
        return pd.DataFrame()
    return df[df["name"].astype(str).str.lower() == str(name).lower()].copy()


def new_attempt_id(name):
    safe = str(name).strip().lower().replace(" ", "_")
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{safe}_{now}"
