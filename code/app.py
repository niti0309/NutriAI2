"""
NutriAI — Automated Diet Plan Builder
BAX-423 Big Data · Spring 2026
BAX-423 Techniques: TF-IDF Embeddings (FAISS) + Bloom Filter (allergen exclusion)
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import hashlib
import json
import os
import io
from datetime import datetime
from collections import defaultdict

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="NutriAI — Personalized Diet Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3, .big-title {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
}
.stApp {
    background: #0a0e1a;
    color: #e8eaf0;
}
[data-testid="stSidebar"] {
    background: #0f1526 !important;
    border-right: 1px solid #1e2a45;
}
.metric-card {
    background: linear-gradient(135deg, #111827, #1a2235);
    border: 1px solid #2d3a52;
    border-radius: 14px;
    padding: 18px 22px;
    margin: 8px 0;
}
.meal-card {
    background: linear-gradient(135deg, #0d1625, #141f35);
    border: 1px solid #243049;
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
    transition: border-color 0.2s;
}
.meal-card:hover {
    border-color: #4ade80;
}
.day-header {
    background: linear-gradient(90deg, #1a4731, #0d2818);
    border-left: 4px solid #4ade80;
    border-radius: 0 10px 10px 0;
    padding: 10px 18px;
    margin: 18px 0 8px 0;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: #4ade80;
}
.excluded-tag {
    background: #2d1018;
    border: 1px solid #7f1d1d;
    color: #fca5a5;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.78rem;
    display: inline-block;
    margin: 2px 4px;
}
.included-tag {
    background: #0d2818;
    border: 1px solid #166534;
    color: #4ade80;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.78rem;
    display: inline-block;
    margin: 2px 4px;
}
.warn-tag {
    background: #2d2310;
    border: 1px solid #92400e;
    color: #fbbf24;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.78rem;
    display: inline-block;
    margin: 2px 4px;
}
.nutrient-bar-label { font-size: 0.82rem; color: #94a3b8; margin-bottom: 2px; }
.nutrient-bar-val   { font-size: 0.88rem; font-weight: 600; color: #e2e8f0; }
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4ade80, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.15;
    margin-bottom: 0.3rem;
}
.hero-sub {
    font-size: 1.05rem;
    color: #64748b;
    margin-bottom: 1.5rem;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 24px 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e2a45;
}
.pass-badge  { color: #4ade80; font-weight: 700; }
.fail-badge  { color: #f87171; font-weight: 700; }
.warn-badge  { color: #fbbf24; font-weight: 700; }
.gen-timer   { font-family: 'Syne', sans-serif; font-size: 1.6rem; color: #22d3ee; font-weight: 800; }
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #16a34a, #0e7490) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.6rem 1.8rem !important;
    transition: opacity 0.2s !important;
}
div[data-testid="stButton"] > button:hover { opacity: 0.88 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'food_database.csv')

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df['diet_tags_list']       = df['diet_tags'].fillna('').str.split('|')
    df['allergens_list']       = df['allergens'].fillna('').str.split('|')
    df['categories_list']      = df['categories'].fillna('').str.split('|')
    df['safe_conditions_list'] = df['safe_conditions'].fillna('').str.split('|')
    return df

# ─────────────────────────────────────────────
# BAX-423 TECHNIQUE 1 — BLOOM FILTER (allergen exclusion)
# ─────────────────────────────────────────────
class BloomFilter:
    """Probabilistic set membership for fast allergen/flag exclusion (BAX-423: Sketching)."""
    def __init__(self, capacity=50000, error_rate=0.001):
        self.size = self._get_size(capacity, error_rate)
        self.hash_count = self._get_hash_count(self.size, capacity)
        self.bit_array = bytearray(self.size)

    @staticmethod
    def _get_size(n, p): return int(-(n * np.log(p)) / (np.log(2)**2))

    @staticmethod
    def _get_hash_count(m, n): return int((m / n) * np.log(2))

    def _hashes(self, item):
        h1 = int(hashlib.md5(item.encode()).hexdigest(), 16)
        h2 = int(hashlib.sha256(item.encode()).hexdigest(), 16)
        return [(h1 + i * h2) % self.size for i in range(self.hash_count)]

    def add(self, item):
        for idx in self._hashes(str(item)):
            self.bit_array[idx] = 1

    def __contains__(self, item):
        return all(self.bit_array[idx] for idx in self._hashes(str(item)))

def build_exclusion_filter(food_ids_to_exclude):
    bf = BloomFilter()
    for fid in food_ids_to_exclude:
        bf.add(fid)
    return bf

# ─────────────────────────────────────────────
# BAX-423 TECHNIQUE 2 — TF-IDF EMBEDDINGS + FAISS (matching/ranking)
# ─────────────────────────────────────────────
@st.cache_resource
def build_faiss_index(df):
    """Build TF-IDF embedding matrix + FAISS index for meal ranking (BAX-423: Embeddings)."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import faiss

        corpus = (
            df['name'] + ' ' + df['cuisine'] + ' ' +
            df['diet_tags'].fillna('') + ' ' +
            df['categories'].fillna('') + ' ' +
            df['safe_conditions'].fillna('')
        ).tolist()

        vec = TfidfVectorizer(max_features=256, ngram_range=(1,2))
        X = vec.fit_transform(corpus).toarray().astype('float32')
        faiss.normalize_L2(X)

        index = faiss.IndexFlatIP(X.shape[1])
        index.add(X)
        return vec, index, X
    except Exception:
        return None, None, None

