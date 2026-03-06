# Semippu + Retirement AI — Feature List & Pitch Note

## Complete feature list

### Retirement-AI (Backend — FastAPI, port 8000)

| Feature | Description |
|--------|-------------|
| **Health / Home** | `/health`, `/` — API status check |
| **Predict** | `POST /predict` — AI plan from user profile + contributions |
| **Get plan** | `GET /get-plan/{user_id}` — Latest saved plan for user |
| **Save profile** | `POST /save-profile` — Persist user profile to Firestore |
| **ML models** | 3 models: savings (RandomForest regressor), investment scheme (classifier), corpus (regressor; used only for fallback / training) |
| **Corpus formula** | Fresh corpus = FV of monthly savings at 5% until age 50. No contributions → use predicted monthly savings; with contributions → use avg (total / number of contributions). No adding to old corpus or existing savings. |
| **Pension per month** | `(retirement_corpus × 0.06) / 12` in response |
| **Warnings** | Expense vs income check; low-savings nudge; “on track” message |
| **Firestore** | Saves plans under `savings_plans/{user_id}/plans`, profiles under `users/{user_id}` |

---

### Semippu (Frontend — React + Express, port 3000)

#### Auth & onboarding
- **Language first** | Choose English or Tamil before login.
- **Login** | Phone number + password; JWT (7d).
- **Register** | OTP to phone → verify OTP → set password → optional “Login as Admin”.
- **Onboarding (7 steps)** | Age, dependents, monthly expenses, existing savings, years to retire (slider), min/max daily wage, min/max working days. Stored in context + localStorage.

#### Dashboard
- **Stats** | Total invested, inflation rate %, adjusted returns (total + inflation).
- **Recent contributions** | Last 5 entries (amount, type, date).
- **Loan summary** | If user has a loan: status (Pending/Approved/Rejected), amount, link to Loans.
- **Calculation logic** | Base investment, inflation impact, adjusted total.
- **Grow pension** | CTA to Invest.
- **Awareness** | Loan-scam tips (OTP, fees, verification).

#### Invest
- **New contribution** | Amount + type (Daily / Monthly); confirm; success toast.
- **Contribution history** | List of all contributions (amount, type, date).
- **Avg from contributions** | `totalInvested / contributions.length` sent to AI as avg monthly savings.

#### Loans
- **Eligibility** | Up to 90% of total invested; shown as amount.
- **Apply** | Enter amount; validation vs 90% limit; submit → Pending.
- **EMI preview** | 8% p.a., 24 months; EMI, total payable, total interest.
- **My application** | Status (Pending / Approved / Rejected), amount.

#### AI (Personalized insights)
- **Profile summary** | Age, dependents, expenses, savings, wage range, working days, years to retire, total invested.
- **Save per day** | AI recommended daily savings (₹).
- **Save per month** | AI recommended monthly savings (₹).
- **Retirement outlook** | “In X years you’ll have ₹Y” + horizon message.
- **Pension per month** | `(corpus × 0.06) / 12` — estimated monthly pension.
- **Best scheme** | Recommended type (e.g. Post Office RD, PPF, NPS).
- **Retirement corpus** | Estimated corpus; Refresh plan button.
- **Warning banner** | Expense/income, low savings, or on-track message.

#### Policies
- **Government schemes** | 5 cards: Pension for daily wage labourers, Women financial support, Senior citizen pension, Farmer subsidy, Low income family welfare. Each: name, description, eligibility, benefit.

#### Settings
- **Appearance** | Light / Dark theme.
- **Language** | English / Tamil (with i18n).

#### Admin (admin only)
- **Settings** | Global inflation rate; save.
- **Loan requests** | List all loans; Approve / Reject; total outstanding.
- **Data management** | Export state (contributions, loans, inflation) as JSON; Import JSON (replace contributions, loans, inflation).
- **All contributions** | Table: edit amount/type, delete.
- **Users** | Tab present (user management UI as needed).

#### UX & tech
- **Navbar** | Dashboard, Invest, Loans, Policies, AI, Settings, Admin (if admin); user name + Member/Admin; logout. Mobile hamburger menu.
- **Protected routes** | Language → Auth → app; redirect to language or auth when missing.
- **Theme** | Light/dark with persistence.
- **i18n** | English + Tamil for all main UI strings.

---

### Semippu server (Express, port 3000)

- **Auth** | `POST /api/auth/register-otp`, `POST /api/auth/register-verify`, `POST /api/auth/login` (SQLite, bcrypt, JWT).
- **AI proxy** | `POST /api/ai/predict` → FastAPI `/predict`; `GET /api/ai/plan/:userId` → FastAPI `/get-plan/:user_id`.
- **Static / SPA** | Vite in dev; serves `dist` in production.

---

## Pros of AI in this product

1. **Personalized numbers** — Save-per-day and save-per-month from income, expenses, dependents, and working days (no one-size-fits-all).
2. **Scheme recommendation** — Suggests Post Office RD / PPF / NPS by profile so users get a concrete next step.
3. **Retirement corpus** — Formula-based projection (5% until 50) so users see a clear goal; when they log contributions, corpus updates from their real average (no double-counting, fresh each time).
4. **Pension estimate** — Simple 6% drawdown → monthly pension amount so retirement feels tangible.
5. **Guarded defaults** — If profile is incomplete, API returns safe zeros and a clear “complete profile” message instead of wrong numbers.
6. **Warnings** — Flags bad months (income < expenses), low savings, and “on track,” so behaviour is nudged without being overwhelming.

---

## Cons / limitations

1. **No real OTP** — Registration uses simulated OTP (no SMS gateway); fine for demo, not for production.
2. **Auth split** — Frontend uses phone/password + localStorage; AI backend uses `user_id` (e.g. email) and Firestore. Semippu currently uses phone as identity; linking to AI’s user_id needs a single source of truth.
3. **Loans are in-memory** — Loans live in context + localStorage only; no backend persistence or real disbursement.
4. **Inflation is global** — One rate in Admin; not per-user or time-varying.
5. **Corpus formula is fixed** — 5% until 50 only; no user-chosen rate or retirement age in the formula.
6. **ML corpus model unused** — Corpus is formula-based; the trained corpus model is loaded but not used in `/predict`.
7. **Contributions not in backend** — Contributions are frontend-only; if user clears storage, history is lost unless exported/imported.
8. **Admin “Users”** — Tab exists; actual user list/management may be placeholder.

---

## Short pitch note

**Semippu** is a pension and savings app for informal workers (daily wage, variable income). Users set a profile once (age, dependents, expenses, wage range, working days), then log contributions (daily or monthly). The **Retirement AI** backend gives:

- **How much to save** — Per day and per month, tailored to their situation.  
- **How much they’ll have** — Retirement corpus from a simple, transparent rule: average monthly savings (or AI recommendation if no contributions yet), grown at 5% until age 50, with no mixing of old corpus or existing savings.  
- **What they’ll get as pension** — Monthly pension = 6% of that corpus per year, shown as ₹/month.  
- **Which scheme fits** — Post Office RD / PPF / NPS style recommendation.

The app also offers **loans** (up to 90% of invested amount, with EMI preview), **government scheme info**, **dark/light theme**, and **Tamil + English**. Admins can set inflation, approve/reject loans, and export/import data.  

**In one line:** Semippu uses AI to tell informal workers how much to save, how much they’ll have by 50, and what monthly pension that could mean — and updates the plan as they log real contributions.
