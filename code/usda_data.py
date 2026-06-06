"""
USDA FoodData Central integration + static clinical databases.
All static data sourced from:
- Monash University Low-FODMAP app/list (monashfodmap.com)
- NIH DRI tables (ncbi.nlm.nih.gov/books/NBK56068)
- International GI Database (glycemicindex.com / Atkinson et al. 2008)
- DASH diet NHLBI guidelines (nhlbi.nih.gov/education/dash-eating-plan)
"""

import requests
import pandas as pd
import numpy as np
import os, json, time

USDA_API_KEY = "0cgLd6SqV4l6qf0Xudmfyi71vnGglJMwkZaYq1ei"  # FoodData Central API key
USDA_BASE    = "https://api.nal.usda.gov/fdc/v1"

# ─────────────────────────────────────────────────────────
# MONASH UNIVERSITY LOW-FODMAP DATABASE
# Source: Monash University FODMAP Diet App & published literature
# Traffic-light system: RED=high FODMAP (avoid), YELLOW=moderate, GREEN=safe
# ─────────────────────────────────────────────────────────
MONASH_FODMAP = {
    # HIGH FODMAP — AVOID for IBS
    "high": [
        "garlic", "onion", "shallot", "leek", "spring onion",
        "wheat", "rye", "barley", "wheat bread", "pasta", "couscous",
        "apple", "pear", "mango", "watermelon", "cherry", "peach", "plum",
        "milk", "yogurt", "soft cheese", "ice cream", "custard",
        "legumes", "kidney beans", "chickpeas", "lentils",  # in large amounts
        "cauliflower", "mushroom", "artichoke", "asparagus", "beetroot",
        "cashews", "pistachios",
        "honey", "high fructose corn syrup", "fructose",
        "inulin", "chicory root",
    ],
    # MODERATE — limit portion
    "moderate": [
        "avocado", "sweet potato", "corn", "oats",
        "almonds",  # limit to 10
        "butternut squash", "cabbage", "broccoli",  # small portions ok
    ],
    # LOW FODMAP — SAFE for IBS
    "safe": [
        "rice", "quinoa", "oats", "potato", "carrot", "zucchini",
        "spinach", "kale", "tomato", "cucumber", "lettuce",
        "banana", "blueberry", "strawberry", "orange", "grape", "kiwi",
        "chicken", "fish", "beef", "pork", "eggs", "tofu",  # firm tofu ok
        "cheddar", "brie", "feta",  # hard cheeses ok
        "almond milk", "oat milk", "lactose-free milk",
        "walnuts", "macadamia", "peanuts", "pecans",
        "olive oil", "maple syrup",
        "eggplant", "capsicum", "green beans", "pumpkin",
    ]
}

def is_high_fodmap(food_name: str) -> bool:
    """Check if food is high-FODMAP using Monash list."""
    name_lower = food_name.lower()
    for term in MONASH_FODMAP["high"]:
        if term in name_lower:
            return True
    return False

def get_fodmap_reason(food_name: str) -> str:
    name_lower = food_name.lower()
    for term in MONASH_FODMAP["high"]:
        if term in name_lower:
            return f"High-FODMAP ingredient: '{term}' (Monash University list) — triggers IBS symptoms"
    return ""