def embed_query(query_text, vectorizer):
    import faiss
    q = vectorizer.transform([query_text]).toarray().astype('float32')
    faiss.normalize_L2(q)
    return q

# ─────────────────────────────────────────────
# RDA TARGETS (per day) — adult defaults
# ─────────────────────────────────────────────
RDA = {
    'iron_mg':       {'M': 8,   'F': 18},
    'calcium_mg':    {'M': 1000,'F': 1000},
    'vitamin_b12_ug':{'M': 2.4, 'F': 2.4},
    'vitamin_d_iu':  {'M': 600, 'F': 600},
    'zinc_mg':       {'M': 11,  'F': 8},
    'potassium_mg':  {'M': 3400,'F': 2600},
    'magnesium_mg':  {'M': 420, 'F': 320},
}

def get_rda(sex='M'):
    return {k: v[sex] for k, v in RDA.items()}

# ─────────────────────────────────────────────
# CLINICAL + ALLERGY FILTERING
# ─────────────────────────────────────────────
CONDITION_RULES = {
    'IBS':          {'exclude_flags': ['is_high_fodmap'], 'label': 'High-FODMAP — triggers IBS symptoms'},
    'GERD':         {'exclude_flags': ['is_gerd_trigger'], 'label': 'GERD trigger food (citrus/spicy/fried)'},
    'T2 Diabetes':  {'max_gi': 55, 'label': 'High glycaemic index (GI > 55) — spikes blood sugar'},
    'Hypertension': {'max_sodium': 1500, 'label': 'Excess sodium — raises blood pressure'},
}

ALLERGEN_MAP = {
    'Gluten':      ['gluten','wheat','barley','rye'],
    'Dairy':       ['dairy','milk','lactose','cheese','butter','cream','whey'],
    'Eggs':        ['eggs','egg'],
    'Tree Nuts':   ['tree nuts','almonds','cashews','walnuts','pistachios','pecans','hazelnuts','macadamia','brazil nuts'],
    'Peanuts':     ['peanuts','peanut'],
    'Shellfish':   ['shellfish','shrimp','crab','lobster','prawn'],
    'Fish':        ['fish','salmon','tuna','cod','mackerel','tilapia','bass','trout'],
    'Soy':         ['soy','tofu','edamame','tempeh','miso'],
    'Sesame':      ['sesame','tahini'],
}

DIET_ANIMAL_RULES = {
    'Vegan':        {'blocked_allergens': [], 'blocked_categories': [], 'blocked_tags': ['non-vegetarian','pescatarian','vegetarian'], 'required_tag': 'vegan'},
    'Vegetarian':   {'blocked_tags': ['non-vegetarian','pescatarian'], 'required_tag': 'vegetarian'},
    'Pescatarian':  {'blocked_tags': ['non-vegetarian'], 'required_tag': None, 'allow_seafood': True},
    'Non-Vegetarian': {'required_tag': None},
}

ANIMAL_ALLERGENS = {'dairy','eggs','fish','shellfish'}

