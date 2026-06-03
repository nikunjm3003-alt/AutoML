# ⚡ AutoML Studio

> Upload a CSV. Pick a target. Get a trained model — no code required.

🔗 **Live Demo:** https://automl-uvw7ktj7tuxeq7dk7ahappk.streamlit.app/

---

## 🔍 What is AutoML Studio?

AutoML Studio is a no-code machine learning web app that automatically detects your problem type (classification or regression), preprocesses your data, trains multiple models, compares their performance, and lets you make live predictions — all through a clean browser interface.

---

## ✨ Features

- 🔐 **User Auth** — Register & login with bcrypt-hashed passwords and email verification
- 📧 **Email Verification** — Real email validation via Abstract API + Gmail SMTP verification flow
- 🧹 **Auto Preprocessing** — Handles nulls, encodes categoricals, drops ID/high-cardinality columns
- 🤖 **Auto Problem Detection** — Classifies your task as classification or regression automatically
- 📊 **Model Comparison** — Trains 4 models with both Train/Test Split and 5-Fold CV metrics
- 🏆 **Best Model Selection** — Picks the best model by KFold AUC (classification) or KFold R² (regression)
- 🔮 **Live Predictions** — Interactive input form to predict on new data instantly
- 📈 **Dashboard** — Dataset overview, feature distributions, correlation heatmap, and model results

---

## 🧠 Models Trained

| Task | Models |
|------|--------|
| Classification | Logistic Regression, Decision Tree, Random Forest, XGBoost |
| Regression | Linear Regression, Decision Tree, Random Forest, XGBoost |

All classification pipelines include **SMOTE** for class imbalance handling.

---

## 📁 Project Structure

```
AUTOML/
├── app.py                  # Main entry point (auth + training)
├── pages/
│   ├── 1_dashboard.py      # Dataset overview & model comparison
│   └── 2_predictions.py    # Live prediction interface
├── utils/
│   ├── preprocessor.py     # Data cleaning & encoding
│   ├── detector.py         # Problem type detection
│   ├── trainer.py          # Training dispatcher
│   ├── train_class.py      # Classification pipelines
│   ├── train_reg.py        # Regression pipelines
│   ├── mailer.py           # Email verification (SMTP + Abstract API)
│   └── style.py            # UI theming & background
├── assets/
│   ├── Backg.jpg           # Login page background
│   └── app_bg.jpg          # Main app background
├── .streamlit/
│   └── secrets.toml        # Credentials (not in repo)
├── requirements.txt
└── .gitignore
```

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/nikunjm3003/automl-studio.git
cd automl-studio

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add credentials (see Secrets Setup below)

# 5. Run the app
streamlit run app.py
```

---

## 🗄️ Database Setup

AutoML Studio uses PostgreSQL for user authentication. Create this table before running:

```sql
CREATE TABLE users_automl (
    user_id      VARCHAR(36) PRIMARY KEY,
    username     VARCHAR(50) UNIQUE NOT NULL,
    email        VARCHAR(100) UNIQUE NOT NULL,
    password     TEXT NOT NULL,
    verified     BOOLEAN DEFAULT FALSE,
    verify_token TEXT
);
```

---

## 🔑 Secrets Setup

Create `.streamlit/secrets.toml` with the following:

```toml
[connections.postgresql]
url = "postgresql://user:password@host:port/dbname"

[gmail]
sender = "yourgmail@gmail.com"
app_password = "your_16_char_app_password"

[abstract]
api_key = "your_abstract_api_key"
```

- **PostgreSQL** — your Supabase or any PostgreSQL connection URL
- **Gmail** — sender email + [App Password](https://myaccount.google.com/apppasswords) (requires 2-Step Verification)
- **Abstract API** — free key from [abstractapi.com/email-verification](https://www.abstractapi.com/api/email-verification-validation-api) (100 verifications/day free)

---

## 📧 Email Verification Flow

1. User registers → Abstract API checks if the email is real
2. If valid, a verification email is sent via Gmail SMTP
3. User clicks the link in their inbox → account marked as verified in DB
4. Only verified accounts can log in

---

## 📦 Requirements

```
streamlit
pandas
numpy
scikit-learn
xgboost
imbalanced-learn
plotly
sqlalchemy
bcrypt
psycopg2-binary
requests
```

---

## 🙋 Author

**Nikunj Mishra**
Specializing in Machine Learning & Data Analysis

- GitHub: https://github.com/nikunjm3003
- LinkedIn: https://linkedin.com/in/nikunj-mishra-68b7052bb/

---

<p align="center">Built with ❤️ using Streamlit & scikit-learn</p>