# This file creates some fake demo data so you can test train.py quickly.
# You can delete this file later. Real data will be better than this sample data.

import os
import random
import pandas as pd
from datetime import datetime, timedelta

os.makedirs("data", exist_ok=True)

names = ["Aman", "Riya", "Karan", "Meera", "Pratyush", "Arya", "Nikhil", "Sana", "Rahul", "Ishita", "Dev", "Ananya"]
profiles = ["Research Explorer", "Creative Inventor", "Practical Problem Solver", "Bold Experimenter", "Product Builder", "Growing Innovator"]
fields = ["AI Research", "Robotics", "Product Innovation", "Social Innovation", "Space / Future Tech"]

rows = []
for i in range(24):
    creativity = random.randint(45, 95)
    originality = random.randint(45, 95)
    problem = random.randint(40, 92)
    research = random.randint(40, 96)
    invention = random.randint(45, 94)
    pattern = random.randint(35, 100)
    risk = random.randint(35, 95)
    innovation = int(creativity*0.18 + originality*0.16 + problem*0.16 + research*0.17 + invention*0.16 + pattern*0.09 + risk*0.08)

    d = datetime.now() - timedelta(days=random.randint(0, 10))
    rows.append({
        "attempt_id": f"demo_{i}",
        "name": random.choice(names),
        "age": random.randint(18, 24),
        "background": "Student",
        "date": d.strftime("%Y-%m-%d %H:%M:%S"),
        "time_taken_sec": random.randint(300, 1200),
        "profile": random.choice(profiles),
        "recommended_fields": ", ".join(random.sample(fields, 3)),
        "ml_cluster": "Not trained yet",
        "creativity": creativity,
        "originality": originality,
        "problem_solving": problem,
        "research_aptitude": research,
        "invention_thinking": invention,
        "pattern_recognition": pattern,
        "risk_taking": risk,
        "innovation_score": innovation
    })

pd.DataFrame(rows).to_csv("data/attempts.csv", index=False)
print("Sample data created in data/attempts.csv")
