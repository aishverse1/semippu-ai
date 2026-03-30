import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
import pickle

df = pd.read_csv("dataset.csv")

FEATURES = [
    "age", "dependents", "monthly_expenses", "existing_savings",
    "years_to_retire", "min_wage", "max_wage", "min_days", "max_days",
    "worst_income", "best_income", "expected_income",
]
# Corpus formula = f(monthly_savings, age); recommended_savings_amount is key
FEATURES_CORPUS = FEATURES + ["recommended_savings_amount"]

X = df[FEATURES]
X_corpus = df[FEATURES_CORPUS]

y_savings = df["recommended_savings_amount"]
X_train, X_test, y_train, y_test = train_test_split(X, y_savings, test_size=0.2, random_state=42)
savings_model = RandomForestRegressor(n_estimators=200, max_depth=20, min_samples_leaf=5, random_state=42)
savings_model.fit(X_train, y_train)
print(f"✅ Savings Model trained! MAE: ₹{mean_absolute_error(y_test, savings_model.predict(X_test)):.2f}")

y_investment = df["investment_type"]
X_train2, X_test2, y_train2, y_test2 = train_test_split(X, y_investment, test_size=0.2, random_state=42)
investment_model = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42)
investment_model.fit(X_train2, y_train2)
print(f"✅ Investment Model trained! Accuracy: {accuracy_score(y_test2, investment_model.predict(X_test2)) * 100:.1f}%")

y_corpus = df["retirement_corpus"]
X_train3, X_test3, y_train3, y_test3 = train_test_split(X_corpus, y_corpus, test_size=0.2, random_state=42)
corpus_model = RandomForestRegressor(n_estimators=200, max_depth=20, min_samples_leaf=3, random_state=42)
corpus_model.fit(X_train3, y_train3)
print(f"✅ Corpus Model trained! MAE: ₹{mean_absolute_error(y_test3, corpus_model.predict(X_test3)):.2f}")

with open("savings_model.pkl", "wb") as f: pickle.dump(savings_model, f)
with open("investment_model.pkl", "wb") as f: pickle.dump(investment_model, f)
with open("corpus_model.pkl", "wb") as f: pickle.dump(corpus_model, f)
print("✅ All 3 models saved!")
