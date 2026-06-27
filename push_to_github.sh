#!/usr/bin/env bash
# push_to_github.sh — create the "link to your code" for the Kaggle submission.
# Usage: edit GH_USER below, create an empty repo named "promoguard" on GitHub, then run this.
set -euo pipefail

GH_USER="HuaNgo3979"     # <-- change me
REPO="promoguard"

git init
git add .
git config user.name  "Kaggle Student"
git config user.email "student@example.com"
# Pre-commit will fire if installed; the repo ships clean (no hardcoded secrets).
git commit -m "feat: PromoGuard ambient promotion-integrity agent (ADK 2.0 capstone)"
git branch -M main
git remote add origin "https://github.com/${GH_USER}/${REPO}.git"
git push -u origin main

echo
echo "Done. Your code link for the Kaggle writeup is:"
echo "  https://github.com/${GH_USER}/${REPO}"
