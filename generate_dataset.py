import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

def generate_dataset(num_records=1000):
    data = []
    for _ in range(num_records):
        age = random.randint(20, 55)
        retirement_age_goal = random.randint(55, 65)
        dependents = random.randint(0, 4)
        monthly_expenses = random.randint(3000, 14000)
        existing_savings = random.randint(0, 50000)
        min_wage = random.randint(300, 600)
        max_wage = random.randint(min_wage + 50, min_wage + 400)
        min_days = random.randint(10, 18)
        max_days = random.randint(min_days + 2, 26)
        worst_income = min_wage * min_days
        best_income = max_wage * max_days
        expected_income = int(((min_wage + max_wage) / 2) * ((min_days + max_days) / 2))
        years_to_retire = retirement_age_goal - age
        disposable_income = expected_income - monthly_expenses
        if disposable_income <= 0:
            savings_amount = 0
            savings_rate = 0.0
        else:
            savings_rate = round(random.uniform(0.10, 0.30), 2)
            savings_amount = round(disposable_income * savings_rate)
        monthly_rate = 0.06 / 12
        months = years_to_retire * 12
        if monthly_rate > 0 and months > 0 and savings_amount > 0:
            corpus = round(savings_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate))
        else:
            corpus = existing_savings
        if expected_income < 8000:
            investment_type = "Post Office RD"
        elif expected_income < 15000:
            investment_type = "PPF"
        else:
            investment_type = "NPS"
        data.append({
            "age": age, "dependents": dependents,
            "monthly_expenses": monthly_expenses, "existing_savings": existing_savings,
            "retirement_age_goal": retirement_age_goal, "years_to_retire": years_to_retire,
            "min_wage": min_wage, "max_wage": max_wage,
            "min_days": min_days, "max_days": max_days,
            "worst_income": worst_income, "best_income": best_income,
            "expected_income": expected_income,
            "recommended_savings_amount": savings_amount,
            "savings_rate": savings_rate, "retirement_corpus": corpus,
            "investment_type": investment_type,
        })
    df = pd.DataFrame(data)
    df.to_csv("dataset.csv", index=False)
    print(f"✅ Dataset created with {len(df)} records!")
    print(df.head())

generate_dataset()