# ─────────────────────────────────────────────────────────
# GLYCAEMIC INDEX DATABASE
# Source: Atkinson et al. (2008) Diabetes Care + glycemicindex.com
# GI categories: Low <55, Medium 55-69, High ≥70
# ─────────────────────────────────────────────────────────
GI_DATABASE = {
    # Grains & Starches
    "white rice": 73, "brown rice": 50, "basmati rice": 57,
    "white bread": 75, "whole wheat bread": 69, "sourdough": 54,
    "oats": 55, "rolled oats": 57, "instant oats": 79,
    "quinoa": 53, "barley": 28, "pasta": 49, "white pasta": 58,
    "potato": 78, "sweet potato": 63, "yam": 37,
    "corn": 52, "popcorn": 55, "rice cakes": 82, "pretzels": 83,
    "cornflakes": 81, "bran flakes": 74, "muesli": 57,
    # Legumes (all low GI)
    "lentils": 32, "chickpeas": 28, "kidney beans": 24,
    "black beans": 30, "soybeans": 16, "tofu": 15,
    "hummus": 6, "edamame": 18,
    # Fruits
    "apple": 36, "banana": 51, "orange": 43, "mango": 51,
    "watermelon": 76, "grapes": 59, "pineapple": 59,
    "strawberry": 40, "blueberry": 40, "cherry": 22,
    "pear": 38, "peach": 42, "plum": 39,
    # Dairy
    "milk": 39, "yogurt": 41, "ice cream": 57,
    # Vegetables (most near 0 — negligible carbs)
    "carrot": 39, "broccoli": 15, "spinach": 15, "kale": 15,
    "tomato": 15, "cucumber": 15, "lettuce": 15, "zucchini": 15,
    # Proteins (no GI — no carbs)
    "chicken": 0, "fish": 0, "beef": 0, "eggs": 0, "salmon": 0,
    "tuna": 0, "shrimp": 0, "tofu": 15,
    # Snacks
    "chocolate": 40, "chips": 56, "crackers": 67,
}

def get_gi_score(food_name: str) -> int:
    """Look up GI score from database."""
    name_lower = food_name.lower()
    for food, gi in GI_DATABASE.items():
        if food in name_lower:
            return gi
    # Default by category heuristic
    if any(x in name_lower for x in ["rice", "bread", "pasta", "potato"]):
        return 60  # medium default
    if any(x in name_lower for x in ["bean", "lentil", "legume", "dal", "dhal"]):
        return 30  # low GI
    if any(x in name_lower for x in ["chicken", "fish", "beef", "egg", "meat", "salmon"]):
        return 0
    return 45  # default moderate

# ─────────────────────────────────────────────────────────
# NIH DIETARY REFERENCE INTAKES (RDA)
# Source: NIH DRI Tables — ncbi.nlm.nih.gov/books/NBK56068
# Values per day for adults 19-50
# ─────────────────────────────────────────────────────────
NIH_RDA = {
    # (male, female) per day
    "iron_mg":        {"M": {"19-50": 8,  "51+": 8},  "F": {"19-50": 18, "51+": 8}},
    "calcium_mg":     {"M": {"19-50": 1000,"51+": 1000},"F": {"19-50": 1000,"51+": 1200}},
    "vitamin_b12_ug": {"M": {"19-50": 2.4,"51+": 2.4}, "F": {"19-50": 2.4,"51+": 2.4}},
    "vitamin_d_iu":   {"M": {"19-50": 600,"51+": 800}, "F": {"19-50": 600,"51+": 800}},
    "zinc_mg":        {"M": {"19-50": 11, "51+": 11},  "F": {"19-50": 8,  "51+": 8}},
    "potassium_mg":   {"M": {"19-50": 3400,"51+": 3400},"F": {"19-50": 2600,"51+": 2600}},
    "magnesium_mg":   {"M": {"19-50": 400,"51+": 420}, "F": {"19-50": 310,"51+": 320}},
    "sodium_mg":      {"M": {"19-50": 2300,"51+": 2300},"F": {"19-50": 2300,"51+": 2300}},
}

def get_rda(sex: str = "M", age: int = 30) -> dict:
    """Get age/sex adjusted RDA from NIH tables."""
    age_key = "19-50" if age <= 50 else "51+"
    return {
        nutrient: values[sex][age_key]
        for nutrient, values in NIH_RDA.items()
    }