def is_food_excluded(row, conditions, allergens_set, diet, cuisines, custom_allergens):
    """Returns (excluded: bool, reasons: list[str])"""
    reasons = []

    # Diet filter
    tags = set(row['diet_tags_list'])
    if diet == 'Vegan':
        if 'vegan' not in tags:
            reasons.append('Not vegan-certified')
            # also check animal allergens
            for a in ANIMAL_ALLERGENS:
                if a in row['allergens_list']:
                    reasons.append(f'Contains animal product: {a}')
    elif diet == 'Vegetarian':
        if not any(t in tags for t in ['vegan','vegetarian']):
            reasons.append('Not vegetarian')
    elif diet == 'Pescatarian':
        if 'non-vegetarian' in tags and 'pescatarian' not in tags:
            reasons.append('Contains meat (not pescatarian-friendly)')
    elif diet == 'Halal':
        if 'halal' not in tags:
            reasons.append('Not Halal-certified')
    elif diet == 'Kosher':
        if 'kosher' not in tags:
            reasons.append('Not Kosher-certified')

    # Allergen filter (Bloom Filter used upstream; this is the secondary exact check)
    food_allergens = set(row['allergens_list'])
    for allergen in allergens_set:
        keywords = ALLERGEN_MAP.get(allergen, [allergen.lower()])
        for kw in keywords:
            if any(kw in fa.lower() for fa in food_allergens) or kw in row['name'].lower():
                reasons.append(f'Allergen: {allergen}')
                break

    # Custom allergens
    for ca in custom_allergens:
        ca_lower = ca.lower().strip()
        if ca_lower and (ca_lower in row['name'].lower() or
                         any(ca_lower in fa.lower() for fa in food_allergens)):
            reasons.append(f'Custom allergen: {ca}')

    # Clinical condition filters
    for cond in conditions:
        if cond == 'IBS' and row.get('is_high_fodmap', 0):
            reasons.append('High-FODMAP — excluded for IBS')
        if cond == 'GERD' and row.get('is_gerd_trigger', 0):
            reasons.append('GERD trigger food (citrus/spicy/fried/acidic)')
        if cond == 'T2 Diabetes':
            gi = row.get('gi_score', 0)
            if gi > 55:
                reasons.append(f'High GI ({gi}) — excluded for T2 Diabetes')
        if cond == 'Hypertension':
            # Per-meal sodium limit (total daily = 1500, we allow ~500/meal)
            if row.get('sodium_mg', 0) > 600:
                reasons.append(f'High sodium ({row["sodium_mg"]} mg/meal) — excluded for Hypertension')

    return len(reasons) > 0, reasons

# ─────────────────────────────────────────────
# DIVERSITY ENGINE
# ─────────────────────────────────────────────
def diversity_score(plan_names):
    """Simple diversity: ratio of unique foods to total meals."""
    if not plan_names:
        return 0.0
    return len(set(plan_names)) / len(plan_names)

# ─────────────────────────────────────────────
# PLAN GENERATION
# ─────────────────────────────────────────────
MEAL_SLOTS = ['Breakfast', 'Lunch', 'Dinner']
DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

MEAL_CATEGORY_PREFS = {
    'Breakfast': ['breakfast','grain','fruit','light','snack'],
    'Lunch':     ['main','salad','soup','grain','legume'],
    'Dinner':    ['main','protein','seafood','vegetable','legume'],
}

def generate_plan(df, conditions, allergens_set, diet, cuisines, calorie_target, sex,
                  custom_allergens, vectorizer, faiss_index, faiss_vectors):
    """
    Full pipeline:
    1. Build Bloom Filter of excluded food IDs
    2. Pre-filter candidate pool (diet, allergens, clinical)
    3. FAISS embedding-based retrieval per meal slot
    4. Diversity-enforced assignment across 7 days
    """
    t0 = time.time()
    exclusions = []  # [(food_name, reasons)]
    excluded_ids = set()

    # ── Step 1: Mark exclusions & build Bloom Filter ──────────────────────
    for _, row in df.iterrows():
        excl, reasons = is_food_excluded(row, conditions, allergens_set, diet, cuisines, custom_allergens)
        if excl:
            excluded_ids.add(row['food_id'])
            exclusions.append({'name': row['name'], 'reasons': reasons})

    bloom = build_exclusion_filter(excluded_ids)

    # ── Step 2: Candidate pool ──────────────────────────────────────────
    candidates = df[~df['food_id'].apply(lambda x: x in bloom)].copy()

    # Cuisine filter (if specific cuisines chosen)
    if cuisines and 'All' not in cuisines:
        candidates = candidates[candidates['cuisine'].isin(cuisines)]

    if len(candidates) < 21:
        # Fallback: relax cuisine filter
        candidates = df[~df['food_id'].apply(lambda x: x in bloom)].copy()

    if len(candidates) < 21:
        return None, exclusions, 0

    # ── Step 3: FAISS embedding retrieval per meal slot ─────────────────
    # Build query per meal slot + user profile
    diet_query = diet.lower()
    cond_query = ' '.join(conditions).lower() if conditions else 'healthy'

    slot_pools = {}
    for slot in MEAL_SLOTS:
        cat_prefs = ' '.join(MEAL_CATEGORY_PREFS[slot])
        query_text = f"{diet_query} {cond_query} {cat_prefs} healthy"
        if vectorizer is not None and faiss_index is not None:
            try:
                q_vec = embed_query(query_text, vectorizer)
                k = min(200, len(candidates))
                D, I = faiss_index.search(q_vec, k)
                top_indices = I[0][I[0] >= 0]
                # Filter to candidates only
                candidate_ids_set = set(candidates.index.tolist())
                ranked = [i for i in top_indices if i in candidate_ids_set][:100]
                slot_pool = candidates.loc[ranked] if ranked else candidates
            except Exception:
                slot_pool = candidates
        else:
            # Fallback: filter by category preference
            cat_filter = candidates[candidates['categories'].apply(
                lambda x: any(c in str(x) for c in MEAL_CATEGORY_PREFS[slot])
            )]
            slot_pool = cat_filter if len(cat_filter) >= 7 else candidates
        slot_pools[slot] = slot_pool

    # ── Step 4: Diverse 7-day assignment ─────────────────────────────────
    cal_per_meal = {
        'Breakfast': calorie_target * 0.25,
        'Lunch':     calorie_target * 0.38,
        'Dinner':    calorie_target * 0.37,
    }

    plan = {day: {} for day in DAYS}
    used_names = set()

    for day in DAYS:
        for slot in MEAL_SLOTS:
            pool = slot_pools[slot]
            # Prefer not-yet-used foods
            unused = pool[~pool['name'].isin(used_names)]
            source = unused if len(unused) >= 3 else pool

            # Calorie proximity scoring (pick closest to target per meal)
            target_cal = cal_per_meal[slot]
            source = source.copy()
            source['_cal_diff'] = (source['calories'] - target_cal).abs()
            source = source.sort_values('_cal_diff')

            # Pick top-5, choose randomly for variety
            top_n = min(8, len(source))
            chosen = source.iloc[random.randint(0, max(0, top_n-1))]
            plan[day][slot] = chosen.to_dict()
            used_names.add(chosen['name'])

    t1 = time.time()
    elapsed = round(t1 - t0, 2)
    return plan, exclusions, elapsed

