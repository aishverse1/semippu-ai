from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

try:
    with open("savings_model.pkl", "rb") as f:
        savings_model = pickle.load(f)
    with open("investment_model.pkl", "rb") as f:
        scheme_model = pickle.load(f)
    with open("corpus_model.pkl", "rb") as f:
        corpus_model = pickle.load(f)
    print("✅ All 3 models loaded successfully")
except Exception as e:
    print("❌ Error loading models:", e)

def calculate_corpus(monthly_savings: float, current_age: int) -> int:
    """
    Corpus = FV of monthly savings at 5% until age 50 only.
    No existing_savings or previous corpus — generate new from current data only.
    - 0 contributions → use predicted monthly_savings.
    - 1 contribution (e.g. 500) → avg = 500, corpus from that.
    - 2+ contributions → avg = total / number of contributions, corpus from that.
    """
    if current_age >= 50 or monthly_savings <= 0:
        return 0
    years_to_50 = 50 - current_age
    months = years_to_50 * 12
    r = 0.05 / 12  # monthly rate 5% annual
    # FV of monthly annuity: PMT * (((1 + r)^n - 1) / r)
    fv = monthly_savings * (((1 + r) ** months - 1) / r)
    return round(fv)


class UserProfile(BaseModel):
    """
    More forgiving profile schema so frontend requests never fail with 422.

    All numeric fields have safe defaults. If the frontend forgets to send a
    field, FastAPI will use these defaults instead of rejecting the request.
    """
    user_id: str
    age: int = 0
    dependents: int = 0
    monthly_expenses: float = 0.0
    existing_savings: float = 0.0
    retirement_age: int = 60
    min_wage: float = 0.0
    max_wage: float = 0.0
    min_days: int = 0
    max_days: int = 0
    avg_monthly_savings: float = 0.0  # Total contributions / months since signup (from frontend)
    total_contributed: float = 0.0     # Sum of all contributions (optional, for reference)

@app.get("/health")
def health():
    return {"status": "Semippu AI API running ✅"}

@app.get("/")
def home():
    return {"message": "Semippu AI API running ✅"}

@app.post("/predict")
def predict(user: UserProfile):
    # Basic guard: if critical fields are missing/zero, return a clear message
    if user.age <= 0 or user.retirement_age <= 0 or user.min_wage <= 0 or user.max_wage <= 0 or user.min_days <= 0 or user.max_days <= 0:
        return {
            "user_id": user.user_id,
            "warning": "Please complete your income and working days profile to get an AI plan.",
            "monthly_savings": 0,
            "daily_savings": 0,
            "best_scheme": "N/A",
            "retirement_corpus": 0,
            "pension_per_month": 0,
            "worst_income": 0,
            "best_income": 0,
            "expected_income": 0,
            "years_to_retire": max(user.retirement_age - user.age, 0),
            "created_at": datetime.now().isoformat(),
        }

    worst_income = user.min_wage * user.min_days
    best_income = user.max_wage * user.max_days
    expected_income = int(
        ((user.min_wage + user.max_wage) / 2) *
        ((user.min_days + user.max_days) / 2)
    )
    years_to_retire = user.retirement_age - user.age
    features = [[
        user.age, user.dependents, user.monthly_expenses,
        user.existing_savings, years_to_retire,
        user.min_wage, user.max_wage, user.min_days, user.max_days,
        worst_income, best_income, expected_income
    ]]
    monthly_savings = round(savings_model.predict(features)[0])
    best_scheme = scheme_model.predict(features)[0]
    # 0 contributions → use predicted monthly_savings; 1+ contributions → use avg (total / number of contributions)
    effective_monthly_savings = user.avg_monthly_savings if user.avg_monthly_savings > 0 else monthly_savings
    corpus = calculate_corpus(float(effective_monthly_savings), user.age)
    daily_savings = round(monthly_savings / user.min_days) if user.min_days > 0 else 0
    if worst_income < user.monthly_expenses:
        warning = "⚠️ Bad months may not cover expenses! Build ₹5,000 emergency fund first."
    elif monthly_savings < 500:
        warning = "🟡 Savings are low. Try to reduce expenses."
    else:
        warning = "✅ You're on a good track!"
    # Pension per month = (retirement_corpus * 0.06) / 12 (6% annual drawdown, monthly)
    pension_per_month = round((corpus * 0.06) / 12) if corpus else 0

    plan = {
        "user_id": user.user_id,
        "worst_income": worst_income,
        "best_income": best_income,
        "expected_income": expected_income,
        "monthly_savings": monthly_savings,
        "daily_savings": daily_savings,
        "best_scheme": best_scheme,
        "retirement_corpus": corpus,
        "pension_per_month": pension_per_month,
        "years_to_retire": years_to_retire,
        "warning": warning,
        "created_at": datetime.now().isoformat()
    }
    db.collection("savings_plans").document(user.user_id).collection("plans").document().set(plan)
    return plan

@app.get("/get-plan/{user_id}")
def get_plan(user_id: str):
    plans = db.collection("savings_plans").document(user_id).collection("plans").order_by("created_at", direction=firestore.Query.DESCENDING).limit(1).stream()
    for plan in plans:
        return plan.to_dict()
    return {"error": "No plan found for this user"}

@app.post("/save-profile")
def save_profile(user: UserProfile):
    profile = user.dict()
    profile["created_at"] = datetime.now().isoformat()
    db.collection("users").document(user.user_id).set(profile)
    return {"message": "Profile saved ✅"}