# ─────────────────────────────────────────────────────────
# DASH DIET GUIDELINES
# Source: NHLBI — nhlbi.nih.gov/education/dash-eating-plan
# ─────────────────────────────────────────────────────────
DASH_GUIDELINES = {
    "sodium_max_mg": 1500,       # strict DASH
    "sodium_standard_mg": 2300,  # standard limit
    "potassium_min_mg": 4700,    # DASH target
    "magnesium_min_mg": 500,     # DASH target
    "saturated_fat_max_pct": 6,  # % of total calories
    "total_fat_max_pct": 27,
    "fiber_min_g": 30,
    "recommended_foods": [
        "vegetables", "fruits", "whole grains", "lean protein",
        "low-fat dairy", "nuts", "seeds", "legumes", "fish"
    ],
    "limit_foods": [
        "red meat", "sweets", "sugar-sweetened beverages",
        "sodium", "saturated fat", "processed foods"
    ]
}

def get_dash_sodium_limit(hypertension: bool = False) -> int:
    return DASH_GUIDELINES["sodium_max_mg"] if hypertension else DASH_GUIDELINES["sodium_standard_mg"]

# ─────────────────────────────────────────────────────────
# GERD TRIGGER LIST
# Source: American College of Gastroenterology clinical guidelines
# ─────────────────────────────────────────────────────────
GERD_TRIGGERS = {
    "high": [
        "tomato", "tomato sauce", "ketchup", "marinara",
        "citrus", "lemon", "lime", "orange juice", "grapefruit",
        "coffee", "espresso", "caffeine",
        "chocolate", "cocoa",
        "spicy", "chili", "hot sauce", "jalapeño", "cayenne",
        "fried", "deep fried", "french fries",
        "peppermint", "spearmint",
        "alcohol", "wine", "beer",
        "vinegar", "balsamic",
        "garlic",  # also GERD trigger
        "onion",
        "fatty meat", "high fat",
    ],
    "safe": [
        "oatmeal", "ginger", "banana", "melon", "fennel",
        "chicken", "fish", "seafood", "turkey",
        "root vegetables", "green vegetables", "lettuce",
        "whole grains", "rice", "bread",
        "low-fat dairy",
    ]
}

def is_gerd_trigger(food_name: str) -> tuple:
    """Returns (is_trigger: bool, reason: str)"""
    name_lower = food_name.lower()
    for term in GERD_TRIGGERS["high"]:
        if term in name_lower:
            return True, f"GERD trigger: '{term}' (ACG guidelines) — worsens acid reflux"
    return False, ""

# ─────────────────────────────────────────────────────────
# USDA FoodData Central API
# ─────────────────────────────────────────────────────────
NUTRIENT_MAP = {
    "Energy": "calories",
    "Protein": "protein_g",
    "Total lipid (fat)": "fat_g",
    "Carbohydrate, by difference": "carbs_g",
    "Fiber, total dietary": "fiber_g",
    "Iron, Fe": "iron_mg",
    "Calcium, Ca": "calcium_mg",
    "Vitamin B-12": "vitamin_b12_ug",
    "Vitamin D (D2 + D3)": "vitamin_d_iu",
    "Zinc, Zn": "zinc_mg",
    "Potassium, K": "potassium_mg",
    "Magnesium, Mg": "magnesium_mg",
    "Sodium, Na": "sodium_mg",
}

