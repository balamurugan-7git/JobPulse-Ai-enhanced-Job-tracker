"""
One-time training script for the role-type classifier.
Run this manually (not via the API) whenever you want to retrain:
    python -m job_tracker_backend.train_classifier
"""

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ---------- Training data ----------
# Each entry: (text, label). Text combines role title + short description,
# since that's what we'll feed the model at prediction time too.

TRAINING_DATA = [
    # SDE
    ("Software Development Engineer Intern building backend services in Java and Python", "sde"),
    ("SDE Intern working on distributed systems and microservices", "sde"),
    ("Backend Developer building REST APIs with Node.js and databases", "sde"),
    ("Full Stack Developer working on React frontend and Django backend", "sde"),
    ("Software Engineer Intern writing production code and unit tests", "sde"),
    ("Mobile App Developer building Android applications in Kotlin", "sde"),
    ("DevOps Engineer managing CI/CD pipelines and cloud infrastructure", "sde"),
    ("Site Reliability Engineer maintaining uptime of production systems", "sde"),

    # DATA
    ("Data Analyst Intern building dashboards and SQL queries for business insights", "data"),
    ("Data Engineer building ETL pipelines with Spark and Airflow", "data"),
    ("Business Intelligence Analyst creating reports in Tableau and Power BI", "data"),
    ("Data Analytics Intern analyzing customer behavior using Excel and SQL", "data"),
    ("Database Administrator managing MySQL and PostgreSQL clusters", "data"),
    ("Analytics Engineer transforming raw data into structured warehouse tables", "data"),

    # ML_AI
    ("Machine Learning Engineer Intern training deep learning models with PyTorch", "ml_ai"),
    ("AI Research Intern working on NLP and transformer architectures", "ml_ai"),
    ("Data Scientist building predictive models using scikit-learn and pandas", "ml_ai"),
    ("Computer Vision Engineer developing object detection models", "ml_ai"),
    ("ML Ops Engineer deploying and monitoring machine learning models in production", "ml_ai"),
    ("Applied Scientist Intern researching recommendation systems", "ml_ai"),

    # PRODUCT
    ("Product Manager Intern defining roadmap and writing product requirement documents", "product"),
    ("Associate Product Manager conducting user research and prioritizing features", "product"),
    ("Product Analyst working closely with engineering and design teams", "product"),
    ("Technical Product Manager owning the API product strategy", "product"),
    ("Product Owner Intern managing backlog and sprint planning", "product"),

    # DESIGN
    ("UI/UX Designer Intern creating wireframes and prototypes in Figma", "design"),
    ("Product Designer working on user flows and interaction design", "design"),
    ("Graphic Design Intern creating marketing assets and brand visuals", "design"),
    ("UX Researcher conducting usability testing and user interviews", "design"),
    ("Visual Designer Intern designing app icons and illustrations", "design"),

    # OTHER
    ("Marketing Intern managing social media campaigns and content calendars", "other"),
    ("HR Intern coordinating recruitment and onboarding processes", "other"),
    ("Sales Intern reaching out to prospective clients and closing deals", "other"),
    ("Finance Intern preparing quarterly financial reports and budgets", "other"),
    ("Operations Intern optimizing supply chain and logistics workflows", "other"),
    ("Content Writer Intern creating blog posts and SEO articles", "other"),
]


def train_and_save():
    texts = [t for t, _ in TRAINING_DATA]
    labels = [l for _, l in TRAINING_DATA]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000)),
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print("Evaluation on held-out test set:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Retrain on full dataset before saving (use all data for the final model)
    pipeline.fit(texts, labels)

    joblib.dump(pipeline, "job_tracker_backend/role_classifier.pkl")
    print("Model saved to job_tracker_backend/role_classifier.pkl")


if __name__ == "__main__":
    train_and_save()