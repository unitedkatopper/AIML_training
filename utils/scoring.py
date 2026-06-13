import re
import math

# simple word groups. Not perfect, but useful for a first version.
bold_words = [
    "new", "unique", "risk", "experiment", "prototype", "test", "future",
    "change", "different", "creative", "smart", "automatic", "sensor", "ai",
    "data", "research", "low cost", "community", "model", "system"
]

practical_words = [
    "cost", "cheap", "low", "available", "simple", "step", "test", "implement",
    "prototype", "user", "time", "budget", "material", "maintain", "safe"
]

research_words = [
    "why", "how", "data", "survey", "observe", "measure", "compare", "cause",
    "effect", "pattern", "problem", "question", "study", "experiment", "feedback"
]

risk_words = [
    "try", "risk", "unique", "difficult", "fail", "learn", "prototype", "prove",
    "test", "improve", "original", "challenge", "attempt"
]

field_words = {
    "AI Research": ["ai", "data", "model", "algorithm", "pattern", "prediction", "automation"],
    "Robotics": ["sensor", "device", "machine", "automatic", "hardware", "robot", "movement"],
    "Product Innovation": ["user", "design", "prototype", "feature", "product", "app", "useful"],
    "Social Innovation": ["village", "student", "people", "community", "public", "college", "farmer"],
    "Space / Future Tech": ["future", "astronaut", "space", "energy", "advanced", "satellite"]
}


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def word_list(text):
    text = clean_text(text)
    if text == "":
        return []
    return text.split()


def count_ideas(text):
    # a rough idea counter. Students often separate ideas by comma, number, next line etc.
    original = str(text)
    parts = re.split(r"\n|,|;|\.|\d\)|\d\.", original)
    parts = [p.strip() for p in parts if len(p.strip().split()) >= 2]
    return max(1, len(parts)) if len(word_list(text)) > 0 else 0


def keyword_count(text, words):
    t = clean_text(text)
    total = 0
    for w in words:
        if w in t:
            total += 1
    return total


def basic_text_features(text):
    words = word_list(text)
    unique = set(words)
    wc = len(words)
    unique_ratio = len(unique) / wc if wc else 0
    ideas = count_ideas(text)
    long_words = len([w for w in words if len(w) >= 7])

    return {
        "word_count": wc,
        "unique_words": len(unique),
        "unique_ratio": round(unique_ratio, 3),
        "idea_count": ideas,
        "long_words": long_words,
        "bold_hits": keyword_count(text, bold_words),
        "practical_hits": keyword_count(text, practical_words),
        "research_hits": keyword_count(text, research_words),
        "risk_hits": keyword_count(text, risk_words),
    }


def limit_score(x):
    try:
        x = float(x)
    except Exception:
        x = 0
    return int(max(0, min(100, round(x))))


def score_text_answer(text, section):
    f = basic_text_features(text)
    wc = f["word_count"]
    ideas = f["idea_count"]

    # length should help, but not too much. Otherwise people can write nonsense long answers.
    length_score = min(35, wc * 1.2)
    variety_score = min(20, f["unique_ratio"] * 30)
    idea_score = min(25, ideas * 5)
    bold_score = min(15, f["bold_hits"] * 3)
    practical_score = min(20, f["practical_hits"] * 4)
    research_score = min(20, f["research_hits"] * 4)
    risk_score = min(20, f["risk_hits"] * 4)

    if section == "Creativity":
        score = length_score + variety_score + idea_score + bold_score
    elif section == "Problem Solving":
        score = length_score + practical_score + min(20, ideas * 4) + min(15, f["long_words"] * 1.5)
    elif section == "Research Aptitude":
        score = length_score + research_score + min(20, ideas * 4) + variety_score / 2
    elif section == "Invention Challenge":
        score = length_score + idea_score + practical_score + bold_score / 2
    elif section == "Risk Taking":
        score = length_score + risk_score + min(20, ideas * 4) + variety_score / 2
    else:
        score = length_score + variety_score

    return limit_score(score)


def score_mcq(selected, correct):
    return 100 if selected == correct else 0


