# PhishGuard — AI-Based Phishing Website Detection

Animated, responsive Flask website + Random Forest URL classifier. Designed to run locally on Windows in VS Code and can be deployed to a Python web host.

## 1. Run on Windows

Install Python 3.11 (check **Add Python to PATH**) and Git. Extract this ZIP, then open the `AI-Phishing-Website-Detection` folder in VS Code.

In VS Code choose **Terminal → New Terminal**, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python train_model.py
python app.py
```

Open `http://127.0.0.1:5000` in your browser. Stop the local server with `Ctrl+C`.

If PowerShell blocks environment activation, use Command Prompt terminal:
```bat
.venv\Scripts\activate.bat
```
Then run the install/train/run commands.

## 2. Train with your own dataset

Place a CSV in `dataset/` with columns named `url` and `label` (`0` legitimate, `1` phishing, after verifying the dataset's documentation). Example:

```powershell
python train_model.py --csv dataset/urls.csv
```

The included small synthetic dataset is only a demo. Do not report its metrics as real model performance.

## 3. Push to GitHub from VS Code

1. Create a new empty repository in your GitHub account.
2. Open this project folder in VS Code.
3. Select **Source Control** on the left.
4. Click **Initialize Repository**.
5. Review the files; do not add private data, credentials, or `.venv`.
6. Enter a commit message such as `Build PhishGuard phishing URL scanner`, click **Commit**.
7. Choose **Publish to GitHub** and follow the sign-in prompts.

Or use the terminal (replace the placeholder with your own repository URL):

```bash
git init
git add .
git commit -m "Build PhishGuard phishing URL scanner"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

The `.gitignore` intentionally excludes the trained `.joblib` model. For deployment, retrain on the host from a properly managed dataset or adjust the workflow to securely provide the trained model.

## 4. Deploy the website

GitHub Pages cannot run a Flask/Python backend. Push the source to GitHub, then use a Python hosting service that supports Flask (for example Render or Railway) and connect the repository.

Typical build/install command:
`pip install -r requirements.txt`

Typical start command on Linux hosting:
`gunicorn app:app`

Before deployment, ensure the model exists on the host. You can change the build/start workflow to run `python train_model.py` before starting Gunicorn, or use a verified training dataset/model artifact. Do not use the synthetic demo model as a production security service. Free hosting availability and requirements may change.

## 5. Important security limitations

- This is an educational prototype, not a definitive safety verdict.
- It only analyzes URL text; it does not visit submitted URLs.
- HTTPS does not guarantee a site is legitimate.
- The model score is not a calibrated probability of danger.
- Real evaluation requires a large, verified, representative dataset, leakage-resistant splitting, threshold testing, monitoring, rate limiting and security review.
- `debug=True` is for local development only. Do not expose the Flask development server publicly.