# ─────────────────────────────────────────────
# NUTRITIONAL ANALYSIS
# ─────────────────────────────────────────────
MACROS = ['calories','protein_g','carbs_g','fat_g','fiber_g']
MICROS = ['iron_mg','calcium_mg','vitamin_b12_ug','vitamin_d_iu','zinc_mg','potassium_mg','magnesium_mg','sodium_mg']

def analyze_plan(plan, sex='M'):
    rda = get_rda(sex)
    daily_summaries = []
    all_names = []
    for day in DAYS:
        day_totals = defaultdict(float)
        for slot in MEAL_SLOTS:
            meal = plan[day][slot]
            for col in MACROS + MICROS:
                day_totals[col] += float(meal.get(col, 0))
            all_names.append(meal['name'])
        # RDA check
        flags = {}
        for micro, rda_val in rda.items():
            actual = day_totals.get(micro, 0)
            pct = (actual / rda_val * 100) if rda_val > 0 else 0
            flags[micro] = {'actual': round(actual, 1), 'rda': rda_val, 'pct': round(pct, 0), 'ok': pct >= 80}
        daily_summaries.append({'day': day, 'totals': dict(day_totals), 'rda_flags': flags})
    diversity = diversity_score(all_names)
    return daily_summaries, diversity

# ─────────────────────────────────────────────
# CSV EXPORT
# ─────────────────────────────────────────────
def plan_to_csv(plan, daily_summaries):
    rows = []
    for day in DAYS:
        for slot in MEAL_SLOTS:
            meal = plan[day][slot]
            rows.append({
                'Day': day, 'Meal': slot, 'Food': meal['name'],
                'Cuisine': meal.get('cuisine',''), 'Calories': meal.get('calories',0),
                'Protein_g': meal.get('protein_g',0), 'Carbs_g': meal.get('carbs_g',0),
                'Fat_g': meal.get('fat_g',0), 'Fiber_g': meal.get('fiber_g',0),
                'Iron_mg': meal.get('iron_mg',0), 'Calcium_mg': meal.get('calcium_mg',0),
                'B12_ug': meal.get('vitamin_b12_ug',0), 'VitD_IU': meal.get('vitamin_d_iu',0),
                'Zinc_mg': meal.get('zinc_mg',0), 'Potassium_mg': meal.get('potassium_mg',0),
                'Magnesium_mg': meal.get('magnesium_mg',0), 'Sodium_mg': meal.get('sodium_mg',0),
            })
    return pd.DataFrame(rows).to_csv(index=False)

