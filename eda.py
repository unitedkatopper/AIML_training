import os
import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = "data/attempts.csv"
OUT_DIR = "results/eda"

score_cols = [
    "creativity", "originality", "problem_solving", "research_aptitude",
    "invention_thinking", "pattern_recognition", "risk_taking", "innovation_score"
]


def main():
    if not os.path.exists(DATA_FILE):
        print("No attempts.csv found. First collect user responses from the app.")
        return

    df = pd.read_csv(DATA_FILE)
    os.makedirs(OUT_DIR, exist_ok=True)

    if df.empty:
        print("Dataset is empty.")
        return

    # 1. Innovation score distribution
    plt.figure(figsize=(8, 5))
    plt.hist(df["innovation_score"], bins=10)
    plt.title("Innovation Score Distribution")
    plt.xlabel("Innovation Score")
    plt.ylabel("Number of Users")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/innovation_score_distribution.png")
    plt.close()

    # 2. Boxplot of all score columns
    available = [c for c in score_cols if c in df.columns]
    plt.figure(figsize=(10, 5))
    plt.boxplot([df[c] for c in available], labels=available)
    plt.title("Score Spread Across AM Dimensions")
    plt.ylabel("Score")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/score_boxplot.png")
    plt.close()

    # 3. Creativity vs Innovation score
    if "creativity" in df.columns:
        plt.figure(figsize=(7, 5))
        plt.scatter(df["creativity"], df["innovation_score"])
        plt.title("Creativity vs Innovation Score")
        plt.xlabel("Creativity")
        plt.ylabel("Innovation Score")
        plt.tight_layout()
        plt.savefig(f"{OUT_DIR}/creativity_vs_innovation.png")
        plt.close()

    # 4. Correlation heatmap using matplotlib only
    corr = df[available].corr()
    plt.figure(figsize=(8, 6))
    plt.imshow(corr, aspect="auto")
    plt.colorbar(label="Correlation")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=40, ha="right")
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title("Correlation Heatmap of AM Features")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/correlation_heatmap.png")
    plt.close()

    # summary table
    df[available].describe().to_csv(f"{OUT_DIR}/eda_summary.csv")

    print("EDA completed. Files saved in results/eda folder.")


if __name__ == "__main__":
    main()
