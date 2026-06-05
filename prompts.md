# prompts.md — Key AI Prompts Used

**BAX-423 NutriAI · AI Tool: Claude**

---

## Prompt 1 — Food Database Generation
**Prompt:** "Generate a Python script to create a 5,000+ item food database CSV with columns for name, cuisine (Indian/Chinese/Korean/American etc.), diet tags (vegan/vegetarian/pescatarian/halal/kosher), allergens, macros (calories/protein/carbs/fat/fiber), and micronutrients (iron/calcium/B12/vitD/zinc/potassium/magnesium/sodium), plus clinical flags (is_high_fodmap, is_gerd_trigger, is_high_gi, is_high_sodium, has_soy, has_tree_nuts). Use USDA-aligned nutrient ranges per food category."
**Used for:** Generating the seed food templates and expansion logic in the data pipeline.
**Modifications:** Added 12 cuisine categories, added Halal/Kosher diet tags, tuned per-category micronutrient baselines to be medically realistic.

---

## Prompt 2 — Bloom Filter Implementation
**Prompt:** "Implement a Bloom filter in pure Python (no external libraries) for allergen exclusion in a diet planning app. It should support add() and __contains__() methods, use md5+sha256 dual hashing, and be configurable by capacity and error rate."
**Used for:** BAX-423 Technique 1 (Sketching) — Step 1 of the food filtering pipeline.
**Modifications:** Adjusted to use bytearray instead of bitarray to avoid extra dependencies. Added food_id-based key design for pipeline integration.

---

## Prompt 3 — FAISS + TF-IDF Meal Ranking
**Prompt:** "Write a function that builds a TF-IDF embedding matrix from food item text (name + cuisine + diet tags + categories) and indexes it with FAISS IndexFlatIP for cosine similarity search. Then write a query function that embeds a meal slot description (e.g. 'vegan IBS breakfast grain') and retrieves top-k relevant foods."
**Used for:** BAX-423 Technique 2 (Embeddings) — Step 3 of the meal ranking pipeline.
**Modifications:** Added @st.cache_resource decorator for efficiency, added fallback to category-based filtering when FAISS unavailable, normalized vectors with faiss.normalize_L2 for cosine similarity.

---

## Prompt 4 — Clinical Filtering Logic
**Prompt:** "Write Python logic to filter foods for IBS (FODMAP), GERD (acid triggers), Type 2 Diabetes (GI ≤ 55), and Hypertension (sodium ≤ 1500 mg/day DASH). Return not just a boolean but a list of human-readable exclusion reasons for the 'Why excluded' feature."
**Used for:** Core Capability 1 (Clinical Condition Filtering) and the Why Excluded tab.
**Modifications:** Added per-meal sodium threshold (600mg/meal) instead of total daily to make filtering practical at query time. Added cross-contamination risk language.

---

## Prompt 5 — Streamlit UI Design
**Prompt:** "Build a dark-themed Streamlit app for a clinical diet planner. Use a sidebar for user inputs (dietary preference, cuisine selection, allergies, conditions). Main area should have a hero header, metric cards for generation stats, and a tabbed interface showing the 7-day meal plan, nutrient analysis, excluded foods, and CSV export. Use custom CSS with the Syne + DM Sans font pairing."
**Used for:** Full UI layout and styling.
**Modifications:** Added BAX-423 technique badges, persona display cards, diversity score display, per-meal detailed nutrient grid, and the benchmark table.

---

## Prompt 6 — RDA Nutrient Analysis
**Prompt:** "Write a function that takes a 7-day meal plan dict and computes daily macro+micronutrient totals, comparing them against NIH RDA values differentiated by sex. Flag any day where a micronutrient falls below 80% of RDA. Return structured data suitable for display in a bar-chart-style UI."
**Used for:** Core Capability 5 (Macro & Micronutrient Analysis).
**Modifications:** Added sodium handling separately (lower-is-better for hypertension, not RDA-style), added weekly average summary table.