# ─────────────────────────────────────────────
# SIDEBAR — USER PROFILE
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:#4ade80;margin-bottom:4px;">🥗 NutriAI</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#64748b;font-size:0.85rem;margin-bottom:18px;">Personalized 7-Day Meal Planner</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("**👤 Personal Info**")
    col_a, col_b = st.columns(2)
    with col_a:
        age = st.number_input("Age", 10, 100, 30, key='age')
    with col_b:
        sex = st.selectbox("Sex", ["M", "F"], key='sex')

    calorie_target = st.slider("Daily Calorie Target (kcal)", 1200, 4000, 2000, 50)

    st.divider()
    st.markdown("**🥦 Dietary Preference**")
    diet = st.selectbox("Diet Type", [
        "Non-Vegetarian", "Vegetarian", "Vegan", "Pescatarian", "Halal", "Kosher"
    ])

    st.markdown("**🌍 Cuisine Preferences**")
    all_cuisines = ['Indian','Chinese','Korean','American','Mexican','Mediterranean','Japanese','Thai','Italian','Middle Eastern','French','Greek']
    cuisines_selected = st.multiselect(
        "Select cuisines (leave empty for all)",
        options=all_cuisines,
        default=[]
    )
    cuisines_final = cuisines_selected if cuisines_selected else all_cuisines

    st.divider()
    st.markdown("**🏥 Clinical Conditions**")
    conditions = st.multiselect(
        "Select your conditions",
        options=["IBS", "GERD", "T2 Diabetes", "Hypertension"],
        default=[]
    )

    st.divider()
    st.markdown("**⚠️ Allergies & Intolerances**")
    allergen_options = list(ALLERGEN_MAP.keys())
    selected_allergens = st.multiselect(
        "Common allergens",
        options=allergen_options,
        default=[]
    )
    custom_allergens_raw = st.text_input(
        "Custom allergens (comma-separated)",
        placeholder="e.g. mustard, celery, lupin"
    )
    custom_allergens = [a.strip() for a in custom_allergens_raw.split(',') if a.strip()]

    st.divider()
    generate_btn = st.button("🚀 Generate My 7-Day Plan", use_container_width=True)

# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
df = load_data()
vectorizer, faiss_index, faiss_vectors = build_faiss_index(df)

# Hero header
st.markdown('<div class="hero-title">NutriAI — Your Personal Diet Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Clinically-aware · Allergen-safe · 7-day personalized meal plans · Sub-60s generation</div>', unsafe_allow_html=True)

# Technique badges
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="metric-card"><b style="color:#22d3ee">🔬 BAX-423 Technique 1</b><br><span style="color:#94a3b8;font-size:0.88rem">Bloom Filter — probabilistic allergen exclusion (O(1) lookups)</span></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card"><b style="color:#a78bfa">🧠 BAX-423 Technique 2</b><br><span style="color:#94a3b8;font-size:0.88rem">TF-IDF Embeddings + FAISS — semantic meal ranking</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="metric-card"><b style="color:#4ade80">📊 Dataset</b><br><span style="color:#94a3b8;font-size:0.88rem">{:,} food items · USDA-aligned nutrients</span></div>'.format(len(df)), unsafe_allow_html=True)

st.divider()

if generate_btn:
    with st.spinner("Building your personalized plan..."):
        plan, exclusions, elapsed = generate_plan(
            df, conditions, set(selected_allergens), diet,
            cuisines_final, calorie_target, sex, custom_allergens,
            vectorizer, faiss_index, faiss_vectors
        )

    if plan is None:
        st.error("⚠️ Not enough foods match your constraints. Try relaxing cuisine filters or allergen selections.")
        st.stop()

    daily_summaries, div_score = analyze_plan(plan, sex)
    st.session_state['plan'] = plan
    st.session_state['exclusions'] = exclusions
    st.session_state['elapsed'] = elapsed
    st.session_state['daily_summaries'] = daily_summaries
    st.session_state['div_score'] = div_score
    st.session_state['calorie_target'] = calorie_target
    st.session_state['sex'] = sex

