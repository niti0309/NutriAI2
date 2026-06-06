"""
fetch_usda_data.py — NutriAI food database builder
Run ONCE locally to pull real nutrient data from USDA FoodData Central.

Usage:
    cd /Users/nitipatel/Downloads/nutriai/data
    python fetch_usda_data.py

Requires: pip install requests pandas
Produces: food_database.csv  (5,000+ USDA foods — curated dishes + bulk catalog)
Takes:    ~5-15 minutes (rate-limited to respect USDA 1,000 req/hour cap)
"""

import requests, pandas as pd, time, os, copy, random

API_KEY  = "0cgLd6SqV4l6qf0Xudmfyi71vnGglJMwkZaYq1ei"
BASE_URL = "https://api.nal.usda.gov/fdc/v1"

# ─────────────────────────────────────────────────────────────────────────────
# 400+ DISTINCT DISHES
# Format: (usda_search_query, display_name, cuisine, diet_tags, allergens, categories)
#
# diet_tags   — pipe-separated from: vegan, vegetarian, pescatarian,
#               non-vegetarian, gluten-free, halal, kosher
# allergens   — pipe-separated from: dairy, eggs, gluten, soy, fish,
#               shellfish, tree nuts, peanuts, sesame, none
# categories  — pipe-separated from: breakfast, grain, legume, protein,
#               seafood, vegetable, salad, soup, snack, main, side, dessert, light
# ─────────────────────────────────────────────────────────────────────────────
FOOD_QUERIES = [

    # ══════════════════════════════════════════════════════
    # INDIAN — Breakfast
    # ══════════════════════════════════════════════════════
    ("idli steamed rice cake",        "Idli Sambar",             "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|breakfast"),
    ("dosa fermented crepe",          "Masala Dosa",             "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|breakfast"),
    ("upma semolina",                 "Upma",                    "Indian",        "vegan|vegetarian|halal|kosher",              "gluten",            "grain|breakfast"),
    ("poha flattened rice",           "Poha",                    "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|breakfast"),
    ("besan chickpea flour pancake",  "Besan Chilla",            "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|breakfast"),
    ("paratha whole wheat flatbread", "Aloo Paratha",            "Indian",        "vegetarian|halal|kosher",                    "gluten|dairy",      "grain|breakfast"),
    ("oats porridge",                 "Oatmeal with Banana",     "Indian",        "vegan|vegetarian|halal|kosher",              "gluten",            "grain|breakfast"),
    ("rava semolina pancake",         "Rava Uttapam",            "Indian",        "vegetarian|halal|kosher",                    "gluten|dairy",      "grain|breakfast"),
    ("dhokla steamed chickpea",       "Dhokla",                  "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|snack"),
    ("egg omelette",                  "Masala Omelette",         "Indian",        "vegetarian|gluten-free|halal|kosher",        "eggs",              "protein|breakfast"),
    ("vermicelli upma",               "Seviyan Upma",            "Indian",        "vegan|vegetarian|halal|kosher",              "gluten",            "grain|breakfast"),
    ("sprouts mung bean salad",       "Sprouts Chaat",           "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|breakfast|snack"),

    # ══════════════════════════════════════════════════════
    # INDIAN — Mains & Curries
    # ══════════════════════════════════════════════════════
    ("red lentils cooked",            "Masoor Dal",              "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("yellow moong dal cooked",       "Moong Dal Tadka",         "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|soup"),
    ("toor dal pigeon pea",           "Toor Dal",                "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("kidney beans cooked",           "Rajma Chawal",            "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("chickpeas cooked",              "Chole Bhature",           "Indian",        "vegan|vegetarian|halal|kosher",              "gluten",            "legume|main"),
    ("chickpea chana masala",         "Chana Masala",            "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("paneer cottage cheese",         "Paneer Tikka Masala",     "Indian",        "vegetarian|gluten-free|kosher",              "dairy",             "protein|main"),
    ("paneer palak spinach",          "Saag Paneer",             "Indian",        "vegetarian|gluten-free|kosher",              "dairy",             "protein|main"),
    ("paneer matar peas",             "Matar Paneer",            "Indian",        "vegetarian|gluten-free|kosher",              "dairy",             "protein|main"),
    ("tofu firm",                     "Tofu Palak",              "Indian",        "vegan|vegetarian|gluten-free",               "soy",               "protein|main"),
    ("cauliflower potato curry",      "Aloo Gobi",               "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|main"),
    ("eggplant baingan bharta",       "Baingan Bharta",          "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|main"),
    ("mixed vegetable curry",         "Sabzi Medley",            "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|main"),
    ("spinach lentil dal",            "Palak Dal",               "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("chicken tikka masala",          "Chicken Tikka Masala",    "Indian",        "non-vegetarian|gluten-free|halal",           "dairy",             "protein|main"),
    ("chicken breast tandoori",       "Tandoori Chicken",        "Indian",        "non-vegetarian|gluten-free|halal",           "dairy",             "protein|main"),
    ("chicken korma",                 "Chicken Korma",           "Indian",        "non-vegetarian|gluten-free|halal",           "dairy|tree nuts",   "protein|main"),
    ("lamb mutton curry",             "Mutton Curry",            "Indian",        "non-vegetarian|gluten-free|halal",           "none",              "protein|main"),
    ("fish curry coconut",            "Goan Fish Curry",         "Indian",        "pescatarian|non-vegetarian|gluten-free|halal","fish",             "seafood|main"),
    ("prawn shrimp masala",           "Prawn Masala",            "Indian",        "pescatarian|non-vegetarian|gluten-free|halal","shellfish",        "seafood|main"),
    ("basmati rice cooked",           "Vegetable Biryani",       "Indian",        "vegan|vegetarian|halal|kosher",              "none",              "grain|main"),
    ("chicken biryani rice",          "Chicken Biryani",         "Indian",        "non-vegetarian|halal",                       "none",              "grain|main"),
    ("lamb biryani",                  "Lamb Biryani",            "Indian",        "non-vegetarian|halal",                       "none",              "grain|main"),
    ("sambar lentil vegetable stew",  "Sambar",                  "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|soup"),
    ("rasam tamarind soup",           "Rasam",                   "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "soup|light"),
    ("pav bhaji mixed vegetable",     "Pav Bhaji",               "Indian",        "vegetarian|halal|kosher",                    "gluten|dairy",      "vegetable|main"),
    ("curd rice yogurt",              "Curd Rice",               "Indian",        "vegetarian|gluten-free|kosher",              "dairy",             "grain|main"),
    ("khichdi lentil rice",           "Khichdi",                 "Indian",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("haleem wheat lentil meat",      "Dal Makhani",             "Indian",        "vegetarian|gluten-free|kosher",              "dairy",             "legume|main"),

    # ══════════════════════════════════════════════════════
    # AMERICAN — Breakfast
    # ══════════════════════════════════════════════════════
    ("rolled oats cooked",            "Classic Oatmeal",         "American",      "vegan|vegetarian|halal|kosher",              "gluten",            "grain|breakfast"),
    ("overnight oats",                "Overnight Oats",          "American",      "vegetarian|halal|kosher",                    "gluten|dairy",      "grain|breakfast"),
    ("egg whites scrambled",          "Egg White Scramble",      "American",      "vegetarian|gluten-free|halal|kosher",        "eggs",              "protein|breakfast"),
    ("whole eggs fried",              "Eggs and Avocado Toast",  "American",      "vegetarian|halal|kosher",                    "eggs|gluten",       "protein|breakfast"),
    ("greek yogurt plain",            "Greek Yogurt Parfait",    "American",      "vegetarian|gluten-free|kosher",              "dairy",             "dairy|breakfast"),
    ("banana smoothie",               "Banana Protein Smoothie", "American",      "vegetarian|gluten-free|halal|kosher",        "dairy",             "fruit|breakfast"),
    ("chia seeds",                    "Chia Pudding",            "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|breakfast"),
    ("whole wheat pancakes",          "Whole Wheat Pancakes",    "American",      "vegetarian|halal|kosher",                    "gluten|eggs|dairy", "grain|breakfast"),
    ("blueberry muffin bran",         "Bran Muffin",             "American",      "vegetarian|halal|kosher",                    "gluten|eggs|dairy", "grain|breakfast"),
    ("granola oat clusters",          "Granola Bowl",            "American",      "vegan|vegetarian|halal|kosher",              "gluten|tree nuts",  "grain|breakfast"),
    ("cottage cheese",                "Cottage Cheese Bowl",     "American",      "vegetarian|gluten-free|kosher",              "dairy",             "dairy|breakfast|protein"),
    ("avocado toast sourdough",       "Avocado Toast",           "American",      "vegan|vegetarian|halal|kosher",              "gluten",            "vegetable|breakfast"),
    ("smoothie bowl acai",            "Acai Bowl",               "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "fruit|breakfast"),
    ("turkey sausage breakfast",      "Turkey Sausage & Eggs",   "American",      "non-vegetarian|gluten-free|halal|kosher",    "eggs",              "protein|breakfast"),

    # ══════════════════════════════════════════════════════
    # AMERICAN — Mains
    # ══════════════════════════════════════════════════════
    ("chicken breast grilled",        "Grilled Chicken Salad",   "American",      "non-vegetarian|gluten-free|halal|kosher",    "none",              "protein|main|salad"),
    ("turkey breast roasted",         "Turkey & Sweet Potato",   "American",      "non-vegetarian|gluten-free|halal|kosher",    "none",              "protein|main"),
    ("ground turkey lean",            "Turkey Meatballs",        "American",      "non-vegetarian|halal|kosher",                "gluten|eggs",       "protein|main"),
    ("salmon fillet baked",           "Baked Salmon",            "American",      "pescatarian|non-vegetarian|gluten-free|halal|kosher","fish",      "seafood|main"),
    ("tuna canned water",             "Tuna Salad Wrap",         "American",      "pescatarian|non-vegetarian|halal|kosher",    "fish|gluten",       "seafood|main"),
    ("sweet potato baked",            "Stuffed Sweet Potato",    "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|main"),
    ("black beans cooked",            "Black Bean Burrito Bowl", "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("quinoa cooked",                 "Quinoa Power Bowl",       "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|main"),
    ("brown rice cooked",             "Brown Rice Buddha Bowl",  "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|main"),
    ("lentils green cooked",          "Lentil Tacos",            "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("black bean burger patty",       "Black Bean Burger",       "American",      "vegan|vegetarian|halal",                     "gluten|soy",        "legume|main"),
    ("chicken soup noodle",           "Chicken Noodle Soup",     "American",      "non-vegetarian|halal|kosher",                "gluten",            "protein|soup"),
    ("vegetable beef stew",           "Beef & Veggie Stew",      "American",      "non-vegetarian|gluten-free|halal|kosher",    "none",              "protein|soup"),
    ("caesar salad romaine",          "Caesar Salad",            "American",      "vegetarian|gluten-free",                     "eggs|dairy|fish",   "vegetable|salad"),
    ("cobb salad chicken",            "Cobb Salad",              "American",      "non-vegetarian|gluten-free",                 "eggs|dairy",        "protein|salad"),
    ("spinach salad strawberry",      "Spinach Strawberry Salad","American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|salad"),
    ("shrimp stir fry vegetables",    "Shrimp Stir Fry",         "American",      "pescatarian|non-vegetarian|gluten-free|halal","shellfish",        "seafood|main"),
    ("tilapia fillet baked",          "Lemon Herb Tilapia",      "American",      "pescatarian|non-vegetarian|gluten-free|halal|kosher","fish",      "seafood|main"),
    ("beef sirloin lean grilled",     "Sirloin & Broccoli",      "American",      "non-vegetarian|gluten-free|halal|kosher",    "none",              "protein|main"),
    ("pasta whole wheat marinara",    "Whole Wheat Pasta",       "American",      "vegan|vegetarian|halal|kosher",              "gluten",            "grain|main"),

    # ══════════════════════════════════════════════════════
    # MEDITERRANEAN
    # ══════════════════════════════════════════════════════
    ("hummus chickpea spread",        "Hummus & Veggie Plate",   "Mediterranean", "vegan|vegetarian|gluten-free|halal|kosher",  "sesame",            "legume|snack|light"),
    ("falafel chickpea patty",        "Falafel Wrap",            "Mediterranean", "vegan|vegetarian|halal|kosher",              "gluten|sesame",     "legume|main"),
    ("lentil red soup",               "Red Lentil Soup",         "Mediterranean", "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|soup"),
    ("greek salad cucumber tomato",   "Greek Salad",             "Mediterranean", "vegetarian|gluten-free|halal|kosher",        "dairy",             "vegetable|salad"),
    ("chicken souvlaki grilled",      "Chicken Souvlaki",        "Mediterranean", "non-vegetarian|gluten-free|halal",           "none",              "protein|main"),
    ("lamb kebab grilled",            "Lamb Kebab",              "Mediterranean", "non-vegetarian|halal",                       "none",              "protein|main"),
    ("stuffed grape leaves dolma",    "Stuffed Grape Leaves",    "Mediterranean", "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|main|light"),
    ("tabbouleh bulgur parsley",      "Tabbouleh",               "Mediterranean", "vegan|vegetarian|halal|kosher",              "gluten",            "grain|salad"),
    ("shakshuka eggs tomato sauce",   "Shakshuka",               "Mediterranean", "vegetarian|gluten-free|halal|kosher",        "eggs",              "protein|breakfast"),
    ("halloumi cheese grilled",       "Grilled Halloumi",        "Mediterranean", "vegetarian|gluten-free|kosher",              "dairy",             "protein|main"),
    ("sea bass grilled lemon",        "Grilled Sea Bass",        "Mediterranean", "pescatarian|non-vegetarian|gluten-free|halal|kosher","fish",      "seafood|main"),
    ("octopus grilled",               "Grilled Octopus",         "Mediterranean", "pescatarian|non-vegetarian|gluten-free|halal","shellfish",        "seafood|main"),
    ("fattoush salad pita",           "Fattoush Salad",          "Mediterranean", "vegan|vegetarian|halal|kosher",              "gluten",            "vegetable|salad"),
    ("baba ganoush eggplant",         "Baba Ganoush",            "Mediterranean", "vegan|vegetarian|gluten-free|halal|kosher",  "sesame",            "vegetable|snack"),
    ("tzatziki yogurt cucumber",      "Tzatziki Bowl",           "Mediterranean", "vegetarian|gluten-free|kosher",              "dairy",             "dairy|side|light"),
    ("pita bread whole wheat",        "Whole Wheat Pita",        "Mediterranean", "vegan|vegetarian|halal|kosher",              "gluten",            "grain|side"),
    ("moussaka eggplant lamb",        "Moussaka",                "Mediterranean", "non-vegetarian|halal",                       "gluten|dairy|eggs", "protein|main"),
    ("spanakopita spinach feta",      "Spanakopita",             "Mediterranean", "vegetarian|kosher",                          "gluten|dairy|eggs", "vegetable|main"),
    ("caprese salad mozzarella",      "Caprese Salad",           "Mediterranean", "vegetarian|gluten-free|kosher",              "dairy",             "vegetable|salad"),
    ("panzanella bread tomato salad", "Panzanella",              "Mediterranean", "vegan|vegetarian|halal|kosher",              "gluten",            "vegetable|salad"),

    # ══════════════════════════════════════════════════════
    # ITALIAN
    # ══════════════════════════════════════════════════════
    ("pasta whole wheat cooked",      "Pasta Primavera",         "Italian",       "vegan|vegetarian|halal",                     "gluten",            "grain|main"),
    ("pasta marinara tomato sauce",   "Spaghetti Marinara",      "Italian",       "vegan|vegetarian|halal|kosher",              "gluten",            "grain|main"),
    ("pasta pesto basil",             "Pasta al Pesto",          "Italian",       "vegetarian|halal|kosher",                    "gluten|dairy|tree nuts","grain|main"),
    ("risotto arborio rice vegetable","Vegetable Risotto",       "Italian",       "vegetarian|gluten-free|kosher",              "dairy",             "grain|main"),
    ("risotto mushroom",              "Mushroom Risotto",        "Italian",       "vegetarian|gluten-free|kosher",              "dairy",             "grain|main"),
    ("minestrone soup vegetable",     "Minestrone Soup",         "Italian",       "vegan|vegetarian|halal|kosher",              "gluten",            "vegetable|soup"),
    ("pizza margherita",              "Margherita Pizza",        "Italian",       "vegetarian|halal|kosher",                    "gluten|dairy",      "grain|main"),
    ("pizza vegetables",              "Veggie Pizza",            "Italian",       "vegetarian|halal|kosher",                    "gluten|dairy",      "grain|main"),
    ("bruschetta tomato bread",       "Bruschetta",              "Italian",       "vegan|vegetarian|halal|kosher",              "gluten",            "vegetable|snack|light"),
    ("zucchini noodles raw",          "Zucchini Noodles",        "Italian",       "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|main"),
    ("chicken piccata lemon caper",   "Chicken Piccata",         "Italian",       "non-vegetarian|halal|kosher",                "gluten|eggs",       "protein|main"),
    ("salmon pasta lemon cream",      "Salmon Pasta",            "Italian",       "pescatarian|non-vegetarian|halal|kosher",    "fish|gluten|dairy", "seafood|main"),
    ("lentil bolognese pasta",        "Lentil Bolognese",        "Italian",       "vegan|vegetarian|halal|kosher",              "gluten",            "legume|main"),
    ("frittata egg vegetable",        "Vegetable Frittata",      "Italian",       "vegetarian|gluten-free|kosher",              "eggs|dairy",        "protein|breakfast|main"),
    ("polenta corn grilled",          "Polenta & Ragu",          "Italian",       "vegetarian|gluten-free|kosher",              "dairy",             "grain|main"),
    ("ribollita tuscan bean soup",    "Ribollita",               "Italian",       "vegan|vegetarian|halal|kosher",              "gluten",            "legume|soup"),
    ("arancini rice balls",           "Arancini",                "Italian",       "vegetarian|halal|kosher",                    "gluten|eggs|dairy", "grain|snack"),

    # ══════════════════════════════════════════════════════
    # JAPANESE
    # ══════════════════════════════════════════════════════
    ("miso soup tofu seaweed",        "Miso Soup",               "Japanese",      "vegan|vegetarian|gluten-free",               "soy",               "soup|light"),
    ("edamame steamed",               "Edamame",                 "Japanese",      "vegan|vegetarian|gluten-free|halal|kosher",  "soy",               "legume|snack"),
    ("sushi salmon roll",             "Salmon Sushi Roll",       "Japanese",      "pescatarian|non-vegetarian|gluten-free",     "fish|soy",          "seafood|main"),
    ("sushi tuna roll",               "Tuna Sushi Roll",         "Japanese",      "pescatarian|non-vegetarian|gluten-free",     "fish|soy",          "seafood|main"),
    ("sushi vegetable roll",          "Veggie Sushi Roll",       "Japanese",      "vegan|vegetarian|gluten-free",               "soy|sesame",        "grain|main"),
    ("ramen noodle soup chicken",     "Chicken Ramen",           "Japanese",      "non-vegetarian|halal",                       "gluten|eggs|soy",   "grain|soup"),
    ("udon noodle soup vegetable",    "Vegetable Udon",          "Japanese",      "vegan|vegetarian|halal",                     "gluten|soy",        "grain|soup"),
    ("soba noodles cold",             "Cold Soba",               "Japanese",      "vegan|vegetarian|halal|kosher",              "gluten",            "grain|main"),
    ("donburi chicken egg rice",      "Oyakodon",                "Japanese",      "non-vegetarian|gluten-free",                 "eggs|soy",          "grain|main"),
    ("tofu agedashi fried",           "Agedashi Tofu",           "Japanese",      "vegan|vegetarian",                           "gluten|soy",        "protein|main"),
    ("teriyaki salmon",               "Teriyaki Salmon",         "Japanese",      "pescatarian|non-vegetarian|gluten-free",     "fish|soy",          "seafood|main"),
    ("teriyaki chicken",              "Teriyaki Chicken",        "Japanese",      "non-vegetarian",                             "gluten|soy",        "protein|main"),
    ("katsu chicken breaded",         "Chicken Katsu",           "Japanese",      "non-vegetarian|halal",                       "gluten|eggs",       "protein|main"),
    ("onigiri rice ball",             "Onigiri",                 "Japanese",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|snack|light"),
    ("sunomono cucumber salad",       "Sunomono Salad",          "Japanese",      "vegan|vegetarian|gluten-free",               "soy|sesame",        "vegetable|salad"),
    ("gyoza pork dumplings",          "Gyoza",                   "Japanese",      "non-vegetarian",                             "gluten|pork",       "protein|snack"),
    ("gyoza vegetable dumplings",     "Veggie Gyoza",            "Japanese",      "vegan|vegetarian",                           "gluten|soy",        "vegetable|snack"),
    ("yakisoba stir fry noodles",     "Yakisoba",                "Japanese",      "non-vegetarian",                             "gluten|soy",        "grain|main"),
    ("chawanmushi steamed egg",       "Chawanmushi",             "Japanese",      "vegetarian|gluten-free",                     "eggs|soy",          "protein|light"),
    ("ochazuke rice green tea",       "Ochazuke",                "Japanese",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|light"),

    # ══════════════════════════════════════════════════════
    # CHINESE
    # ══════════════════════════════════════════════════════
    ("congee rice porridge",          "Congee",                  "Chinese",       "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|breakfast"),
    ("dim sum steamed dumplings",     "Steamed Dumplings",       "Chinese",       "non-vegetarian",                             "gluten|pork",       "protein|snack"),
    ("stir fry vegetables tofu",      "Buddha Bowl",             "Chinese",       "vegan|vegetarian|gluten-free",               "soy",               "vegetable|main"),
    ("kung pao chicken peanut",       "Kung Pao Chicken",        "Chinese",       "non-vegetarian|halal",                       "peanuts|soy",       "protein|main"),
    ("mapo tofu spicy",               "Mapo Tofu",               "Chinese",       "non-vegetarian",                             "soy",               "protein|main"),
    ("fried rice egg vegetable",      "Veggie Fried Rice",       "Chinese",       "vegetarian|halal|kosher",                    "eggs|soy",          "grain|main"),
    ("beef broccoli stir fry",        "Beef & Broccoli",         "Chinese",       "non-vegetarian|gluten-free|halal",           "soy",               "protein|main"),
    ("wonton soup chicken",           "Wonton Soup",             "Chinese",       "non-vegetarian",                             "gluten|eggs",       "protein|soup"),
    ("spring roll vegetable",         "Vegetable Spring Rolls",  "Chinese",       "vegan|vegetarian|halal|kosher",              "gluten",            "vegetable|snack"),
    ("hot sour soup tofu",            "Hot & Sour Soup",         "Chinese",       "vegan|vegetarian|gluten-free",               "soy",               "protein|soup"),
    ("steamed fish ginger scallion",  "Steamed Ginger Fish",     "Chinese",       "pescatarian|non-vegetarian|gluten-free|halal","fish|soy",         "seafood|main"),
    ("eggplant garlic sauce",         "Eggplant in Garlic Sauce","Chinese",       "vegan|vegetarian|gluten-free",               "soy",               "vegetable|main"),
    ("sesame noodles",                "Sesame Noodles",          "Chinese",       "vegan|vegetarian|halal",                     "gluten|soy|sesame", "grain|main"),
    ("green beans stir fry",          "Stir Fry Green Beans",    "Chinese",       "vegan|vegetarian|gluten-free",               "soy",               "vegetable|side"),
    ("clay pot rice casserole",       "Clay Pot Rice",           "Chinese",       "non-vegetarian",                             "gluten|soy",        "grain|main"),

    # ══════════════════════════════════════════════════════
    # KOREAN
    # ══════════════════════════════════════════════════════
    ("bibimbap mixed rice bowl",      "Bibimbap",                "Korean",        "vegetarian",                                 "eggs|gluten",       "grain|main"),
    ("bibimbap vegetables tofu",      "Veg Bibimbap",            "Korean",        "vegan|vegetarian|gluten-free",               "soy",               "grain|main"),
    ("kimchi stew pork tofu",         "Kimchi Jjigae",           "Korean",        "non-vegetarian",                             "gluten|soy",        "protein|soup"),
    ("doenjang soybean paste stew",   "Doenjang Jjigae",         "Korean",        "vegetarian",                                 "soy",               "protein|soup"),
    ("sundubu jjigae soft tofu stew", "Sundubu Jjigae",          "Korean",        "vegetarian",                                 "soy|eggs",          "protein|soup"),
    ("japchae glass noodles vegetables","Japchae",               "Korean",        "vegetarian|gluten-free",                     "eggs|soy",          "grain|main"),
    ("bulgogi beef marinated",        "Bulgogi",                 "Korean",        "non-vegetarian",                             "gluten|soy",        "protein|main"),
    ("samgyeopsal pork belly",        "Grilled Pork Belly",      "Korean",        "non-vegetarian",                             "gluten|soy",        "protein|main"),
    ("dakgalbi spicy chicken",        "Dakgalbi",                "Korean",        "non-vegetarian|gluten-free",                 "soy",               "protein|main"),
    ("mackerel grilled",              "Grilled Mackerel",        "Korean",        "pescatarian|non-vegetarian|gluten-free|halal","fish",             "seafood|main"),
    ("tteokbokki rice cake spicy",    "Tteokbokki",              "Korean",        "vegan|vegetarian",                           "gluten|soy",        "grain|snack"),
    ("haemul pajeon seafood pancake", "Seafood Pancake",         "Korean",        "pescatarian|non-vegetarian",                 "gluten|eggs|shellfish","seafood|main"),
    ("gimbap seaweed rice roll",      "Gimbap",                  "Korean",        "pescatarian|non-vegetarian|gluten-free",     "eggs|soy|sesame",   "grain|main|snack"),
    ("doenjang soup vegetable",       "Korean Veggie Soup",      "Korean",        "vegan|vegetarian",                           "soy",               "vegetable|soup"),

    # ══════════════════════════════════════════════════════
    # THAI
    # ══════════════════════════════════════════════════════
    ("pad thai rice noodles",         "Pad Thai",                "Thai",          "non-vegetarian",                             "gluten|eggs|peanuts|shellfish","grain|main"),
    ("pad thai tofu vegetarian",      "Veg Pad Thai",            "Thai",          "vegetarian",                                 "gluten|eggs|peanuts|soy","grain|main"),
    ("green curry chicken coconut",   "Green Curry Chicken",     "Thai",          "non-vegetarian|gluten-free|halal",           "shellfish",         "protein|main"),
    ("green curry tofu vegetable",    "Veg Green Curry",         "Thai",          "vegan|vegetarian|gluten-free|halal",         "soy",               "protein|main"),
    ("red curry shrimp",              "Red Curry Shrimp",        "Thai",          "pescatarian|non-vegetarian|gluten-free|halal","shellfish",        "seafood|main"),
    ("massaman curry beef potato",    "Massaman Curry",          "Thai",          "non-vegetarian|gluten-free|halal",           "peanuts",           "protein|main"),
    ("tom yum soup shrimp",           "Tom Yum Soup",            "Thai",          "pescatarian|non-vegetarian|gluten-free|halal","shellfish",        "seafood|soup"),
    ("tom kha coconut soup chicken",  "Tom Kha Gai",             "Thai",          "non-vegetarian|gluten-free|halal",           "none",              "protein|soup"),
    ("som tam papaya salad",          "Som Tam Salad",           "Thai",          "vegan|vegetarian|gluten-free|halal",         "peanuts",           "vegetable|salad"),
    ("mango sticky rice dessert",     "Mango Sticky Rice",       "Thai",          "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|dessert"),
    ("larb salad minced chicken",     "Chicken Larb",            "Thai",          "non-vegetarian|gluten-free|halal",           "none",              "protein|salad"),
    ("basil chicken stir fry",        "Basil Chicken",           "Thai",          "non-vegetarian|gluten-free|halal",           "soy",               "protein|main"),
    ("pad see ew noodles broccoli",   "Pad See Ew",              "Thai",          "non-vegetarian",                             "gluten|eggs|soy",   "grain|main"),
    ("satay chicken peanut sauce",    "Chicken Satay",           "Thai",          "non-vegetarian|gluten-free|halal",           "peanuts",           "protein|snack"),
    ("spring roll fresh rice paper",  "Fresh Spring Rolls",      "Thai",          "vegan|vegetarian|gluten-free",               "peanuts",           "vegetable|light|snack"),

    # ══════════════════════════════════════════════════════
    # MEXICAN
    # ══════════════════════════════════════════════════════
    ("black beans rice burrito",      "Burrito Bowl",            "Mexican",       "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("chicken burrito",               "Chicken Burrito",         "Mexican",       "non-vegetarian|halal",                       "gluten|dairy",      "protein|main"),
    ("fish tacos tilapia",            "Fish Tacos",              "Mexican",       "pescatarian|non-vegetarian|halal",           "fish|gluten|dairy", "seafood|main"),
    ("veggie fajitas peppers onion",  "Veggie Fajitas",          "Mexican",       "vegan|vegetarian|halal|kosher",              "gluten",            "vegetable|main"),
    ("chicken fajitas",               "Chicken Fajitas",         "Mexican",       "non-vegetarian|halal",                       "gluten",            "protein|main"),
    ("guacamole avocado",             "Guacamole",               "Mexican",       "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|snack"),
    ("pico de gallo salsa tomato",    "Pico de Gallo",           "Mexican",       "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|snack|side"),
    ("enchiladas cheese bean",        "Bean & Cheese Enchiladas","Mexican",       "vegetarian|halal|kosher",                    "gluten|dairy",      "legume|main"),
    ("taco al pastor pork",           "Al Pastor Tacos",         "Mexican",       "non-vegetarian|halal",                       "gluten",            "protein|main"),
    ("pozole hominy soup",            "Pozole",                  "Mexican",       "non-vegetarian|gluten-free|halal",           "none",              "grain|soup"),
    ("elote corn on cob",             "Elote",                   "Mexican",       "vegetarian|gluten-free|halal|kosher",        "dairy",             "vegetable|snack"),
    ("lentil taco",                   "Lentil Tacos",            "Mexican",       "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("tortilla soup chicken",         "Tortilla Soup",           "Mexican",       "non-vegetarian|halal",                       "gluten",            "protein|soup"),
    ("chile relleno stuffed pepper",  "Chile Relleno",           "Mexican",       "vegetarian|halal|kosher",                    "eggs|dairy",        "vegetable|main"),

    # ══════════════════════════════════════════════════════
    # FRENCH
    # ══════════════════════════════════════════════════════
    ("ratatouille vegetable stew",    "Ratatouille",             "French",        "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|main"),
    ("nicoise salad tuna egg",        "Salade Niçoise",          "French",        "pescatarian|non-vegetarian|gluten-free",     "fish|eggs",         "seafood|salad"),
    ("soupe a loignon onion soup",    "French Onion Soup",       "French",        "vegetarian|halal|kosher",                    "gluten|dairy",      "vegetable|soup"),
    ("quiche lorraine egg cream",     "Quiche Lorraine",         "French",        "vegetarian|kosher",                          "gluten|eggs|dairy", "protein|main|breakfast"),
    ("crepe buckwheat galette",       "Buckwheat Galette",       "French",        "vegetarian|gluten-free|kosher",              "eggs|dairy",        "grain|breakfast"),
    ("bouillabaisse seafood stew",    "Bouillabaisse",           "French",        "pescatarian|non-vegetarian|gluten-free|halal","fish|shellfish",   "seafood|soup"),
    ("coq au vin chicken wine",       "Coq au Vin",              "French",        "non-vegetarian|halal|kosher",                "none",              "protein|main"),
    ("vichyssoise potato leek soup",  "Vichyssoise",             "French",        "vegetarian|gluten-free|kosher",              "dairy",             "vegetable|soup"),
    ("salade lyonnaise bacon egg",    "Salade Lyonnaise",        "French",        "non-vegetarian",                             "eggs",              "protein|salad"),

    # ══════════════════════════════════════════════════════
    # MIDDLE EASTERN
    # ══════════════════════════════════════════════════════
    ("lentil rice mujaddara",         "Mujaddara",               "Middle Eastern","vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("stuffed bell pepper rice",      "Stuffed Bell Peppers",    "Middle Eastern","vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|main"),
    ("shawarma chicken wrap",         "Chicken Shawarma",        "Middle Eastern","non-vegetarian|halal",                       "gluten|dairy",      "protein|main"),
    ("lamb kofta grilled",            "Lamb Kofta",              "Middle Eastern","non-vegetarian|gluten-free|halal",           "none",              "protein|main"),
    ("ful medames fava bean",         "Ful Medames",             "Middle Eastern","vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|breakfast|main"),
    ("fatayer spinach pie",           "Spinach Fatayer",         "Middle Eastern","vegan|vegetarian|halal|kosher",              "gluten",            "vegetable|snack"),
    ("kibbeh bulgur lamb",            "Kibbeh",                  "Middle Eastern","non-vegetarian|halal",                       "gluten",            "protein|main"),
    ("mansaf lamb yogurt rice",       "Mansaf",                  "Middle Eastern","non-vegetarian|gluten-free|halal",           "dairy",             "protein|main"),
    ("roasted cauliflower tahini",    "Roasted Cauliflower",     "Middle Eastern","vegan|vegetarian|gluten-free|halal|kosher",  "sesame",            "vegetable|side"),
    ("dukkah nut seed spice blend",   "Dukkah Eggs",             "Middle Eastern","vegetarian|gluten-free|kosher",              "eggs|tree nuts|sesame","protein|breakfast"),

    # ══════════════════════════════════════════════════════
    # GREEK
    # ══════════════════════════════════════════════════════
    ("chicken souvlaki skewer",       "Chicken Souvlaki",        "Greek",         "non-vegetarian|gluten-free|halal",           "dairy",             "protein|main"),
    ("lamb chops grilled",            "Lamb Chops",              "Greek",         "non-vegetarian|gluten-free|halal",           "none",              "protein|main"),
    ("fasolada white bean soup",      "Fasolada",                "Greek",         "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|soup"),
    ("lemon chicken orzo soup",       "Avgolemono",              "Greek",         "non-vegetarian|halal|kosher",                "eggs|gluten",       "protein|soup"),
    ("dolmades stuffed vine leaves",  "Dolmades",                "Greek",         "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|main|light"),
    ("horiatiki village salad",       "Village Salad",           "Greek",         "vegetarian|gluten-free|halal|kosher",        "dairy",             "vegetable|salad"),

    # ══════════════════════════════════════════════════════
    # AFRICAN / ETHIOPIAN
    # ══════════════════════════════════════════════════════
    ("injera teff flatbread",         "Injera with Lentil",      "Ethiopian",     "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|main"),
    ("misir wat lentil stew",         "Misir Wat",               "Ethiopian",     "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("shiro chickpea stew",           "Shiro Wat",               "Ethiopian",     "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|main"),
    ("tibs sauteed beef vegetables",  "Tibs",                    "Ethiopian",     "non-vegetarian|gluten-free|halal",           "none",              "protein|main"),
    ("jollof rice tomato west africa","Jollof Rice",             "African",       "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|main"),
    ("egusi melon seed soup",         "Egusi Soup",              "African",       "non-vegetarian|gluten-free|halal",           "none",              "protein|soup"),
    ("suya beef skewer spiced",       "Suya",                    "African",       "non-vegetarian|gluten-free|halal",           "peanuts",           "protein|snack"),
    ("tagine chicken moroccan",       "Chicken Tagine",          "African",       "non-vegetarian|gluten-free|halal",           "none",              "protein|main"),
    ("tagine vegetable moroccan",     "Vegetable Tagine",        "African",       "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|main"),
    ("harira soup lentil lamb",       "Harira Soup",             "African",       "non-vegetarian|gluten-free|halal",           "none",              "legume|soup"),

    # ══════════════════════════════════════════════════════
    # LATIN AMERICAN
    # ══════════════════════════════════════════════════════
    ("arepa corn cake stuffed",       "Arepa",                   "Latin American","vegetarian|gluten-free|halal|kosher",        "dairy",             "grain|main|breakfast"),
    ("empanada baked chicken",        "Empanada",                "Latin American","non-vegetarian|halal",                       "gluten|eggs",       "protein|snack"),
    ("feijoada black bean stew",      "Feijoada",                "Latin American","non-vegetarian|gluten-free|halal",           "none",              "legume|main"),
    ("ceviche shrimp lime",           "Ceviche",                 "Latin American","pescatarian|non-vegetarian|gluten-free|halal","shellfish",        "seafood|main|light"),
    ("lomo saltado peru beef",        "Lomo Saltado",            "Latin American","non-vegetarian|halal",                       "gluten|soy",        "protein|main"),
    ("arroz con pollo rice chicken",  "Arroz con Pollo",         "Latin American","non-vegetarian|gluten-free|halal",           "none",              "grain|main"),
    ("black bean soup cuban",         "Cuban Black Bean Soup",   "Latin American","vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|soup"),
    ("tamales corn masa",             "Tamales",                 "Latin American","non-vegetarian|gluten-free|halal",           "none",              "grain|main"),
    ("quinoa salad peruvian",         "Quinoa Ensalada",         "Latin American","vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|salad"),

    # ══════════════════════════════════════════════════════
    # SNACKS / SIDES / LIGHT
    # ══════════════════════════════════════════════════════
    ("apple slices almond butter",    "Apple & Almond Butter",   "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "tree nuts",         "fruit|snack"),
    ("mixed berries yogurt",          "Berry Yogurt Bowl",       "American",      "vegetarian|gluten-free|kosher",              "dairy",             "fruit|snack|breakfast"),
    ("celery sticks hummus",          "Celery & Hummus",         "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "sesame",            "vegetable|snack"),
    ("boiled eggs",                   "Hard Boiled Eggs",        "American",      "vegetarian|gluten-free|halal|kosher",        "eggs",              "protein|snack"),
    ("mixed nuts",                    "Mixed Nuts",              "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "tree nuts",         "protein|snack"),
    ("kale chips baked",              "Kale Chips",              "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|snack"),
    ("roasted chickpeas spiced",      "Roasted Chickpeas",       "Mediterranean", "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "legume|snack"),
    ("rice cakes with avocado",       "Rice Cakes & Avocado",    "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "grain|snack|light"),
    ("steamed broccoli lemon",        "Steamed Broccoli",        "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|side"),
    ("roasted sweet potato wedges",   "Sweet Potato Wedges",     "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|side"),
    ("cucumber tomato salad",         "Cucumber Tomato Salad",   "American",      "vegan|vegetarian|gluten-free|halal|kosher",  "none",              "vegetable|salad|light"),
    ("watermelon feta mint salad",    "Watermelon Salad",        "Mediterranean", "vegetarian|gluten-free|halal|kosher",        "dairy",             "fruit|salad|light"),
    ("mango lassi yogurt",            "Mango Lassi",             "Indian",        "vegetarian|gluten-free|halal|kosher",        "dairy",             "dairy|snack|light"),
    ("golden milk turmeric",          "Turmeric Golden Milk",    "Indian",        "vegetarian|gluten-free|halal|kosher",        "dairy",             "dairy|snack|light"),
    ("protein shake whey",            "Protein Shake",           "American",      "vegetarian|gluten-free|halal|kosher",        "dairy",             "dairy|snack|breakfast"),

]

# ─────────────────────────────────────────────────────────────────────────────
NUTRIENT_IDS = {
    "Energy":                       "calories",
    "Protein":                      "protein_g",
    "Total lipid (fat)":            "fat_g",
    "Carbohydrate, by difference":  "carbs_g",
    "Fiber, total dietary":         "fiber_g",
    "Iron, Fe":                     "iron_mg",
    "Calcium, Ca":                  "calcium_mg",
    "Vitamin B-12":                 "vitamin_b12_ug",
    "Vitamin D (D2 + D3)":          "vitamin_d_iu",
    "Zinc, Zn":                     "zinc_mg",
    "Potassium, K":                 "potassium_mg",
    "Magnesium, Mg":                "magnesium_mg",
    "Sodium, Na":                   "sodium_mg",
}

# Realistic nutrient defaults by category (used when USDA returns nothing)
CATEGORY_DEFAULTS = {
    "grain":     dict(calories=320, protein_g=8,  fat_g=4,  carbs_g=62, fiber_g=5,  iron_mg=2.0, calcium_mg=30,  vitamin_b12_ug=0.1, vitamin_d_iu=0,  zinc_mg=1.5, potassium_mg=200, magnesium_mg=40, sodium_mg=180),
    "legume":    dict(calories=250, protein_g=15, fat_g=3,  carbs_g=40, fiber_g=10, iron_mg=4.0, calcium_mg=60,  vitamin_b12_ug=0.0, vitamin_d_iu=0,  zinc_mg=2.5, potassium_mg=500, magnesium_mg=70, sodium_mg=200),
    "protein":   dict(calories=280, protein_g=30, fat_g=10, carbs_g=8,  fiber_g=1,  iron_mg=2.5, calcium_mg=40,  vitamin_b12_ug=1.5, vitamin_d_iu=20, zinc_mg=4.0, potassium_mg=400, magnesium_mg=35, sodium_mg=250),
    "seafood":   dict(calories=240, protein_g=28, fat_g=8,  carbs_g=4,  fiber_g=0,  iron_mg=1.5, calcium_mg=50,  vitamin_b12_ug=3.0, vitamin_d_iu=80, zinc_mg=2.0, potassium_mg=450, magnesium_mg=40, sodium_mg=300),
    "vegetable": dict(calories=180, protein_g=6,  fat_g=5,  carbs_g=28, fiber_g=6,  iron_mg=2.0, calcium_mg=80,  vitamin_b12_ug=0.0, vitamin_d_iu=0,  zinc_mg=1.0, potassium_mg=600, magnesium_mg=50, sodium_mg=150),
    "salad":     dict(calories=200, protein_g=8,  fat_g=10, carbs_g=20, fiber_g=5,  iron_mg=2.0, calcium_mg=100, vitamin_b12_ug=0.2, vitamin_d_iu=0,  zinc_mg=1.2, potassium_mg=500, magnesium_mg=45, sodium_mg=200),
    "soup":      dict(calories=200, protein_g=10, fat_g=5,  carbs_g=28, fiber_g=4,  iron_mg=2.5, calcium_mg=60,  vitamin_b12_ug=0.3, vitamin_d_iu=0,  zinc_mg=1.5, potassium_mg=450, magnesium_mg=35, sodium_mg=400),
    "dairy":     dict(calories=200, protein_g=12, fat_g=6,  carbs_g=24, fiber_g=0,  iron_mg=0.2, calcium_mg=250, vitamin_b12_ug=1.2, vitamin_d_iu=50, zinc_mg=1.5, potassium_mg=350, magnesium_mg=30, sodium_mg=120),
    "fruit":     dict(calories=180, protein_g=3,  fat_g=2,  carbs_g=38, fiber_g=5,  iron_mg=0.5, calcium_mg=30,  vitamin_b12_ug=0.0, vitamin_d_iu=0,  zinc_mg=0.5, potassium_mg=400, magnesium_mg=25, sodium_mg=20),
    "snack":     dict(calories=180, protein_g=6,  fat_g=8,  carbs_g=22, fiber_g=3,  iron_mg=1.0, calcium_mg=50,  vitamin_b12_ug=0.1, vitamin_d_iu=0,  zinc_mg=1.0, potassium_mg=200, magnesium_mg=25, sodium_mg=150),
    "light":     dict(calories=150, protein_g=6,  fat_g=4,  carbs_g=20, fiber_g=3,  iron_mg=1.0, calcium_mg=60,  vitamin_b12_ug=0.1, vitamin_d_iu=0,  zinc_mg=0.8, potassium_mg=300, magnesium_mg=30, sodium_mg=180),
    "breakfast": dict(calories=300, protein_g=12, fat_g=8,  carbs_g=42, fiber_g=4,  iron_mg=2.0, calcium_mg=120, vitamin_b12_ug=0.5, vitamin_d_iu=20, zinc_mg=1.5, potassium_mg=300, magnesium_mg=35, sodium_mg=220),
    "main":      dict(calories=450, protein_g=22, fat_g=14, carbs_g=52, fiber_g=6,  iron_mg=3.0, calcium_mg=80,  vitamin_b12_ug=0.8, vitamin_d_iu=15, zinc_mg=3.0, potassium_mg=500, magnesium_mg=55, sodium_mg=450),
    "side":      dict(calories=150, protein_g=4,  fat_g=4,  carbs_g=24, fiber_g=4,  iron_mg=1.2, calcium_mg=50,  vitamin_b12_ug=0.0, vitamin_d_iu=0,  zinc_mg=0.8, potassium_mg=350, magnesium_mg=35, sodium_mg=120),
    "dessert":   dict(calories=280, protein_g=4,  fat_g=5,  carbs_g=55, fiber_g=2,  iron_mg=0.8, calcium_mg=40,  vitamin_b12_ug=0.1, vitamin_d_iu=0,  zinc_mg=0.5, potassium_mg=200, magnesium_mg=20, sodium_mg=50),
}

MONASH_HIGH = ["garlic","onion","wheat","rye","barley","legumes","chickpeas",
               "lentils","kidney beans","cauliflower","mushroom","apple","pear",
               "mango","milk","yogurt","custard","fructose","inulin"]
GERD_LIST   = ["tomato","citrus","coffee","chocolate","spicy","fried",
               "peppermint","alcohol","vinegar","garlic","onion"]

# ── Bulk USDA catalog settings ───────────────────────────────────────────────
TARGET_MIN   = 5000          # BAX-423 requirement: ≥5,000-item offline snapshot
PAGE_SIZE    = 200           # USDA max page size for list/search
REQUEST_GAP  = 0.15          # seconds between API calls (1,000 req/hour limit)
BATCH_SIZE   = 20            # fdcIds per /foods batch detail request

USDA_DATA_TYPES = ["Foundation", "SR Legacy", "Branded"]

# Broad search terms — fills gaps if list pagination is slow to reach TARGET_MIN
BULK_SEARCH_TERMS = [
    "rice", "chicken", "beef", "pork", "fish", "salmon", "tuna", "shrimp",
    "bean", "lentil", "chickpea", "tofu", "egg", "milk", "cheese", "yogurt",
    "bread", "pasta", "oat", "quinoa", "potato", "sweet potato", "corn",
    "apple", "banana", "orange", "berry", "grape", "mango", "avocado",
    "broccoli", "spinach", "kale", "carrot", "tomato", "pepper", "onion",
    "mushroom", "cauliflower", "cabbage", "lettuce", "cucumber", "zucchini",
    "soup", "salad", "stew", "curry", "stir fry", "grilled", "baked", "roasted",
    "sandwich", "burger", "pizza", "taco", "burrito", "wrap", "bowl", "smoothie",
    "cereal", "granola", "muffin", "pancake", "waffle", "cookie", "cake",
    "nuts", "almond", "peanut", "walnut", "seed", "hummus", "sauce", "oil",
    "turkey", "lamb", "sausage", "bacon", "ham", "crab", "lobster", "cod",
    "tilapia", "mackerel", "sardine", "tempeh", "edamame", "soy", "barley",
    "wheat", "rye", "couscous", "bulgur", "millet", "barley", "pea", "spinach",
    "asparagus", "beet", "squash", "pumpkin", "melon", "peach", "pear", "plum",
    "cherry", "strawberry", "blueberry", "raspberry", "coconut", "honey",
    "butter", "cream", "ice cream", "chocolate", "coffee", "tea", "juice",
]

MEAT_TERMS = [
    "beef", "pork", "bacon", "ham", "sausage", "pepperoni", "salami", "prosciutto",
    "chicken", "turkey", "duck", "lamb", "mutton", "veal", "venison", "bison",
    "meat", "steak", "burger", "hot dog", "frankfurter", "chorizo",
]
FISH_TERMS = [
    "fish", "salmon", "tuna", "cod", "tilapia", "mackerel", "sardine", "anchovy",
    "trout", "bass", "halibut", "haddock", "catfish", "shrimp", "prawn", "crab",
    "lobster", "scallop", "oyster", "clam", "mussel", "squid", "octopus", "seafood",
]
PORK_TERMS = ["pork", "bacon", "ham", "sausage", "pepperoni", "salami", "prosciutto", "chorizo", "lard"]

CUISINE_KEYWORDS = {
    "Indian":        ["curry", "dal", "masala", "tikka", "biryani", "naan", "chutney", "paneer", "sambar", "dosa", "idli"],
    "Japanese":      ["sushi", "miso", "ramen", "udon", "soba", "teriyaki", "edamame", "tempura", "onigiri", "gyoza"],
    "Chinese":       ["wonton", "dim sum", "kung pao", "mapo", "congee", "fried rice", "lo mein", "szechuan"],
    "Korean":        ["kimchi", "bibimbap", "bulgogi", "gochujang", "japchae", "gimbap", "jjigae"],
    "Thai":          ["pad thai", "tom yum", "tom kha", "satay", "massaman", "green curry", "red curry"],
    "Mexican":       ["taco", "burrito", "enchilada", "quesadilla", "guacamole", "salsa", "tamale", "pozole", "fajita"],
    "Italian":       ["pasta", "pizza", "risotto", "pesto", "marinara", "parmesan", "mozzarella", "bruschetta"],
    "Mediterranean": ["hummus", "falafel", "tzatziki", "tabbouleh", "dolma", "fattoush", "shakshuka", "halloumi"],
    "French":        ["ratatouille", "quiche", "bouillabaisse", "coq au vin", "crepe", "galette", "nicoise"],
    "Middle Eastern":["shawarma", "kofta", "tahini", "ful medames", "kibbeh", "mansaf", "fatayer"],
    "Greek":         ["souvlaki", "moussaka", "spanakopita", "gyro", "tzatziki", "feta", "dolmades"],
    "Ethiopian":     ["injera", "wat", "berbere", "teff", "shiro"],
    "African":       ["jollof", "egusi", "suya", "tagine", "harira", "couscous"],
    "Latin American":["arepa", "empanada", "feijoada", "ceviche", "lomo saltado", "arroz con pollo"],
}


def extract_nutrients(food):
    """Parse nutrients from USDA search, list, or detail responses."""
    nutrients = {}
    for n in food.get("foodNutrients", []):
        nutrient = n.get("nutrient") or {}
        name = (
            n.get("nutrientName")
            or n.get("name")
            or nutrient.get("name")
            or nutrient.get("nutrientName")
            or ""
        )
        mapped = NUTRIENT_IDS.get(name)
        if not mapped:
            continue
        raw = n.get("value")
        if raw is None:
            raw = n.get("amount")
        if raw is None:
            raw = n.get("quantity")
        if raw is None:
            continue
        try:
            val = float(raw)
        except (TypeError, ValueError):
            continue
        if val > 0:
            nutrients[mapped] = round(val, 2)
    return nutrients


def fetch_food(query):
    url = f"{BASE_URL}/foods/search"
    params = {"query": query, "api_key": API_KEY, "pageSize": 1,
              "dataType": "Foundation,SR Legacy,Branded"}
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        foods = data.get("foods", [])
        if not foods:
            return None
        food = foods[0]
        nutrients = extract_nutrients(food)
        return {"usda_fdcId": str(food.get("fdcId", "")),
                "usda_description": food.get("description", query),
                **nutrients}
    except Exception:
        return None


def fetch_foods_list_page(page_number, data_types):
    """Paginated /foods/list — Foundation, SR Legacy, Branded catalog."""
    try:
        r = requests.post(
            f"{BASE_URL}/foods/list?api_key={API_KEY}",
            json={
                "pageSize": PAGE_SIZE,
                "pageNumber": page_number,
                "dataType": data_types,
                "sortBy": "fdcId",
                "sortOrder": "asc",
            },
            timeout=30,
        )
        if r.status_code != 200:
            return []
        data = r.json()
        return data if isinstance(data, list) else []
    except Exception:
        return []


def fetch_search_page(query, page_number):
    """Paginated /foods/search for additional USDA items."""
    try:
        r = requests.post(
            f"{BASE_URL}/foods/search?api_key={API_KEY}",
            json={
                "query": query,
                "pageSize": PAGE_SIZE,
                "pageNumber": page_number,
                "dataType": USDA_DATA_TYPES,
                "sortBy": "dataType.keyword",
                "sortOrder": "asc",
            },
            timeout=30,
        )
        if r.status_code != 200:
            return []
        return r.json().get("foods", [])
    except Exception:
        return []


def fetch_foods_batch_details(fdc_ids):
    """Batch-fetch full nutrient profiles for items missing key fields."""
    if not fdc_ids:
        return {}
    try:
        r = requests.post(
            f"{BASE_URL}/foods?api_key={API_KEY}",
            json={"fdcIds": fdc_ids, "format": "full"},
            timeout=45,
        )
        if r.status_code != 200:
            return {}
        out = {}
        for food in r.json():
            fdc = food.get("fdcId")
            if fdc:
                out[str(fdc)] = extract_nutrients(food)
        return out
    except Exception:
        return {}


def get_defaults(categories_str):
    cats = categories_str.split("|")
    for cat in cats:
        if cat in CATEGORY_DEFAULTS:
            return dict(CATEGORY_DEFAULTS[cat])
    return dict(CATEGORY_DEFAULTS["main"])


def _contains_any(text, terms):
    return any(t in text for t in terms)


def infer_allergens(text):
    t = text.lower()
    found = []
    if _contains_any(t, ["wheat", "bread", "pasta", "flour", "barley", "rye", "gluten",
                         "couscous", "noodle", "cracker", "bagel", "muffin", "cereal", "spelt"]):
        found.append("gluten")
    if _contains_any(t, ["milk", "cheese", "yogurt", "butter", "cream", "whey", "casein",
                         "dairy", "lactose", "ghee", "paneer", "ricotta", "mozzarella"]):
        found.append("dairy")
    if _contains_any(t, ["egg", "eggs", "omelette", "mayonnaise", "meringue"]):
        found.append("eggs")
    if _contains_any(t, ["soy", "tofu", "edamame", "tempeh", "miso", "soybean", "soya"]):
        found.append("soy")
    if _contains_any(t, ["peanut", "peanuts", "groundnut"]):
        found.append("peanuts")
    if _contains_any(t, ["almond", "cashew", "walnut", "pecan", "pistachio", "hazelnut",
                         "macadamia", "pine nut", "tree nut", "brazil nut"]):
        found.append("tree nuts")
    if _contains_any(t, ["shrimp", "prawn", "crab", "lobster", "scallop", "oyster",
                         "clam", "mussel", "shellfish", "crayfish"]):
        found.append("shellfish")
    if _contains_any(t, ["salmon", "tuna", "cod", "fish", "anchovy", "sardine", "trout",
                         "bass", "halibut", "tilapia", "mackerel", "haddock"]):
        found.append("fish")
    if _contains_any(t, ["sesame", "tahini"]):
        found.append("sesame")
    return "|".join(found) if found else "none"


def infer_diet_tags(text, allergens):
    t = text.lower()
    allergen_set = set(allergens.split("|")) if allergens else set()
    has_meat = _contains_any(t, MEAT_TERMS)
    has_fish = _contains_any(t, FISH_TERMS) or "fish" in allergen_set or "shellfish" in allergen_set
    has_pork = _contains_any(t, PORK_TERMS)
    has_dairy = "dairy" in allergen_set
    has_eggs  = "eggs" in allergen_set

    tags = []
    if not has_meat and not has_fish and not has_dairy and not has_eggs:
        tags.extend(["vegan", "vegetarian"])
    elif not has_meat and not has_fish:
        tags.append("vegetarian")
    if has_fish and not has_meat:
        tags.append("pescatarian")
    if has_meat:
        tags.append("non-vegetarian")
    if "gluten" not in allergen_set:
        tags.append("gluten-free")
    if not has_pork:
        tags.append("halal")
    if not has_pork and "shellfish" not in allergen_set:
        tags.append("kosher")
    return "|".join(dict.fromkeys(tags))  # preserve order, dedupe


def infer_categories(text):
    t = text.lower()
    cats = []
    rules = [
        (["breakfast", "oatmeal", "cereal", "pancake", "waffle", "omelette", "granola"], "breakfast"),
        (["soup", "broth", "stew", "chowder", "bisque", "jjigae", "ramen"], "soup"),
        (["salad", "slaw"], "salad"),
        (FISH_TERMS, "seafood"),
        (MEAT_TERMS + ["protein", "steak", "breast", "thigh"], "protein"),
        (["bean", "lentil", "chickpea", "legume", "dal", "hummus", "edamame", "pea"], "legume"),
        (["rice", "bread", "pasta", "noodle", "oat", "quinoa", "grain", "cereal", "barley", "couscous"], "grain"),
        (["milk", "cheese", "yogurt", "cream", "butter", "dairy"], "dairy"),
        (["apple", "banana", "berry", "fruit", "orange", "mango", "grape", "melon"], "fruit"),
        (["cookie", "cake", "dessert", "ice cream", "chocolate", "candy", "pie"], "dessert"),
        (["snack", "chip", "cracker", "bar", "nuts"], "snack"),
        (["broccoli", "spinach", "carrot", "vegetable", "kale", "pepper", "tomato", "onion"], "vegetable"),
    ]
    for keywords, cat in rules:
        if _contains_any(t, keywords):
            cats.append(cat)
    if not cats:
        cats.append("main")
    if "side" not in cats and any(x in t for x in ["side", "accompaniment"]):
        cats.append("side")
    return "|".join(dict.fromkeys(cats))


def infer_cuisine(text):
    t = text.lower()
    for cuisine, keywords in CUISINE_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            return cuisine
    return "American"


def clean_display_name(description):
    """Turn USDA description into a readable dish/food name."""
    name = description.strip()
    if not name:
        return "USDA Food Item"
    if name.isupper() and len(name) > 4:
        name = name.title()
    return name[:120]


def fill_nutrients(usda, categories):
    defaults = get_defaults(categories)
    for k, v in defaults.items():
        if k not in usda or usda.get(k, 0) == 0:
            usda[k] = v
    return usda, defaults


def build_record(fid, name, cuisine, categories, diet_tags, allergens,
                 usda, query_fallback=""):
    name_lower = f"{name} {query_fallback}".lower()
    is_fodmap = int(any(t in name_lower for t in MONASH_HIGH))
    is_gerd   = int(any(t in name_lower for t in GERD_LIST))
    defaults  = get_defaults(categories)
    usda, _   = fill_nutrients(usda, categories)
    is_hi_na  = int(usda.get("sodium_mg", 0) > 400)
    allergen_l = allergens.lower()
    return {
        "food_id":          fid,
        "name":             name,
        "cuisine":          cuisine,
        "categories":       categories,
        "diet_tags":        diet_tags,
        "safe_conditions":  "",
        "allergens":        allergens,
        "calories":         usda.get("calories", defaults["calories"]),
        "protein_g":        usda.get("protein_g", defaults["protein_g"]),
        "carbs_g":          usda.get("carbs_g", defaults["carbs_g"]),
        "fat_g":            usda.get("fat_g", defaults["fat_g"]),
        "fiber_g":          usda.get("fiber_g", defaults["fiber_g"]),
        "iron_mg":          usda.get("iron_mg", defaults["iron_mg"]),
        "calcium_mg":       usda.get("calcium_mg", defaults["calcium_mg"]),
        "vitamin_b12_ug":   usda.get("vitamin_b12_ug", defaults["vitamin_b12_ug"]),
        "vitamin_d_iu":     usda.get("vitamin_d_iu", defaults["vitamin_d_iu"]),
        "zinc_mg":          usda.get("zinc_mg", defaults["zinc_mg"]),
        "potassium_mg":     usda.get("potassium_mg", defaults["potassium_mg"]),
        "magnesium_mg":     usda.get("magnesium_mg", defaults["magnesium_mg"]),
        "sodium_mg":        usda.get("sodium_mg", defaults["sodium_mg"]),
        "gi_score":         45,
        "is_high_fodmap":   is_fodmap,
        "is_gerd_trigger":  is_gerd,
        "is_high_gi":       0,
        "is_high_sodium":   is_hi_na,
        "has_soy":          int("soy" in allergen_l),
        "has_tree_nuts":    int("tree nuts" in allergen_l),
        "usda_fdcId":       usda.get("usda_fdcId", ""),
        "usda_description": usda.get("usda_description", name),
    }


def add_bulk_food(food, records, seen_fdc, seen_names, fid, pending_detail):
    """Add one USDA catalog item; queue for batch detail fetch if nutrients sparse."""
    fdc_id = food.get("fdcId")
    if not fdc_id:
        return fid, False
    fdc_key = str(fdc_id)
    if fdc_key in seen_fdc:
        return fid, False

    desc = (food.get("description") or "").strip()
    if len(desc) < 3:
        return fid, False

    name_key = desc.lower()
    if name_key in seen_names:
        return fid, False

    nutrients = extract_nutrients(food)
    if nutrients.get("calories", 0) == 0:
        pending_detail.append(fdc_id)

    allergens  = infer_allergens(desc)
    categories = infer_categories(desc)
    diet_tags  = infer_diet_tags(desc, allergens)
    cuisine    = infer_cuisine(desc)
    display    = clean_display_name(desc)

    usda = {
        "usda_fdcId": fdc_key,
        "usda_description": desc,
        **nutrients,
    }

    records.append(build_record(
        fid, display, cuisine, categories, diet_tags, allergens, usda, desc
    ))
    seen_fdc.add(fdc_key)
    seen_names.add(name_key)
    return fid + 1, True


def apply_batch_details(records, detail_map):
    """Back-fill nutrients from batch /foods detail responses."""
    if not detail_map:
        return
    for rec in records:
        fdc = str(rec.get("usda_fdcId", ""))
        if not fdc or fdc not in detail_map:
            continue
        extra = detail_map[fdc]
        if not extra:
            continue
        for k, v in extra.items():
            if v and (rec.get(k, 0) == 0 or rec.get(k) is None):
                rec[k] = v
        defaults = get_defaults(rec["categories"])
        for k, v in defaults.items():
            if rec.get(k, 0) == 0:
                rec[k] = v
        rec["is_high_sodium"] = int(rec.get("sodium_mg", 0) > 400)


def bulk_fetch_usda(records, seen_fdc, seen_names, fid):
    """
    Phase 2: Paginate USDA Foundation + SR Legacy + Branded until TARGET_MIN.
    Phase 3: Supplement with broad search terms if still below target.
    """
    pending_detail = []

    print(f"\n── Phase 2: Bulk USDA catalog (target ≥ {TARGET_MIN:,}) ──\n")
    for data_type in USDA_DATA_TYPES:
        if len(records) >= TARGET_MIN:
            break
        page = 1
        empty_streak = 0
        print(f"  Fetching {data_type}...", flush=True)
        while len(records) < TARGET_MIN and empty_streak < 2:
            foods = fetch_foods_list_page(page, [data_type])
            if not foods:
                empty_streak += 1
                page += 1
                time.sleep(REQUEST_GAP)
                continue
            empty_streak = 0
            added = 0
            for food in foods:
                fid, ok = add_bulk_food(
                    food, records, seen_fdc, seen_names, fid, pending_detail
                )
                if ok:
                    added += 1
            print(f"    page {page:>4}  +{added:>3} items  (total {len(records):,})", flush=True)
            if len(foods) < PAGE_SIZE:
                break
            page += 1
            time.sleep(REQUEST_GAP)

    if len(records) < TARGET_MIN:
        print(f"\n── Phase 3: Search supplement (still need {TARGET_MIN - len(records):,}) ──\n")
        for term in BULK_SEARCH_TERMS:
            if len(records) >= TARGET_MIN:
                break
            for page in range(1, 6):
                if len(records) >= TARGET_MIN:
                    break
                foods = fetch_search_page(term, page)
                if not foods:
                    break
                added = 0
                for food in foods:
                    fid, ok = add_bulk_food(
                        food, records, seen_fdc, seen_names, fid, pending_detail
                    )
                    if ok:
                        added += 1
                if added:
                    print(f"    '{term}' p{page}  +{added}  (total {len(records):,})", flush=True)
                if len(foods) < PAGE_SIZE:
                    break
                time.sleep(REQUEST_GAP)

    return fid, pending_detail


def save_csv(records, label=""):
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "food_database.csv")
    df = pd.DataFrame(records)
    df.to_csv(out, index=False)
    tag = f" ({label})" if label else ""
    print(f"\n💾  Saved {len(df):,} foods to {out}{tag}", flush=True)
    return out, df


def backfill_nutrients(records, pending_detail):
    """Optional Phase 4 — enrich sparse nutrient rows (slow; safe to skip)."""
    if not pending_detail:
        return
    unique_pending = list(dict.fromkeys(pending_detail))
    total_batches = (len(unique_pending) - 1) // BATCH_SIZE + 1
    print(f"\n── Phase 4: Back-filling nutrients for {len(unique_pending):,} items ──", flush=True)
    print(f"    ({total_batches} API batches — ~{total_batches * 2}s, please wait)\n", flush=True)
    for i in range(0, len(unique_pending), BATCH_SIZE):
        batch_num = i // BATCH_SIZE + 1
        batch = unique_pending[i:i + BATCH_SIZE]
        print(f"    batch {batch_num}/{total_batches} ...", end="", flush=True)
        detail_map = fetch_foods_batch_details(batch)
        apply_batch_details(records, detail_map)
        print(f" done ({len(detail_map)} enriched)", flush=True)
        time.sleep(REQUEST_GAP)


def main():
    n_curated = len(FOOD_QUERIES)
    print(f"NutriAI — building ≥{TARGET_MIN:,}-item USDA food database")
    print(f"  Phase 1: {n_curated} curated dishes")
    print(f"  Phase 2: bulk Foundation + SR Legacy + Branded catalog\n")

    records    = []
    seen_fdc   = set()
    seen_names = set()
    fid        = 1

    # ── Phase 1: Curated dishes (original FOOD_QUERIES) ──────────────────────
    for i, (query, display_name, cuisine, diet_tags, allergens, categories) in enumerate(FOOD_QUERIES):
        print(f"  [{i+1:>3}/{n_curated}] {display_name:<35} ", end="", flush=True)
        usda = fetch_food(query)
        defaults = get_defaults(categories)

        if usda and usda.get("usda_fdcId"):
            usda, _ = fill_nutrients(usda, categories)
            seen_fdc.add(str(usda["usda_fdcId"]))
            print(f"✅  {usda['calories']:.0f} kcal  [fdcId={usda['usda_fdcId']}]")
        else:
            usda = dict(defaults)
            usda["usda_fdcId"] = ""
            usda["usda_description"] = query
            print(f"⚠️  defaults used ({defaults['calories']} kcal)")

        seen_names.add(display_name.lower())
        records.append(build_record(
            fid, display_name, cuisine, categories, diet_tags, allergens, usda, query
        ))
        fid += 1
        time.sleep(REQUEST_GAP)

    # ── Phase 2+3: Bulk USDA until ≥ 5,000 ───────────────────────────────────
    fid, pending_detail = bulk_fetch_usda(records, seen_fdc, seen_names, fid)

    # Save immediately so 5,000+ rows are on disk even if Phase 4 is slow/interrupted
    out, df = save_csv(records, label="before nutrient back-fill")

    # Phase 4 is optional — set SKIP_BACKFILL=1 to finish faster
    if os.environ.get("SKIP_BACKFILL", "").strip() not in ("1", "true", "yes"):
        backfill_nutrients(records, pending_detail)
        out, df = save_csv(records, label="final")
    else:
        print("\n⏭️  Skipped Phase 4 back-fill (SKIP_BACKFILL=1)", flush=True)

    real_usda = (df["usda_fdcId"].astype(str).str.strip() != "").sum()
    print(f"\n✅  Done — {len(df):,} foods in {out}")
    print(f"    Curated dishes: {n_curated:,}")
    print(f"    Bulk USDA catalog: {len(df) - n_curated:,}")
    print(f"    Real USDA fdcIds: {real_usda:,}  |  Defaults-filled: {len(df) - real_usda:,}")
    print(f"    Cuisines: {df['cuisine'].nunique()}  |  Data types: Foundation, SR Legacy, Branded")

    if len(df) < TARGET_MIN:
        print(f"\n⚠️  WARNING: Only {len(df):,} items — re-run script (API may have rate-limited).")
    else:
        print(f"\n🎉  Requirement met: {len(df):,} ≥ {TARGET_MIN:,} offline snapshot items.")


if __name__ == "__main__":
    main()