def make_final_scores(answer_rows):
    # answer_rows is list of dicts having section and score
    scores = {
        "Creativity": [],
        "Problem Solving": [],
        "Research Aptitude": [],
        "Invention Challenge": [],
        "Pattern Recognition": [],
        "Risk Taking": []
    }

    for row in answer_rows:
        sec = row.get("section")
        if sec in scores:
            scores[sec].append(float(row.get("score", 0)))

    avg = {}
    for sec, vals in scores.items():
        avg[sec] = round(sum(vals) / len(vals), 2) if vals else 0

    creativity = avg["Creativity"]
    originality = round((avg["Creativity"] * 0.55 + avg["Invention Challenge"] * 0.45), 2)
    problem = avg["Problem Solving"]
    research = avg["Research Aptitude"]
    invention = avg["Invention Challenge"]
    pattern = avg["Pattern Recognition"]
    risk = avg["Risk Taking"]

    innovation = (
        creativity * 0.18 + originality * 0.16 + problem * 0.16 + research * 0.17 +
        invention * 0.16 + pattern * 0.09 + risk * 0.08
    )

    return {
        "creativity": limit_score(creativity),
        "originality": limit_score(originality),
        "problem_solving": limit_score(problem),
        "research_aptitude": limit_score(research),
        "invention_thinking": limit_score(invention),
        "pattern_recognition": limit_score(pattern),
        "risk_taking": limit_score(risk),
        "innovation_score": limit_score(innovation)
    }


def get_profile(scores):
    c = scores["creativity"]
    r = scores["research_aptitude"]
    p = scores["problem_solving"]
    i = scores["invention_thinking"]
    risk = scores["risk_taking"]
    pat = scores["pattern_recognition"]

    if r >= 75 and pat >= 65:
        return "Research Explorer"
    if c >= 75 and i >= 70:
        return "Creative Inventor"
    if p >= 75 and pat >= 70:
        return "Practical Problem Solver"
    if risk >= 75 and c >= 65:
        return "Bold Experimenter"
    if i >= 70 and p >= 65:
        return "Product Builder"
    return "Growing Innovator"


def get_level(score):
    if score >= 85:
        return "Exceptional"
    if score >= 70:
        return "Strong"
    if score >= 55:
        return "Developing"
    return "Needs Practice"


def strength_and_weakness(scores):
    keys = ["creativity", "originality", "problem_solving", "research_aptitude", "invention_thinking", "pattern_recognition", "risk_taking"]
    best = max(keys, key=lambda x: scores[x])
    weak = min(keys, key=lambda x: scores[x])

    names = {
        "creativity": "generating fresh ideas",
        "originality": "thinking differently from common answers",
        "problem_solving": "turning problems into practical steps",
        "research_aptitude": "asking deeper questions before solving",
        "invention_thinking": "building product-like solutions",
        "pattern_recognition": "finding hidden patterns",
        "risk_taking": "choosing bold and original attempts"
    }
    return names[best], names[weak]


def recommend_fields(scores, all_answers_text):
    text = clean_text(all_answers_text)
    field_score = {}
    for field, words in field_words.items():
        field_score[field] = keyword_count(text, words)

    # score based recommendation also
    if scores["research_aptitude"] > 70:
        field_score["AI Research"] += 2
    if scores["invention_thinking"] > 70:
        field_score["Product Innovation"] += 2
    if scores["problem_solving"] > 70:
        field_score["Social Innovation"] += 1
    if scores["creativity"] > 75:
        field_score["Product Innovation"] += 1
    if scores["pattern_recognition"] > 75:
        field_score["AI Research"] += 1

    ranked = sorted(field_score.items(), key=lambda x: x[1], reverse=True)
    return [x[0] for x in ranked[:3]]


def next_challenge(weak_area):
    tasks = {
        "generating fresh ideas": "Try the '20 uses of one object' exercise every day for 5 minutes.",
        "thinking differently from common answers": "For every solution, force yourself to write one strange alternative also.",
        "turning problems into practical steps": "Take one idea and write materials, cost, users and testing plan.",
        "asking deeper questions before solving": "Before solving any problem, write 5 why/how questions first.",
        "building product-like solutions": "Convert one idea into features, users and prototype sketch.",
        "finding hidden patterns": "Practice number series, analogies and pattern puzzles daily.",
        "choosing bold and original attempts": "Pick one uncommon idea and make a small demo instead of only explaining it."
    }
    return tasks.get(weak_area, "Practice one small innovation challenge every day.")
