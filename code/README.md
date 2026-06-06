# NutriAI — Automated Diet Plan Builder
**BAX-423 Big Data · Spring 2026 · Final Project Option A**

> Generates a clinically-safe, allergen-free, diverse 7-day meal plan in under 60 seconds.

---

## Quick Start (Local)

```bash
# 1. Clone / unzip the project
cd LastName_FirstName_BAX423_Final

# 2. Install dependencies
pip install -r code/requirements.txt

# 3. Run
streamlit run code/app.py
```

App opens at **http://localhost:8501**

---

## Deploy to Streamlit Community Cloud (Free)

1. Push this repo to GitHub (public or private).
2. Go to **https://share.streamlit.io** → "New app"
3. Set:
   - **Repository**: your GitHub repo
   - **Branch**: `main`
   - **Main file path**: `code/app.py`
4. Click **Deploy** — live URL in ~2 minutes.

> Make sure `data/food_database.csv` is committed to the repo (it's ~2MB, well within limits).

---

## Deploy to Render (Free tier)

1. Create a `render.yaml` in root:
```yaml
services:
  - type: web
    name: nutriai
    env: python
    buildCommand: pip install -r code/requirements.txt
    startCommand: streamlit run code/app.py --server.port $PORT --server.address 0.0.0.0
```
2. Connect your GitHub repo on **https://render.com** → "New Web Service"

---

## Project Structure

```
├── code/
│   ├── app.py              # Main Streamlit application
│   └── requirements.txt    # Python dependencies
├── data/
│   └── food_database.csv   # 5,000+ food items with full nutrient profiles
├── brief.pdf               # Technical brief (4 pages)
├── prompts.md              # Key AI prompts used
└── README.md               # This file
```

---

## 6 Core Capabilities

| # | Capability | Status |
|---|-----------|--------|
| 1 | Clinical Condition Filtering (IBS, GERD, T2D, Hypertension) | ✅ |
| 2 | Allergy Detection & Exclusion (8 standard + custom) | ✅ |
| 3 | Dietary Preference Handling (Veg/Vegan/Pesc/Halal/Kosher) | ✅ |
| 4 | Diversity Engine (no repeats, diversity score) | ✅ |
| 5 | Macro & Micronutrient Analysis vs RDA | ✅ |
| 6 | Sub-60s Generation with technique benchmarks | ✅ |

---

## BAX-423 Techniques Used

| Technique | Lecture | Implementation |
|-----------|---------|----------------|
| **Bloom Filter** | Sketching | Probabilistic allergen/flag exclusion — O(k) lookup vs O(n) scan |
| **TF-IDF Embeddings + FAISS** | Embeddings / Retrieval | Semantic meal ranking per slot — sub-linear ANN search |

---

## Test Personas

| Persona | Diet | Conditions | Allergens | Calories |
|---------|------|-----------|-----------|---------|
| Priya | Vegetarian | IBS | Dairy | 1800 |
| Ravi | Non-Veg | GERD | Gluten | 2200 |
| Mei | Vegan | T2 Diabetes | Tree Nuts | 1600 |
| James | Pescatarian | Hypertension | Soy | 2000 |

---

## Data Sources

- **USDA FoodData Central** — nutrient profiles (Foundation + SR Legacy)
- **NIH RDA tables** — Recommended Dietary Allowances by sex
- **Monash University Low-FODMAP list** — IBS-safe food rules
- **DASH diet guidelines (NHLBI)** — Hypertension sodium limits

*Offline snapshot included in `data/food_database.csv` (**≥10,000** deduplicated items) for grader use without API access.*

Verify ingestion (rubric §1):

```bash
cd data
python verify_ingestion.py   # prints PASS when ≥10,000 records
```