# ─────────────────────────────────────────────────────────
# CROSS-CONTAMINATION RULES
# Source: FDA Food Allergen Labeling and Consumer Protection Act (FALCPA 2004)
# Foods that carry cross-contamination risk for an allergen even when
# that allergen is not a primary listed ingredient.
# ─────────────────────────────────────────────────────────
CROSS_CONTAM_RULES = {
    "Gluten": {
        "risk_foods": ["oats", "oatmeal", "overnight oats", "granola", "muesli",
                       "rolled oats", "oat milk", "bran", "cornflakes", "cereal",
                       "rice cakes", "pretzels", "popcorn"],
        "reason": "Oats and cereals frequently processed on shared wheat equipment (FDA FALCPA)"
    },
    "Tree Nuts": {
        "risk_foods": ["chocolate", "energy bar", "trail mix", "granola", "muesli",
                       "cookie", "brownie", "cake", "muffin", "ice cream"],
        "reason": "Shared processing facilities common in confectionery/snack categories (FDA FALCPA)"
    },
    "Peanuts": {
        "risk_foods": ["chocolate", "energy bar", "trail mix", "granola", "cookie",
                       "brownie", "cake", "satay", "asian sauce"],
        "reason": "Shared processing with peanuts common in confectionery and Asian condiments (FDA FALCPA)"
    },
    "Dairy": {
        "risk_foods": ["dark chocolate", "margarine", "non-dairy creamer",
                       "tuna canned", "bread", "crackers"],
        "reason": "Dairy traces common in processed foods due to shared lines (FDA FALCPA)"
    },
    "Eggs": {
        "risk_foods": ["pasta", "bread", "noodle", "ramen", "udon", "cake", "muffin"],
        "reason": "Egg cross-contamination common in pasta and bakery products (FDA FALCPA)"
    },
}

def get_cross_contam_warnings(food_name: str, allergens_set: set) -> list:
    """
    Return cross-contamination warning strings for a food given the
    user's declared allergen set. Uses FDA FALCPA-based rules.
    """
    warnings = []
    name_lower = food_name.lower()
    for allergen in allergens_set:
        rule = CROSS_CONTAM_RULES.get(allergen)
        if not rule:
            continue
        for risk_word in rule["risk_foods"]:
            if risk_word in name_lower:
                warnings.append(
                    f"⚠️ Cross-contamination risk ({allergen}): "
                    f"'{risk_word}' — {rule['reason']}"
                )
                break  # one warning per allergen per food
    return warnings
    
def fetch_usda_food(food_name: str, api_key: str = USDA_API_KEY) -> dict:
    """Fetch nutrient data from USDA FoodData Central API."""
    try:
        url = f"{USDA_BASE}/foods/search"
        params = {
            "query": food_name,
            "api_key": api_key,
            "pageSize": 1,
            "dataType": "Foundation,SR Legacy",
        }
        r = requests.get(url, params=params, timeout=8)
        if r.status_code != 200:
            return {}
        data = r.json()
        foods = data.get("foods", [])
        if not foods:
            return {}
        food = foods[0]
        nutrients = {}
        for n in food.get("foodNutrients", []):
            mapped = NUTRIENT_MAP.get(n.get("nutrientName", ""))
            if mapped:
                nutrients[mapped] = round(float(n.get("value", 0)), 2)
        nutrients["usda_fdcId"] = food.get("fdcId", "")
        nutrients["usda_description"] = food.get("description", food_name)
        return nutrients
    except Exception:
        return {}

def enrich_with_usda(df: pd.DataFrame, api_key: str = USDA_API_KEY,
                     max_items: int = 100, cache_path: str = None) -> pd.DataFrame:
    """
    Enrich food database with live USDA data for top items.
    Uses cache to avoid re-fetching.
    """
    cache = {}
    if cache_path and os.path.exists(cache_path):
        with open(cache_path) as f:
            cache = json.load(f)

    enriched = 0
    for idx, row in df.head(max_items).iterrows():
        name = row["name"]
        if name in cache:
            usda = cache[name]
        else:
            usda = fetch_usda_food(name, api_key)
            cache[name] = usda
            time.sleep(0.1)  # rate limit

        if usda:
            for col in ["calories","protein_g","fat_g","carbs_g","fiber_g",
                        "iron_mg","calcium_mg","vitamin_b12_ug","vitamin_d_iu",
                        "zinc_mg","potassium_mg","magnesium_mg","sodium_mg"]:
                if col in usda and usda[col] > 0:
                    df.at[idx, col] = usda[col]
            enriched += 1

    if cache_path:
        with open(cache_path, "w") as f:
            json.dump(cache, f)

    return df, enriched
