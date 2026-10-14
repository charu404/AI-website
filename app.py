from flask import Flask, render_template, request
from urllib.parse import urlparse
import ipaddress, os, joblib

app = Flask(__name__)
MODEL_PATH = os.path.join("model", "phishing_model.joblib")

SUSPICIOUS_WORDS = [
    "login", "verify", "account", "update", "secure", "banking",
    "password", "signin", "confirm", "wallet", "gift", "free"
]

def extract_features(url):
    """Keep this feature order identical to train_model.py."""
    url = url.strip()
    parsed = urlparse(url if "://" in url else "http://" + url)
    host = parsed.hostname or ""
    path = parsed.path or ""
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
        sum(word in low for word in SUSPICIOUS_WORDS), len(path)
    ]

def valid_url(value):
    if not value or len(value) > 2048 or any(c.isspace() for c in value):
        return False
    parsed = urlparse(value if "://" in value else "http://" + value)
    return bool(parsed.hostname and "." in parsed.hostname)

@app.route("/", methods=["GET", "POST"])
def index():
    result, error, submitted_url = None, None, ""
    if request.method == "POST":
        submitted_url = request.form.get("url", "").strip()
        if not valid_url(submitted_url):
            error = "Enter a valid URL, for example https://example.com."
        elif not os.path.isfile(MODEL_PATH):
            error = "The model is missing. Run python train_model.py in the project terminal first."
        else:
            model = joblib.load(MODEL_PATH)
            features = [extract_features(submitted_url)]
            label = int(model.predict(features)[0])
            score = float(model.predict_proba(features)[0][1]) if hasattr(model, "predict_proba") else None
            result = {
                "label": "Potential phishing" if label == 1 else "Likely legitimate",
                "kind": "danger" if label == 1 else "safe",
                "score": score
            }
    return render_template("index.html", result=result, error=error, submitted_url=submitted_url)

if __name__ == "__main__":
    # Local development only. For production, use a production WSGI server.
    app.run(debug=True)
