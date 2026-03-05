import pickle

# Load models
with open("savings_model.pkl", "rb") as f:
    savings_model = pickle.load(f)
with open("scheme_model.pkl", "rb") as f:
    scheme_model = pickle.load(f)
with open("corpus_model.pkl", "rb") as f:
    corpus_model = pickle.load(f)

# User profile (one time setup)
user = {
    "age": 30,
    "dependents": 2,
    "monthly_expenses": 5000,
    "existing_savings": 5000,
    "years_to_retire": 30,
    "min_wage": 300,
    "max_wage": 700,
    "min_days": 12,
    "max_days": 24,
}

# Calculate income scenarios
user["worst_income"]    = user["min_wage"] * user["min_days"]
user["best_income"]     = user["max_wage"] * user["max_days"]
user["expected_income"] = int(
    ((user["min_wage"] + user["max_wage"]) / 2) *
    ((user["min_days"] + user["max_days"]) / 2)
)

features = [[
    user["age"], user["dependents"], user["monthly_expenses"],
    user["existing_savings"], user["years_to_retire"],
    user["min_wage"], user["max_wage"],
    user["min_days"], user["max_days"],
    user["worst_income"], user["best_income"], user["expected_income"],
]]

monthly_savings = round(savings_model.predict(features)[0])
best_scheme     = scheme_model.predict(features)[0]
corpus          = round(corpus_model.predict(features)[0])
daily_savings   = round(monthly_savings / user["min_days"])

print("\n📊 Your Retirement Savings Plan")
print("─────────────────────────────────────")
print(f"Income Range:         ₹{user['worst_income']} - ₹{user['best_income']}/month")
print(f"Expected Income:      ₹{user['expected_income']}/month")
print(f"💰 Save Per Month:    ₹{monthly_savings}")
print(f"💰 Save Per Day:      ₹{daily_savings} (on working days)")
print(f"📈 Best Scheme:       {best_scheme}")
print(f"🏦 Retirement Corpus: ₹{corpus:,}")
print(f"⏳ Years to Retire:   {user['years_to_retire']} years")
print("─────────────────────────────────────")

if user["worst_income"] < user["monthly_expenses"]:
    print("⚠️  Warning: Bad months may not cover expenses!")
    print("   Build ₹5,000 emergency fund first.")
elif monthly_savings < 500:
    print("🟡 Savings are low. Try to reduce expenses.")
else:
    print("✅ You're on a good track!")