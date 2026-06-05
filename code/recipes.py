"""
Recipe & Ingredient database for NutriAI.
Each entry has: ingredients (with amounts), steps, prep_time, cook_time, servings.
"""

RECIPES = {
    # ─── INDIAN ───────────────────────────────────────────────────────────
    "Brown Rice Bowl": {
        "prep_time": "5 min", "cook_time": "25 min", "servings": 1,
        "ingredients": [
            "½ cup brown rice", "1 cup water or vegetable broth",
            "½ cup chickpeas (canned, drained)", "1 cup spinach",
            "½ tsp cumin seeds", "1 tsp olive oil", "salt to taste", "lemon juice"
        ],
        "steps": [
            "Rinse brown rice and cook in water/broth for 25 min until tender.",
            "Heat oil in a pan, add cumin seeds and sauté 30 seconds.",
            "Add chickpeas and spinach, cook 3 min until wilted.",
            "Serve over rice, squeeze lemon juice on top."
        ]
    },
    "Lentil Dal": {
        "prep_time": "5 min", "cook_time": "20 min", "servings": 1,
        "ingredients": [
            "½ cup red lentils (rinsed)", "1½ cups water", "½ tsp turmeric",
            "1 tsp cumin", "½ tsp coriander powder", "1 tsp ghee or oil",
            "salt to taste", "fresh coriander to garnish"
        ],
        "steps": [
            "Boil lentils with water and turmeric for 15 min until soft.",
            "In a separate pan, heat ghee and add cumin — let it sizzle 30s.",
            "Add coriander powder, stir 10 seconds.",
            "Pour the tempering over the cooked dal, mix and serve."
        ]
    },
    "Paneer Tikka": {
        "prep_time": "15 min", "cook_time": "15 min", "servings": 1,
        "ingredients": [
            "150g paneer (cubed)", "¼ cup Greek yogurt", "1 tsp tandoori masala",
            "½ tsp turmeric", "½ tsp chili powder", "1 tsp lemon juice",
            "1 tsp oil", "bell pepper & onion chunks", "salt to taste"
        ],
        "steps": [
            "Mix yogurt, spices, lemon juice and salt into a marinade.",
            "Coat paneer cubes and vegetables, marinate 10 min.",
            "Grill or pan-fry on high heat 3–4 min per side until charred.",
            "Serve with mint chutney and lemon wedge."
        ]
    },
    "Chicken Curry": {
        "prep_time": "10 min", "cook_time": "25 min", "servings": 1,
        "ingredients": [
            "150g chicken breast (cubed)", "½ cup diced tomatoes",
            "¼ cup coconut milk", "1 tsp curry powder", "½ tsp garam masala",
            "½ tsp turmeric", "1 clove garlic (minced)", "1 tsp oil", "salt"
        ],
        "steps": [
            "Heat oil, sauté garlic 1 min. Add chicken and brown 5 min.",
            "Add tomatoes and all spices, cook 5 min.",
            "Pour in coconut milk, simmer 15 min until chicken is cooked through.",
            "Serve with rice or roti."
        ]
    },
    "Chickpea Curry": {
        "prep_time": "5 min", "cook_time": "20 min", "servings": 1,
        "ingredients": [
            "1 can (400g) chickpeas (drained)", "½ cup crushed tomatoes",
            "¼ cup coconut milk", "1 tsp cumin", "1 tsp coriander",
            "½ tsp turmeric", "½ tsp garam masala", "1 tsp oil", "salt"
        ],
        "steps": [
            "Heat oil in a pan over medium heat.",
            "Add cumin, cook 30s. Add crushed tomatoes and spices, cook 5 min.",
            "Add chickpeas and coconut milk, simmer 15 min.",
            "Adjust seasoning and serve with brown rice or naan."
        ]
    },
    "Masoor Dal": {
        "prep_time": "5 min", "cook_time": "20 min", "servings": 1,
        "ingredients": [
            "½ cup red lentils", "1½ cups water", "½ tsp turmeric",
            "1 tsp cumin seeds", "2 cloves garlic", "1 tsp oil", "salt", "fresh coriander"
        ],
        "steps": [
            "Cook lentils with water and turmeric 15 min until mushy.",
            "Heat oil, fry garlic and cumin seeds until golden.",
            "Pour tempering into dal, season with salt.",
            "Top with fresh coriander and serve."
        ]
    },
    "Idli Sambar": {
        "prep_time": "5 min", "cook_time": "15 min", "servings": 1,
        "ingredients": [
            "4 idli (store-bought or homemade batter)", "½ cup toor dal (cooked)",
            "½ cup mixed vegetables (carrot, drumstick, tomato)",
            "1 tsp sambar powder", "½ tsp tamarind paste", "1 tsp oil",
            "mustard seeds", "curry leaves", "salt"
        ],
        "steps": [
            "Steam idli batter in idli molds for 10 min.",
            "Boil cooked dal with vegetables, sambar powder and tamarind 10 min.",
            "Temper with mustard seeds and curry leaves in oil, add to sambar.",
            "Serve idli with hot sambar."
        ]
    },
    "Poha": {
        "prep_time": "5 min", "cook_time": "10 min", "servings": 1,
        "ingredients": [
            "1 cup flattened rice (poha)", "¼ cup frozen peas",
            "½ tsp mustard seeds", "½ tsp turmeric", "1 tsp oil",
            "½ onion (finely chopped, OPTIONAL — omit for IBS)", "lemon juice", "salt", "fresh coriander"
        ],
        "steps": [
            "Rinse poha in cold water, drain and set aside.",
            "Heat oil, add mustard seeds. When they pop, add onion (if using).",
            "Add turmeric and peas, stir 2 min.",
            "Add soaked poha, mix well, cook 3 min. Finish with lemon juice and coriander."
        ]
    },
    "Besan Chilla": {
        "prep_time": "5 min", "cook_time": "10 min", "servings": 1,
        "ingredients": [
            "½ cup chickpea flour (besan)", "¼ cup water",
            "¼ cup grated zucchini or spinach", "½ tsp cumin", "¼ tsp turmeric",
            "1 tsp oil", "salt and pepper"
        ],
        "steps": [
            "Mix besan, water, vegetables and spices into a smooth batter.",
            "Heat a non-stick pan with oil on medium heat.",
            "Pour batter, spread into a thin circle. Cook 3 min per side.",
            "Serve with green chutney or yogurt (if not dairy-free)."
        ]
    },
    "Rajma Chawal": {
        "prep_time": "5 min", "cook_time": "20 min", "servings": 1,
        "ingredients": [
            "1 can kidney beans (drained)", "½ cup crushed tomatoes",
            "½ tsp cumin", "½ tsp garam masala", "¼ tsp turmeric", "1 tsp oil",
            "½ cup cooked brown rice", "salt", "fresh coriander"
        ],
        "steps": [
            "Heat oil, add cumin. Add tomatoes and spices, cook 5 min.",
            "Add kidney beans, mash a few for thick gravy. Simmer 10 min.",
            "Season with salt, top with coriander.",
            "Serve over brown rice."
        ]
    },
    "Sprouts Salad": {
        "prep_time": "5 min", "cook_time": "0 min", "servings": 1,
        "ingredients": [
            "1 cup mixed bean sprouts", "½ cucumber (diced)", "1 tomato (diced)",
            "½ lemon (juiced)", "¼ tsp cumin powder", "¼ tsp chaat masala",
            "salt and pepper", "fresh coriander"
        ],
        "steps": [
            "Rinse sprouts and combine with cucumber and tomato.",
            "Add lemon juice, cumin powder and chaat masala.",
            "Toss well, season with salt and pepper.",
            "Garnish with coriander and serve immediately."
        ]
    },

    # ─── AMERICAN ────────────────────────────────────────────────────────
    "Grilled Salmon": {
        "prep_time": "5 min", "cook_time": "12 min", "servings": 1,
        "ingredients": [
            "150g salmon fillet", "1 tsp olive oil", "1 clove garlic (minced)",
            "1 tsp lemon juice", "½ tsp dried dill", "salt and pepper",
            "steamed broccoli to serve"
        ],
        "steps": [
            "Rub salmon with olive oil, garlic, dill, salt and pepper.",
            "Heat grill or pan to medium-high.",
            "Cook salmon 5–6 min per side until opaque in the centre.",
            "Squeeze lemon juice over and serve with steamed broccoli."
        ]
    },
    "Oatmeal Bowl": {
        "prep_time": "2 min", "cook_time": "5 min", "servings": 1,
        "ingredients": [
            "½ cup rolled oats", "1 cup oat milk or water", "1 banana (sliced)",
            "1 tbsp chia seeds", "1 tbsp almond butter (omit for tree nut allergy)",
            "1 tsp maple syrup", "pinch of cinnamon"
        ],
        "steps": [
            "Bring oat milk/water to a simmer in a small saucepan.",
            "Stir in oats and cook 3–4 min, stirring occasionally.",
            "Transfer to a bowl and top with banana, chia seeds, almond butter.",
            "Drizzle maple syrup and sprinkle cinnamon."
        ]
    },
    "Quinoa Salad": {
        "prep_time": "5 min", "cook_time": "15 min", "servings": 1,
        "ingredients": [
            "½ cup quinoa", "1 cup water", "½ cup cherry tomatoes (halved)",
            "½ cucumber (diced)", "¼ red onion (finely chopped — omit for IBS)",
            "2 tbsp olive oil", "1 tbsp lemon juice", "fresh parsley", "salt and pepper"
        ],
        "steps": [
            "Rinse quinoa, cook in water 15 min until fluffy. Cool.",
            "Combine cooled quinoa with tomatoes, cucumber and onion.",
            "Whisk olive oil, lemon juice, salt and pepper into dressing.",
            "Toss salad with dressing and garnish with parsley."
        ]
    },
    "Egg White Omelette": {
        "prep_time": "3 min", "cook_time": "5 min", "servings": 1,
        "ingredients": [
            "4 egg whites", "¼ cup baby spinach", "¼ cup diced bell pepper",
            "1 tbsp feta cheese (omit for dairy-free)", "1 tsp olive oil",
            "salt and pepper", "fresh herbs"
        ],
        "steps": [
            "Whisk egg whites with salt and pepper until frothy.",
            "Heat oil in non-stick pan on medium. Add bell pepper, cook 2 min.",
            "Pour in egg whites, cook until edges set. Add spinach and feta.",
            "Fold omelette in half and slide onto plate."
        ]
    },
    "Chia Pudding": {
        "prep_time": "5 min", "cook_time": "0 min (overnight)", "servings": 1,
        "ingredients": [
            "3 tbsp chia seeds", "1 cup coconut milk or oat milk",
            "1 tsp maple syrup", "½ tsp vanilla extract",
            "fresh berries to serve", "1 tbsp pumpkin seeds"
        ],
        "steps": [
            "Whisk chia seeds, milk, maple syrup and vanilla in a jar.",
            "Stir well after 5 min to prevent clumping.",
            "Refrigerate overnight (or at least 4 hours).",
            "Top with fresh berries and pumpkin seeds before serving."
        ]
    },
    "Smoothie Bowl": {
        "prep_time": "5 min", "cook_time": "0 min", "servings": 1,
        "ingredients": [
            "1 frozen banana", "½ cup frozen mango or berries",
            "¼ cup coconut milk", "1 tbsp chia seeds",
            "Toppings: sliced kiwi, granola (GF if needed), coconut flakes, hemp seeds"
        ],
        "steps": [
            "Blend frozen banana, mango/berries and coconut milk until thick and smooth.",
            "Pour into a bowl — mixture should be thick enough to hold toppings.",
            "Arrange toppings decoratively on top.",
            "Eat immediately before it melts."
        ]
    },
    "Sweet Potato Bowl": {
        "prep_time": "5 min", "cook_time": "30 min", "servings": 1,
        "ingredients": [
            "1 medium sweet potato", "½ cup black beans (canned, drained)",
            "¼ avocado (sliced)", "2 tbsp salsa or pico de gallo",
            "1 tsp olive oil", "½ tsp smoked paprika", "salt and pepper"
        ],
        "steps": [
            "Preheat oven to 200°C. Pierce sweet potato, rub with oil and paprika.",
            "Roast 25–30 min until tender. Slice open and fluff inside.",
            "Warm black beans in microwave 1 min.",
            "Top sweet potato with beans, avocado and salsa."
        ]
    },
    "Black Bean Bowl": {
        "prep_time": "5 min", "cook_time": "10 min", "servings": 1,
        "ingredients": [
            "1 can black beans (drained)", "½ cup brown rice (cooked)",
            "¼ avocado", "¼ cup corn", "2 tbsp lime juice",
            "½ tsp cumin", "1 tsp olive oil", "fresh coriander", "salt"
        ],
        "steps": [
            "Heat oil in pan, add cumin. Add black beans and corn, cook 5 min.",
            "Season with lime juice and salt.",
            "Serve over brown rice with avocado and coriander."
        ]
    },
    "Chicken Breast Grilled": {
        "prep_time": "5 min", "cook_time": "15 min", "servings": 1,
        "ingredients": [
            "150g chicken breast", "1 tsp olive oil", "½ tsp garlic powder (omit for IBS)",
            "½ tsp paprika", "½ tsp dried oregano", "salt and pepper",
            "side salad or steamed vegetables"
        ],
        "steps": [
            "Pound chicken breast to even thickness. Rub with oil and spices.",
            "Heat grill pan over medium-high.",
            "Cook chicken 6–7 min per side until internal temp reaches 75°C.",
            "Rest 5 min before slicing. Serve with side salad."
        ]
    },
    "Tuna Salad": {
        "prep_time": "5 min", "cook_time": "0 min", "servings": 1,
        "ingredients": [
            "1 can (120g) tuna in water (drained)", "2 cups mixed greens",
            "½ cucumber (sliced)", "½ cup cherry tomatoes",
            "1 tbsp olive oil", "1 tsp lemon juice", "salt and pepper",
            "1 hard-boiled egg (optional)"
        ],
        "steps": [
            "Flake tuna over a bed of mixed greens.",
            "Add cucumber, tomatoes and egg (if using).",
            "Drizzle with olive oil and lemon juice.",
            "Season with salt and pepper, toss gently."
        ]
    },
    "Cauliflower Rice Bowl": {
        "prep_time": "5 min", "cook_time": "10 min", "servings": 1,
        "ingredients": [
            "1 cup cauliflower rice (or blitz half a head)", "½ cup edamame",
            "¼ avocado", "½ cup shredded red cabbage", "1 tsp sesame oil",
            "1 tbsp low-sodium soy sauce (omit for soy allergy)", "sesame seeds"
        ],
        "steps": [
            "Sauté cauliflower rice in sesame oil 5 min until tender.",
            "Add edamame, cook 2 more min.",
            "Serve in bowl with cabbage and avocado.",
            "Drizzle soy sauce and sprinkle sesame seeds."
        ]
    },

    # ─── JAPANESE / KOREAN ───────────────────────────────────────────────
    "Sushi Bowl": {
        "prep_time": "10 min", "cook_time": "20 min", "servings": 1,
        "ingredients": [
            "½ cup sushi rice", "1 tsp rice vinegar", "80g sashimi-grade salmon",
            "¼ avocado (sliced)", "½ cup edamame (shelled)", "1 sheet nori (torn)",
            "1 tsp low-sodium soy sauce", "1 tsp sesame seeds", "pickled ginger"
        ],
        "steps": [
            "Cook sushi rice according to package. Stir in rice vinegar, cool.",
            "Slice salmon into thin pieces.",
            "Arrange rice in bowl, top with salmon, avocado, edamame and nori.",
            "Drizzle soy sauce, sprinkle sesame seeds, serve with pickled ginger."
        ]
    },
    "Miso Soup": {
        "prep_time": "2 min", "cook_time": "5 min", "servings": 1,
        "ingredients": [
            "1½ cups water", "1 tsp dashi powder (or vegetable stock)",
            "1 tbsp white miso paste", "50g silken tofu (cubed)",
            "1 tbsp dried wakame seaweed", "1 spring onion (sliced)"
        ],
        "steps": [
            "Heat water and dashi to near boil (do not boil).",
            "Whisk in miso paste until dissolved.",
            "Add tofu and wakame, heat 2 min.",
            "Pour into bowl and garnish with spring onion."
        ]
    },
    "Salmon Sashimi": {
        "prep_time": "5 min", "cook_time": "0 min", "servings": 1,
        "ingredients": [
            "120g sashimi-grade salmon", "1 tsp low-sodium soy sauce",
            "½ tsp wasabi (optional)", "pickled ginger", "shredded daikon",
            "1 tsp sesame seeds", "lemon slice"
        ],
        "steps": [
            "Slice salmon thinly against the grain at a slight angle.",
            "Arrange slices on a plate over shredded daikon.",
            "Place wasabi and pickled ginger on the side.",
            "Serve with low-sodium soy sauce and lemon."
        ]
    },
    "Grilled Mackerel": {
        "prep_time": "5 min", "cook_time": "12 min", "servings": 1,
        "ingredients": [
            "1 mackerel fillet (150g)", "1 tsp sesame oil", "1 tsp low-sodium soy sauce",
            "½ tsp ginger (grated)", "1 spring onion", "steamed rice to serve"
        ],
        "steps": [
            "Score the skin of the mackerel and marinate in sesame oil, soy and ginger 10 min.",
            "Grill skin-side up for 5 min, flip and cook 5–6 more min.",
            "Garnish with sliced spring onion.",
            "Serve with steamed rice and pickled vegetables."
        ]
    },
    "Korean Tofu Soup": {
        "prep_time": "5 min", "cook_time": "15 min", "servings": 1,
        "ingredients": [
            "150g firm tofu (cubed)", "2 cups vegetable stock",
            "1 cup napa cabbage (chopped)", "½ cup mushrooms",
            "1 tbsp gochujang (chili paste — omit for GERD)",
            "1 tsp sesame oil", "1 spring onion", "salt"
        ],
        "steps": [
            "Bring stock to boil, add gochujang and stir.",
            "Add tofu, cabbage and mushrooms. Simmer 10 min.",
            "Finish with sesame oil and season with salt.",
            "Serve in a stone bowl with rice, topped with spring onion."
        ]
    },

    # ─── MEDITERRANEAN ───────────────────────────────────────────────────
    "Grilled Sea Bass": {
        "prep_time": "5 min", "cook_time": "12 min", "servings": 1,
        "ingredients": [
            "150g sea bass fillet", "1 tbsp olive oil", "1 clove garlic",
            "½ lemon (juiced — omit for GERD)", "fresh thyme and rosemary",
            "capers and olives to serve", "salt and pepper"
        ],
        "steps": [
            "Score fish skin, rub with olive oil, garlic, herbs, salt and pepper.",
            "Heat pan to high. Cook skin-side down 4–5 min until crispy.",
            "Flip and cook 3–4 min until opaque.",
            "Serve with capers, olives and lemon (if not GERD)."
        ]
    },
    "Hummus Plate": {
        "prep_time": "10 min", "cook_time": "0 min", "servings": 1,
        "ingredients": [
            "1 can chickpeas (drained, reserve liquid)", "2 tbsp tahini",
            "1 tbsp olive oil", "1 clove garlic", "½ lemon (juiced)",
            "½ tsp cumin", "salt", "paprika and olive oil to serve",
            "cucumber, carrot sticks, GF pita or rice crackers"
        ],
        "steps": [
            "Blend chickpeas, tahini, olive oil, garlic, lemon and cumin until smooth.",
            "Add 1–2 tbsp reserved chickpea liquid to reach desired consistency.",
            "Season with salt, spread in a bowl.",
            "Top with paprika drizzle. Serve with vegetables or crackers."
        ]
    },
    "Shakshuka": {
        "prep_time": "5 min", "cook_time": "20 min", "servings": 1,
        "ingredients": [
            "2 eggs", "½ can crushed tomatoes (omit for GERD — use roasted red pepper instead)",
            "¼ onion (omit for IBS)", "½ bell pepper (diced)", "1 tsp cumin",
            "½ tsp paprika", "1 tsp olive oil", "fresh parsley", "salt and pepper"
        ],
        "steps": [
            "Heat oil, sauté onion and bell pepper 5 min.",
            "Add tomatoes and spices, simmer 10 min.",
            "Make 2 wells in the sauce, crack eggs in.",
            "Cover and cook 5–7 min until whites are set. Garnish with parsley."
        ]
    },
    "Lentil Soup": {
        "prep_time": "5 min", "cook_time": "25 min", "servings": 1,
        "ingredients": [
            "½ cup red lentils", "2 cups vegetable stock", "1 carrot (diced)",
            "1 celery stalk (diced)", "1 tsp cumin", "½ tsp turmeric",
            "1 tsp olive oil", "lemon juice", "salt and fresh herbs"
        ],
        "steps": [
            "Heat oil in pot, add cumin, stir 30s.",
            "Add carrot and celery, cook 3 min.",
            "Add lentils, stock and turmeric. Bring to boil, simmer 20 min.",
            "Blend partially for creamy texture. Add lemon juice and season."
        ]
    },
    "Falafel Bowl": {
        "prep_time": "10 min", "cook_time": "20 min", "servings": 1,
        "ingredients": [
            "1 can chickpeas (drained)", "¼ onion", "2 cloves garlic",
            "1 tsp cumin", "1 tsp coriander", "2 tbsp chickpea flour", "salt",
            "1 tsp oil for frying", "quinoa or rice base", "cucumber, tomato, tahini drizzle"
        ],
        "steps": [
            "Blend chickpeas, onion, garlic, spices and flour until coarse paste.",
            "Shape into balls and flatten slightly.",
            "Pan-fry in oil 3–4 min per side until golden.",
            "Serve over quinoa with cucumber, tomato and tahini."
        ]
    },

    # ─── THAI / CHINESE ──────────────────────────────────────────────────
    "Green Curry": {
        "prep_time": "5 min", "cook_time": "20 min", "servings": 1,
        "ingredients": [
            "150g tofu or chicken", "1 can (400ml) coconut milk",
            "1 tbsp green curry paste (check for allergens)", "1 cup mixed vegetables",
            "1 kaffir lime leaf", "1 tsp fish sauce or soy sauce",
            "fresh basil", "steamed jasmine rice"
        ],
        "steps": [
            "Heat a dry pan, fry curry paste 1 min until fragrant.",
            "Add coconut milk, stir until combined.",
            "Add protein and vegetables, simmer 15 min.",
            "Season with fish/soy sauce, add basil. Serve over rice."
        ]
    },
    "Stir Fry Tofu": {
        "prep_time": "5 min", "cook_time": "10 min", "servings": 1,
        "ingredients": [
            "150g firm tofu (pressed, cubed)", "1 cup broccoli florets",
            "½ bell pepper", "1 tbsp low-sodium soy sauce (omit for soy allergy)",
            "1 tsp sesame oil", "1 tsp rice vinegar", "½ tsp ginger (grated)",
            "sesame seeds", "steamed rice"
        ],
        "steps": [
            "Press tofu between paper towels 10 min. Cut into cubes.",
            "Pan-fry tofu in sesame oil until golden, 4 min per side. Remove.",
            "Stir-fry vegetables in same pan 3 min.",
            "Return tofu, add soy sauce, vinegar and ginger. Toss and serve over rice."
        ]
    },
    "Buddha Bowl": {
        "prep_time": "10 min", "cook_time": "20 min", "servings": 1,
        "ingredients": [
            "½ cup brown rice or quinoa (cooked)", "½ cup roasted chickpeas",
            "1 cup roasted sweet potato (cubed)", "1 cup kale (massaged with oil)",
            "¼ avocado", "2 tbsp tahini dressing (tahini + lemon + water + garlic)",
            "sesame seeds"
        ],
        "steps": [
            "Roast chickpeas and sweet potato at 200°C for 20 min with oil and spices.",
            "Massage kale with a drop of olive oil until softened.",
            "Make dressing: whisk tahini, lemon juice, water, garlic and salt.",
            "Assemble bowl with grain base, all toppings and drizzle of dressing."
        ]
    },
    "Congee": {
        "prep_time": "5 min", "cook_time": "30 min", "servings": 1,
        "ingredients": [
            "¼ cup jasmine rice", "3 cups water or light stock",
            "1 tsp ginger (grated)", "1 tsp sesame oil", "1 spring onion (sliced)",
            "soft-boiled egg (optional)", "low-sodium soy sauce", "white pepper"
        ],
        "steps": [
            "Bring rice and stock to boil, reduce to low and simmer 25–30 min, stirring occasionally.",
            "Rice should break down into a thick porridge.",
            "Stir in ginger and sesame oil.",
            "Top with spring onion, egg and a splash of soy sauce."
        ]
    },

    # ─── MEXICAN ─────────────────────────────────────────────────────────
    "Veggie Fajitas": {
        "prep_time": "5 min", "cook_time": "12 min", "servings": 1,
        "ingredients": [
            "1 bell pepper (sliced)", "½ zucchini (sliced)", "½ cup black beans",
            "1 tsp cumin", "½ tsp smoked paprika", "1 tsp olive oil",
            "2 small corn tortillas (GF) or whole wheat tortillas",
            "guacamole and salsa to serve"
        ],
        "steps": [
            "Heat oil in pan over high heat.",
            "Stir-fry pepper and zucchini 5 min until charred at edges.",
            "Add black beans and spices, cook 3 min.",
            "Warm tortillas, fill with vegetable mixture and top with guacamole and salsa."
        ]
    },
    "Guacamole Salad": {
        "prep_time": "5 min", "cook_time": "0 min", "servings": 1,
        "ingredients": [
            "1 ripe avocado", "½ lime (juiced)", "½ cup cherry tomatoes (halved)",
            "¼ cup corn kernels", "1 tbsp fresh coriander",
            "salt and pepper", "rice crackers or vegetable sticks to serve"
        ],
        "steps": [
            "Mash avocado with lime juice and salt.",
            "Fold in tomatoes, corn and coriander.",
            "Season to taste.",
            "Serve immediately with crackers or vegetable sticks to prevent browning."
        ]
    },

    # ─── ITALIAN ─────────────────────────────────────────────────────────
    "Zucchini Noodles": {
        "prep_time": "10 min", "cook_time": "5 min", "servings": 1,
        "ingredients": [
            "2 medium zucchini (spiralised)", "½ cup cherry tomatoes (halved — omit for GERD)",
            "2 tbsp pesto (or olive oil + basil for dairy-free)", "¼ cup pine nuts",
            "1 tsp olive oil", "salt and pepper", "fresh basil"
        ],
        "steps": [
            "Spiralise zucchini or use a peeler to make ribbons.",
            "Heat oil in pan, add tomatoes and cook 2 min.",
            "Add zucchini noodles, toss 2 min (don't overcook — keep al dente).",
            "Remove from heat, stir in pesto, top with pine nuts and basil."
        ]
    },
    "Minestrone Soup": {
        "prep_time": "10 min", "cook_time": "25 min", "servings": 1,
        "ingredients": [
            "2 cups vegetable stock", "½ can cannellini beans", "1 carrot (diced)",
            "1 celery stalk", "½ zucchini", "½ cup spinach",
            "½ tsp dried oregano", "1 tsp olive oil", "salt and pepper",
            "GF pasta (small, optional)"
        ],
        "steps": [
            "Heat oil, sauté carrot and celery 3 min.",
            "Add stock, beans, zucchini and oregano. Bring to boil.",
            "Simmer 15 min. Add pasta if using and cook 8 min more.",
            "Add spinach last minute. Season and serve."
        ]
    },
    "Grilled Cod": {
        "prep_time": "5 min", "cook_time": "10 min", "servings": 1,
        "ingredients": [
            "150g cod fillet", "1 tbsp olive oil", "½ lemon",
            "1 tsp capers", "fresh parsley", "½ tsp dried thyme",
            "salt and pepper", "steamed green beans"
        ],
        "steps": [
            "Pat cod dry. Season with thyme, salt and pepper.",
            "Heat oil in pan over medium-high.",
            "Cook cod 4–5 min per side until flaky.",
            "Squeeze lemon over, scatter capers and parsley. Serve with green beans."
        ]
    },

    # ─── DEFAULT FALLBACK ────────────────────────────────────────────────
    "DEFAULT": {
        "prep_time": "10 min", "cook_time": "20 min", "servings": 1,
        "ingredients": [
            "Main protein or base ingredient (as named in dish)",
            "Seasonal vegetables of choice",
            "Herbs and spices to taste",
            "Healthy fat (olive oil, avocado or nuts)",
            "Salt and pepper"
        ],
        "steps": [
            "Prepare all ingredients — wash, chop and measure.",
            "Cook protein or base ingredient using preferred method (grill, bake, steam).",
            "Add vegetables and cook until tender.",
            "Season with herbs, spices and healthy fat. Serve immediately."
        ]
    },
}

def get_recipe(food_name: str) -> dict:
    """Look up recipe by food name, with fuzzy fallback."""
    # Exact match
    if food_name in RECIPES:
        return RECIPES[food_name]
    # Strip prefixes like "Spicy ", "Baked ", etc.
    prefixes = ['Spicy ','Baked ','Steamed ','Grilled ','Roasted ','Herbed ',
                'Creamy ','Tangy ','Light ','Classic ','Home-style ','Seasonal ',
                'Fresh ','Warm ','Zesty ']
    for pfx in prefixes:
        stripped = food_name.replace(pfx, '')
        if stripped in RECIPES:
            r = dict(RECIPES[stripped])
            r['_note'] = f"Recipe shown for base dish: {stripped}"
            return r
    # Partial match
    name_lower = food_name.lower()
    for key, recipe in RECIPES.items():
        if key.lower() in name_lower or name_lower in key.lower():
            r = dict(recipe)
            r['_note'] = f"Recipe shown for similar dish: {key}"
            return r
    return RECIPES["DEFAULT"]
