# Semippu AI — Retirement Savings Prediction Engine

The AI backend for Semippu — a retirement planning platform for daily wage workers in India. Uses machine learning to predict personalized savings amounts, recommend government schemes, and calculate retirement corpus based on irregular income patterns.

---

## What It Does

- Predicts daily and monthly savings targets based on income range
- Recommends best government scheme (APY, PPF, NPS, Post Office RD)
- Calculates retirement corpus using compound interest at 5% until age 50
- Handles irregular income using variance-based modeling
- Saves plans to Firebase Firestore

---

## How It Works
```
User provides:
  → Min/max daily wage
  → Min/max working days per month
  → Age, dependents, expenses

AI calculates:
  → Worst/best/expected monthly income
  → Suggested daily and monthly savings
  → Best government scheme
  → Retirement corpus at 5% compound interest

Corpus formula:
  → If no contributions: use AI predicted monthly savings
  → If contributions exist: use average of actual contributions
  → Corpus = avg_monthly_savings × compound interest until age 50
```

---

## Tech Stack

- Python 3.10
- FastAPI
- Scikit-learn (Random Forest)
- Firebase Admin SDK
- Uvicorn
- Pydantic
- Docker

---

## Models

| Model | Type | Purpose |
|---|---|---|
| savings_model.pkl | Random Forest Regressor | Predict monthly savings |
| investment_model.pkl | Random Forest Classifier | Recommend best scheme |
| corpus_model.pkl | Random Forest Regressor | Predict retirement corpus |

---

## Project Structure
```
retirement-ai/
├── main.py              ← FastAPI app + endpoints
├── generate_dataset.py  ← Synthetic dataset generation
├── train_model.py       ← Model training
├── predict.py           ← Test predictions
├── requirements.txt     ← Python dependencies
├── Dockerfile           ← Docker config for deployment
├── savings_model.pkl    ← Trained savings model
├── investment_model.pkl ← Trained scheme model
└── corpus_model.pkl     ← Trained corpus model
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Health check |
| POST | /predict | Get AI savings plan |
| GET | /get-plan/{user_id} | Get saved plan |
| POST | /save-profile | Save user profile |

### POST /predict

Request:
```json
{
  "user_id": "user@example.com",
  "age": 30,
  "dependents": 2,
  "monthly_expenses": 7000,
  "existing_savings": 5000,
  "retirement_age": 60,
  "min_wage": 300,
  "max_wage": 700,
  "min_days": 12,
  "max_days": 24,
  "avg_monthly_savings": 500,
  "total_contributed": 3000
}
```

Response:
```json
{
  "monthly_savings": 450,
  "daily_savings": 37,
  "best_scheme": "Atal Pension Yojana (APY)",
  "retirement_corpus": 320000,
  "worst_income": 3600,
  "best_income": 16800,
  "expected_income": 9000,
  "years_to_retire": 20,
  "warning": "✅ You're on a good track!"
}
```

---

## Getting Started

### Installation
```bash
git clone https://github.com/aishverse1/semippu-ai.git
cd semippu-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Train Models
```bash
python3 generate_dataset.py
python3 train_model.py
```

### Run Locally
```bash
uvicorn main:app --reload
```

API runs at `http://127.0.0.1:8000`

### API Docs
```
http://127.0.0.1:8000/docs
```

---

## Deployment

Deployed on **Hugging Face Spaces** using Docker.

Live at: `https://aishverse1-semippu-ai.hf.space`

---

## Novelty

- Only AI model targeting daily wage workers specifically
- Handles irregular income using variance-based modeling
- Suggests only government-backed low-risk schemes
- Corpus calculated from actual contribution history
- Adapts savings suggestion based on good vs bad income days

---

## Team

Built for Zenith Hackathon 2025
