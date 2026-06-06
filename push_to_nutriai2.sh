#!/bin/bash
# One-time script: create NutriAI2 on GitHub and push all files.
# Usage:
#   export GITHUB_TOKEN="your_token_here"
#   bash push_to_nutriai2.sh

set -euo pipefail

GITHUB_USER="${GITHUB_USER:-niti0309}"
REPO_NAME="${REPO_NAME:-NutriAI2}"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "ERROR: Set your token first:"
  echo '  export GITHUB_TOKEN="ghp_..."'
  exit 1
fi

echo "==> Creating public repo ${GITHUB_USER}/${REPO_NAME} (if it does not exist)..."
CREATE_RESP=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/user/repos" \
  -d "{\"name\":\"${REPO_NAME}\",\"description\":\"NutriAI — BAX-423 Automated Diet Plan Builder (Spring 2026)\",\"private\":false}")

HTTP_CODE=$(echo "$CREATE_RESP" | tail -n1)
BODY=$(echo "$CREATE_RESP" | sed '$d')

if [[ "$HTTP_CODE" == "201" ]]; then
  echo "    Created: https://github.com/${GITHUB_USER}/${REPO_NAME}"
elif [[ "$HTTP_CODE" == "422" ]]; then
  echo "    Repo already exists — continuing with push."
else
  echo "    Create response ($HTTP_CODE): $BODY"
  if [[ "$HTTP_CODE" != "422" ]]; then
    exit 1
  fi
fi

REMOTE_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo "==> Configuring git remote..."
if git remote get-url nutriai2 >/dev/null 2>&1; then
  git remote set-url nutriai2 "$REMOTE_URL"
else
  git remote add nutriai2 "$REMOTE_URL"
fi

echo "==> Pushing main branch..."
git push -u nutriai2 main

# Remove token from stored remote URL after push
git remote set-url nutriai2 "https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo ""
echo "Done! Repo: https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo ""
echo "Streamlit Cloud settings:"
echo "  Repository : ${GITHUB_USER}/${REPO_NAME}"
echo "  Branch     : main"
echo "  Main file  : code/app.py"
