# AM — Antarman
## Decoding the DNA of Innovation

AM is a Streamlit based Machine Learning project that evaluates innovative thinking using structured questions, scoring rules and trainable ML models.

## Main Features
- Creativity, originality, problem solving, research aptitude, invention thinking, pattern recognition and risk-taking assessment
- Rule-based scoring engine for initial labels
- User generated dataset stored in CSV format
- Random Forest Regressor for innovation score prediction
- Random Forest Classifier for Low / Medium / High level prediction
- KMeans Clustering for thinking pattern grouping
- EDA graph generation
- Model evaluation metrics generation
- Streamlit deployment ready

## Project Structure
```text
AM/
├── Dataset/              # Submission folder note for dataset
├── Notebook/             # Placeholder for notebook if required
├── Model/                # Submission folder note for model files
├── Streamlit_App/        # Note about Streamlit app
├── Documentation/        # Report notes
├── data/                 # attempts.csv, answers.csv, clustered data
├── models/               # trained .pkl files
├── results/              # EDA graphs and model metrics
├── utils/                # project logic files
├── app.py                # main Streamlit app
├── train.py              # model training and evaluation
├── eda.py                # EDA graph generation
├── sample_data.py        # dummy/demo data generator
└── requirements.txt
```

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## How to Generate EDA
```bash
python eda.py
```

EDA outputs are saved in:
```text
results/eda/
```

## How to Train Models
```bash
python train.py
```

Trained models are saved in:
```text
models/
```

Evaluation metrics are saved in:
```text
results/model_metrics.csv
```

## When to Use sample_data.py
Use it only when there is no real user data and you need demo data quickly.

```bash
python sample_data.py
python train.py
python eda.py
```

For real training, collect responses from users using the Streamlit app and then run only:

```bash
python train.py
python eda.py
```

## Important Note
AM is not a ChatGPT/OpenAI/Gemini wrapper. It uses a scoring engine and machine learning models trained on collected user assessment data.
