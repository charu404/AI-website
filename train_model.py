import argparse, os, ipaddress, joblib
import pandas as pd
from urllib.parse import urlparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

MODEL_PATH = "model/phishing_model.joblib"
WORDS = ["login", "verify", "account", "update", "secure", "banking",
         "password", "signin", "confirm", "wallet", "gift", "free"]

def extract_features(url):
    url = str(url).strip()
    parsed = urlparse(url if "://" in url else "http://" + url)
    host, path = parsed.hostname or "", parsed.path or ""
    try:
        ipaddress.ip_address(host)
        is_ip = 1
    except ValueError:
        is_ip = 0
    low = url.lower()
    return [
        len(url), len(host), url.count("."), url.count("-"), url.count("@"),
        url.count("?"), url.count("="), url.count("//"),
        sum(c.isdigit() for c in url), int(parsed.scheme.lower() == "https"),
        is_ip, max(0, len([p for p in host.split(".") if p]) - 2),
        sum(word in low for word in WORDS), len(path)
    ]

def demo_dataset():
    # Synthetic examples are only for testing that the website runs.
    return pd.DataFrame([
        ("https://www.google.com", 0), ("https://www.wikipedia.org", 0),
        ("https://www.microsoft.com", 0), ("https://www.python.org", 0),
        ("https://www.mozilla.org", 0), ("https://www.github.com", 0),
        ("http://192.168.1.10/login/verify-account", 1),
        ("http://secure-login-account.example.invalid/verify?account=12345", 1),
        ("http://paypal-login.example.invalid/update-password", 1),
        ("http://banking-account-verify.example.invalid/signin", 1),
        ("http://free-gift-wallet.example.invalid/confirm?user=1", 1),
        ("http://verify-your-account.example.invalid/password", 1),
        ("http://account-security-check.example.invalid/login", 1),
        ("http://login-update.example.invalid/verify?password=12", 1),
        ("https://www.python.org/about/", 0), ("https://docs.github.com", 0),
    ], columns=["url", "label"])

def main():
    parser = argparse.ArgumentParser(description="Train phishing URL classifier")
    parser.add_argument("--csv", default="", help="CSV containing url and label columns")
    args = parser.parse_args()
    if args.csv:
        if not os.path.isfile(args.csv):
            raise FileNotFoundError(f"CSV not found: {args.csv}")
        df = pd.read_csv(args.csv)
        if not {"url", "label"}.issubset(df.columns):
            raise ValueError("CSV must have columns named url and label.")
    else:
        print("Using a tiny synthetic demo dataset. Its metrics are NOT meaningful.")
        df = demo_dataset()

    df = df[["url", "label"]].dropna().copy()
    df["url"] = df["url"].astype(str).str.strip()
    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    df = df[df["label"].isin([0, 1]) & (df["url"].str.len() > 0)]
    df["label"] = df["label"].astype(int)
    if len(df) < 8 or df["label"].nunique() != 2:
        raise ValueError("Provide at least 8 valid rows and both labels 0 and 1.")

    X = pd.DataFrame(df["url"].map(extract_features).tolist())
    y = df["label"]
    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=stratify
    )
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("rf", RandomForestClassifier(n_estimators=250, random_state=42, class_weight="balanced"))
    ])
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    print(f"Accuracy:  {accuracy_score(y_test, pred):.3f}")
    print(f"Precision: {precision_score(y_test, pred, zero_division=0):.3f}")
    print(f"Recall:    {recall_score(y_test, pred, zero_division=0):.3f}")
    print(f"F1 score:  {f1_score(y_test, pred, zero_division=0):.3f}")
    print(classification_report(y_test, pred, zero_division=0))
    os.makedirs("model", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")

if __name__ == "__main__":
    main()