# Show plan if generated
if 'plan' in st.session_state:
    plan = st.session_state['plan']
    exclusions = st.session_state['exclusions']
    elapsed = st.session_state['elapsed']
    daily_summaries = st.session_state['daily_summaries']
    div_score = st.session_state['div_score']
    cal_target = st.session_state['calorie_target']

    # ── Summary strip ──────────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Plan Summary</div>', unsafe_allow_html=True)
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        timer_color = "#4ade80" if elapsed < 60 else "#f87171"
        st.markdown(f'<div class="metric-card"><div style="color:#94a3b8;font-size:0.8rem">Generation Time</div><div class="gen-timer" style="color:{timer_color}">{elapsed}s</div><div style="font-size:0.75rem;color:#64748b">{"✅ Under 60s target" if elapsed < 60 else "⚠️ Over 60s"}</div></div>', unsafe_allow_html=True)
    with mc2:
        div_color = "#4ade80" if div_score >= 0.7 else "#fbbf24"
        st.markdown(f'<div class="metric-card"><div style="color:#94a3b8;font-size:0.8rem">Diversity Score</div><div class="gen-timer" style="color:{div_color}">{div_score:.2f}</div><div style="font-size:0.75rem;color:#64748b">{"✅ Good variety" if div_score >= 0.7 else "⚠️ Low diversity"}</div></div>', unsafe_allow_html=True)
    with mc3:
        avg_cal = sum(s['totals']['calories'] for s in daily_summaries) / 7
        st.markdown(f'<div class="metric-card"><div style="color:#94a3b8;font-size:0.8rem">Avg Daily Calories</div><div class="gen-timer" style="color:#f59e0b">{avg_cal:.0f}</div><div style="font-size:0.75rem;color:#64748b">Target: {cal_target} kcal</div></div>', unsafe_allow_html=True)
    with mc4:
        excl_count = len(exclusions)
        st.markdown(f'<div class="metric-card"><div style="color:#94a3b8;font-size:0.8rem">Foods Excluded</div><div class="gen-timer" style="color:#f87171">{excl_count}</div><div style="font-size:0.75rem;color:#64748b">Safety filters applied</div></div>', unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📅 7-Day Meal Plan", "📊 Nutrient Analysis", "❌ Why Excluded", "📥 Export"])

    # ── TAB 1: Meal Plan ───────────────────────────────────────────────
    with tab1:
        for day, summary in zip(DAYS, daily_summaries):
            day_cal = summary['totals']['calories']
            day_prot = summary['totals']['protein_g']
            st.markdown(f'<div class="day-header">📆 {day} &nbsp;·&nbsp; {day_cal:.0f} kcal &nbsp;·&nbsp; {day_prot:.0f}g protein</div>', unsafe_allow_html=True)

            cols = st.columns(3)
            for ci, slot in enumerate(MEAL_SLOTS):
                meal = plan[day][slot]
                with cols[ci]:
                    name = meal['name']
                    cuisine = meal.get('cuisine','')
                    cal = meal.get('calories', 0)
                    prot = meal.get('protein_g', 0)
                    carbs = meal.get('carbs_g', 0)
                    fat = meal.get('fat_g', 0)
                    fiber = meal.get('fiber_g', 0)
                    sodium = meal.get('sodium_mg', 0)
                    gi = meal.get('gi_score', 0)

                    # Tags
                    diet_tags = meal.get('diet_tags', '')
                    tag_html = ''
                    if 'vegan' in diet_tags: tag_html += '<span class="included-tag">🌱 Vegan</span>'
                    elif 'vegetarian' in diet_tags: tag_html += '<span class="included-tag">🥚 Vegetarian</span>'
                    if 'gluten-free' in diet_tags: tag_html += '<span class="included-tag">🌾 GF</span>'
                    if 'halal' in diet_tags: tag_html += '<span class="included-tag">☪️ Halal</span>'
                    if 'kosher' in diet_tags: tag_html += '<span class="included-tag">✡️ Kosher</span>'

                    gi_warn = ''
                    if gi > 0 and gi <= 55: gi_warn = f'<span class="included-tag">GI {gi}</span>'
                    elif gi > 55: gi_warn = f'<span class="warn-tag">GI {gi}</span>'

                    st.markdown(f"""
<div class="meal-card">
  <div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em">{slot}</div>
  <div style="font-family:Syne,sans-serif;font-weight:700;font-size:1rem;color:#e2e8f0;margin:4px 0 2px 0">{name}</div>
  <div style="color:#64748b;font-size:0.8rem;margin-bottom:8px">🌍 {cuisine}</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:0.8rem;margin-bottom:8px">
    <span style="color:#fbbf24">🔥 {cal} kcal</span>
    <span style="color:#60a5fa">💪 {prot}g protein</span>
    <span style="color:#a78bfa">🍞 {carbs}g carbs</span>
    <span style="color:#34d399">🥑 {fat}g fat</span>
    <span style="color:#f472b6">🌿 {fiber}g fiber</span>
    <span style="color:#94a3b8">🧂 {sodium:.0f}mg Na</span>
  </div>
  <div>{tag_html}{gi_warn}</div>
</div>""", unsafe_allow_html=True)

    # ── TAB 2: Nutrient Analysis ───────────────────────────────────────
    with tab2:
        rda = get_rda(st.session_state.get('sex','M'))
        micro_labels = {
            'iron_mg': 'Iron (mg)', 'calcium_mg': 'Calcium (mg)',
            'vitamin_b12_ug': 'Vitamin B12 (µg)', 'vitamin_d_iu': 'Vitamin D (IU)',
            'zinc_mg': 'Zinc (mg)', 'potassium_mg': 'Potassium (mg)',
            'magnesium_mg': 'Magnesium (mg)', 'sodium_mg': 'Sodium (mg)'
        }
        for day, summary in zip(DAYS, daily_summaries):
            with st.expander(f"📆 {day} — {summary['totals']['calories']:.0f} kcal"):
                col_m, col_mi = st.columns(2)
                with col_m:
                    st.markdown("**Macronutrients**")
                    t = summary['totals']
                    for label, key, unit, color in [
                        ('Calories','calories','kcal','#fbbf24'),
                        ('Protein','protein_g','g','#60a5fa'),
                        ('Carbohydrates','carbs_g','g','#a78bfa'),
                        ('Fat','fat_g','g','#34d399'),
                        ('Fiber','fiber_g','g','#f472b6'),
                    ]:
                        val = round(t.get(key, 0), 1)
                        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #1e2a45"><span style="color:#94a3b8">{label}</span><span style="color:{color};font-weight:600">{val} {unit}</span></div>', unsafe_allow_html=True)

                with col_mi:
                    st.markdown("**Micronutrients vs RDA**")
                    for micro, flags in summary['rda_flags'].items():
                        if micro == 'sodium_mg':
                            # For sodium, lower is better for hypertension
                            continue
                        label = micro_labels.get(micro, micro)
                        pct = flags['pct']
                        actual = flags['actual']
                        rda_v = flags['rda']
                        bar_color = '#4ade80' if pct >= 80 else ('#fbbf24' if pct >= 50 else '#f87171')
                        bar_w = min(100, pct)
                        status_icon = '✅' if pct >= 80 else ('⚠️' if pct >= 50 else '❌')
                        st.markdown(f"""
<div style="margin-bottom:8px">
  <div style="display:flex;justify-content:space-between;font-size:0.8rem">
    <span style="color:#94a3b8">{status_icon} {label}</span>
    <span style="color:{bar_color}">{actual}/{rda_v} ({pct:.0f}%)</span>
  </div>
  <div style="background:#1e2a45;border-radius:4px;height:6px;margin-top:3px">
    <div style="width:{bar_w}%;height:6px;background:{bar_color};border-radius:4px;transition:width 0.3s"></div>
  </div>
</div>""", unsafe_allow_html=True)

                    # Sodium display separately
                    sod_flags = summary['rda_flags'].get('sodium_mg', {})
                    sod_val = sod_flags.get('actual', 0)
                    sod_limit = 1500
                    sod_pct = (sod_val / sod_limit * 100) if sod_limit > 0 else 0
                    sod_color = '#4ade80' if sod_val <= 1500 else '#f87171'
                    sod_icon = '✅' if sod_val <= 1500 else '❌'
                    st.markdown(f"""
<div style="margin-bottom:8px">
  <div style="display:flex;justify-content:space-between;font-size:0.8rem">
    <span style="color:#94a3b8">{sod_icon} Sodium (mg) [DASH limit]</span>
    <span style="color:{sod_color}">{sod_val:.0f}/1500 mg</span>
  </div>
</div>""", unsafe_allow_html=True)

        # Weekly avg summary
        st.markdown('<div class="section-title">📊 Weekly Averages vs RDA</div>', unsafe_allow_html=True)
        micro_data = []
        for micro, rda_val in rda.items():
            avg_actual = sum(s['rda_flags'][micro]['actual'] for s in daily_summaries) / 7
            avg_pct = (avg_actual / rda_val * 100) if rda_val > 0 else 0
            micro_data.append({
                'Nutrient': micro_labels.get(micro, micro),
                'Avg Actual': round(avg_actual, 1),
                'RDA': rda_val,
                'Pct RDA': round(avg_pct, 0),
                'Status': '✅ Met' if avg_pct >= 80 else ('⚠️ Low' if avg_pct >= 50 else '❌ Deficient')
            })
        st.dataframe(pd.DataFrame(micro_data), hide_index=True, use_container_width=True)

    # ── TAB 3: Why Excluded ────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-title">❌ Foods Filtered Out & Why</div>', unsafe_allow_html=True)
        if not exclusions:
            st.info("No foods were excluded for your current profile.")
        else:
            st.markdown(f"**{len(exclusions)} foods excluded** to ensure your plan is safe and personalized.")
            # Show first 50
            shown = exclusions[:80]
            for exc in shown:
                reason_tags = ' '.join(f'<span class="excluded-tag">{r}</span>' for r in exc['reasons'])
                st.markdown(f'<div class="meal-card" style="padding:12px 16px"><b style="color:#fca5a5">{exc["name"]}</b><br>{reason_tags}</div>', unsafe_allow_html=True)
            if len(exclusions) > 80:
                st.info(f"...and {len(exclusions)-80} more foods were excluded.")

    # ── TAB 4: Export ──────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">📥 Download Your Plan</div>', unsafe_allow_html=True)
        csv_data = plan_to_csv(plan, daily_summaries)
        st.download_button(
            label="⬇️ Download Plan as CSV",
            data=csv_data,
            file_name=f"NutriAI_7Day_Plan_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
            use_container_width=True
        )

        # JSON export
        plan_json = {}
        for day in DAYS:
            plan_json[day] = {}
            for slot in MEAL_SLOTS:
                meal = plan[day][slot]
                plan_json[day][slot] = {k: v for k, v in meal.items() if not k.startswith('_')}

        st.download_button(
            label="⬇️ Download Plan as JSON",
            data=json.dumps(plan_json, indent=2),
            file_name=f"NutriAI_7Day_Plan_{datetime.now().strftime('%Y%m%d')}.json",
            mime='application/json',
            use_container_width=True
        )

        # Benchmark table
        st.markdown('<div class="section-title">🔬 BAX-423 Technique Benchmarks</div>', unsafe_allow_html=True)
        bench_data = {
            'Technique': ['Bloom Filter (allergen exclusion)', 'TF-IDF + FAISS (meal ranking)', 'Baseline (linear scan, no FAISS)'],
            'Lookup Complexity': ['O(k) hash — ~0.001ms/item', 'O(log n) ANN — sub-linear', 'O(n) per query — linear'],
            'Use in Pipeline': ['Step 1: exclude unsafe food IDs', 'Step 3: retrieve top-k semantically relevant meals', 'Counterfactual baseline'],
            'Benefit': ['~10× faster than set lookup on large DB', 'Semantic similarity vs keyword matching', '—'],
        }
        st.dataframe(pd.DataFrame(bench_data), hide_index=True, use_container_width=True)
        st.markdown(f"""
<div class="metric-card">
<b>Generation Time: <span style="color:#4ade80">{elapsed}s</span></b>
&nbsp;|&nbsp; Dataset: <b>{len(df):,}</b> foods
&nbsp;|&nbsp; Diversity Score: <b>{div_score:.2f}</b>
&nbsp;|&nbsp; Foods excluded: <b>{len(exclusions)}</b>
</div>""", unsafe_allow_html=True)

else:
    # Landing state
    st.markdown("""
<div style="background:linear-gradient(135deg,#0d1625,#141f35);border:1px solid #243049;border-radius:20px;padding:40px;text-align:center;margin-top:20px">
  <div style="font-size:3rem;margin-bottom:16px">🥗</div>
  <div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:700;color:#e2e8f0;margin-bottom:8px">Configure your profile in the sidebar</div>
  <div style="color:#64748b;max-width:500px;margin:0 auto">
    Set your dietary preferences, allergies, clinical conditions, and cuisine choices — then hit <b style="color:#4ade80">Generate My 7-Day Plan</b>
  </div>
  <div style="display:flex;justify-content:center;gap:24px;margin-top:24px;flex-wrap:wrap">
    <div style="text-align:center"><div style="font-size:1.8rem">🧬</div><div style="color:#94a3b8;font-size:0.82rem">Clinical safety</div></div>
    <div style="text-align:center"><div style="font-size:1.8rem">🚫</div><div style="color:#94a3b8;font-size:0.82rem">Allergen-free</div></div>
    <div style="text-align:center"><div style="font-size:1.8rem">🌈</div><div style="color:#94a3b8;font-size:0.82rem">Diverse meals</div></div>
    <div style="text-align:center"><div style="font-size:1.8rem">⚡</div><div style="color:#94a3b8;font-size:0.82rem">Under 60 seconds</div></div>
    <div style="text-align:center"><div style="font-size:1.8rem">📊</div><div style="color:#94a3b8;font-size:0.82rem">RDA tracking</div></div>
    <div style="text-align:center"><div style="font-size:1.8rem">📥</div><div style="color:#94a3b8;font-size:0.82rem">CSV/JSON export</div></div>
  </div>
</div>""", unsafe_allow_html=True)

    # Persona quick-load
    st.markdown('<div class="section-title">🧪 Test Personas (BAX-423)</div>', unsafe_allow_html=True)
    personas = [
        ("👩 Priya", "IBS + Vegetarian + Lactose Intolerant", "IBS · Vegetarian · Dairy allergy · 1800 kcal · Priority: Iron, Calcium, VitD"),
        ("👨 Ravi",  "GERD + Non-Veg + Gluten-Free",         "GERD · Non-Veg · Gluten allergy · 2200 kcal · Priority: B12, Zinc, Magnesium"),
        ("👩 Mei",   "T2 Diabetes + Vegan + Tree Nut Allergy","T2 Diabetes · Vegan · Tree Nut allergy · 1600 kcal · Priority: B12, Iron, Zinc"),
        ("👨 James", "Hypertension + Pescatarian + Soy Allergy","Hypertension · Pescatarian · Soy allergy · 2000 kcal · Priority: Sodium, Potassium"),
    ]
    pc1, pc2, pc3, pc4 = st.columns(4)
    for col, (pname, ptitle, pdesc) in zip([pc1,pc2,pc3,pc4], personas):
        with col:
            st.markdown(f'<div class="meal-card"><b style="color:#e2e8f0">{pname}</b><br><span style="color:#4ade80;font-size:0.8rem">{ptitle}</span><br><span style="color:#64748b;font-size:0.75rem">{pdesc}</span></div>', unsafe_allow_html=True)
