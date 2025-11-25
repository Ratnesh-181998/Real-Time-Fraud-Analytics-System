# GITHUB_UPLOAD_GUIDE.md

## Overview
This repository contains a **Real‑Time Fraud Analytics System** – a full‑stack demo with:
- FastAPI backend (`src/api_server.py`, `src/api_server_demo.py`)
- XGBoost & Auto‑Encoder models (`src/models/…`)
- Feature engineering (`src/features/…`)
- Interactive web UI (`web‑ui/…`) with a UI‑showcase page
- Documentation (`README.md`, `PROJECT_SUMMARY.md`, `ARCHITECTURE.md`, `API_REFERENCE.md`)
- One‑click start script (`start.bat`) and Makefile for development

## Prerequisites
- Git installed (`git --version` ≥ 2.30)
- A GitHub account with a **Personal Access Token (PAT)** that has `repo` scope
- (Optional) SSH key added to GitHub if you prefer SSH URLs

## Step‑by‑Step Upload
1. **Create a new empty repo on GitHub**
   e.g. `https://github.com/<your‑username>/real‑time-fraud‑analytics`

2. **Initialize the local repo** (run from the project root `c:\Users\rattu\Downloads\L-12`):
   ```bat
   cd C:\Users\rattu\Downloads\L-12
   git init
   git add .
   git commit -m "Initial commit – complete fraud analytics system"
   ```

3. **Add the remote** (replace `<USERNAME>` and `<REPO>` with your values):
   ```bat
   git remote add origin https://github.com/<USERNAME>/<REPO>.git
   ```
   *or* using SSH:
   ```bat
   git remote add origin git@github.com:<USERNAME>/<REPO>.git
   ```

4. **Push to GitHub** (first push sets the upstream branch):
   ```bat
   git branch -M main
   git push -u origin main
   ```

5. **Verify**
   Open the repo URL in a browser – you should see all files, including:
   - `web-ui/ui_showcase.html` (the UI showcase page)
   - `web-ui/ui_*.png` (screenshots)
   - `src/`, `docs/`, `Makefile`, `start.bat`, etc.

## Optional – CI/CD (GitHub Actions)
If you want automated linting / testing on each push, add the following workflow:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run lint
        run: |
          pip install flake8
          flake8 src
      - name: Run basic test (demo API)
        run: |
          python -c "import src.api_server_demo as demo; print('Demo API imports OK')"
```

Commit this file as `.github/workflows/ci.yml` and push again – GitHub will automatically run the workflow.

## 🎉 You’re Done!
Your repository now contains a fully documented, runnable fraud‑analytics system ready for collaborators, reviewers, or a portfolio showcase. 🎈

*Tip:* Keep the `GITHUB_UPLOAD_GUIDE.md` in the repo – future contributors will thank you! 🚀
