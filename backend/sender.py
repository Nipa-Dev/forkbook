import niquests
import json

recipes = [
    {
        "title": "Spaghetti Carbonara",
        "description": "Classic Italian pasta with creamy egg sauce and pancetta.",
        "ingredients": [
            {"name": "Spaghetti", "amount": 400, "unit": "g"},
            {"name": "Pancetta", "amount": 150, "unit": "g"},
            {"name": "Eggs", "amount": 4, "unit": "pcs"},
            {"name": "Parmesan cheese", "amount": 50, "unit": "g"},
            {"name": "Black pepper", "amount": 1, "unit": "tsp"},
            {"name": "Salt", "amount": 1, "unit": "tsp"},
        ],
        "steps": [
            {
                "step_order": 1,
                "description": "Boil spaghetti in salted water until al dente.",
                "timer_seconds": 600,
            },
            {
                "step_order": 2,
                "description": "Fry pancetta until crispy.",
                "timer_seconds": 300,
            },
            {
                "step_order": 3,
                "description": "Beat eggs with grated Parmesan and pepper.",
                "timer_seconds": 120,
            },
            {
                "step_order": 4,
                "description": "Combine pasta with pancetta and remove from heat.",
                "timer_seconds": 60,
            },
            {
                "step_order": 5,
                "description": "Quickly stir in egg mixture until creamy.",
                "timer_seconds": 120,
            },
        ],
        "tags": ["Italian", "Pasta", "Quick"],
        "time_minutes": 20,
        "difficulty": "Medium",
    },
    {
        "title": "Chicken Curry",
        "description": "A flavorful and spicy chicken curry with a rich sauce.",
        "ingredients": [
            {"name": "Chicken thighs", "amount": 500, "unit": "g"},
            {"name": "Onion", "amount": 1, "unit": "pc"},
            {"name": "Garlic cloves", "amount": 3, "unit": "pcs"},
            {"name": "Curry powder", "amount": 2, "unit": "tbsp"},
            {"name": "Coconut milk", "amount": 400, "unit": "ml"},
            {"name": "Vegetable oil", "amount": 2, "unit": "tbsp"},
            {"name": "Salt", "amount": 1, "unit": "tsp"},
        ],
        "steps": [
            {
                "step_order": 1,
                "description": "Chop onion and garlic, sauté in oil until soft.",
                "timer_seconds": 300,
            },
            {
                "step_order": 2,
                "description": "Add chicken and brown on all sides.",
                "timer_seconds": 400,
            },
            {
                "step_order": 3,
                "description": "Stir in curry powder and cook for 2 minutes.",
                "timer_seconds": 120,
            },
            {
                "step_order": 4,
                "description": "Pour in coconut milk, simmer until chicken is cooked.",
                "timer_seconds": 900,
            },
            {
                "step_order": 5,
                "description": "Season with salt and serve with rice.",
                "timer_seconds": 60,
            },
        ],
        "tags": ["Indian", "Spicy", "Dinner"],
        "time_minutes": 30,
        "difficulty": "Medium",
    },
    {
        "title": "Fluffy Pancakes",
        "description": "Soft and fluffy breakfast pancakes with syrup.",
        "ingredients": [
            {"name": "All-purpose flour", "amount": 200, "unit": "g"},
            {"name": "Milk", "amount": 250, "unit": "ml"},
            {"name": "Egg", "amount": 1, "unit": "pc"},
            {"name": "Baking powder", "amount": 2, "unit": "tsp"},
            {"name": "Sugar", "amount": 2, "unit": "tbsp"},
            {"name": "Butter", "amount": 30, "unit": "g"},
            {"name": "Salt", "amount": 0.5, "unit": "tsp"},
        ],
        "steps": [
            {
                "step_order": 1,
                "description": "Mix dry ingredients in a bowl.",
                "timer_seconds": 120,
            },
            {
                "step_order": 2,
                "description": "Whisk milk and egg, then combine with dry mix.",
                "timer_seconds": 180,
            },
            {
                "step_order": 3,
                "description": "Heat butter in pan, pour batter to form pancakes.",
                "timer_seconds": 300,
            },
            {
                "step_order": 4,
                "description": "Cook until bubbles appear, flip and cook the other side.",
                "timer_seconds": 300,
            },
        ],
        "tags": ["Breakfast", "Sweet", "Quick"],
        "time_minutes": 15,
        "difficulty": "Easy",
    },
    {
        "title": "Guacamole",
        "description": "Creamy avocado dip perfect for chips or tacos.",
        "ingredients": [
            {"name": "Avocados", "amount": 3, "unit": "pcs"},
            {"name": "Lime juice", "amount": 2, "unit": "tbsp"},
            {"name": "Red onion", "amount": 0.5, "unit": "pc"},
            {"name": "Cilantro", "amount": 2, "unit": "tbsp"},
            {"name": "Salt", "amount": 0.5, "unit": "tsp"},
            {"name": "Tomato", "amount": 1, "unit": "pc"},
        ],
        "steps": [
            {
                "step_order": 1,
                "description": "Mash avocados in a bowl.",
                "timer_seconds": 120,
            },
            {
                "step_order": 2,
                "description": "Add lime juice, chopped onion, tomato, and cilantro.",
                "timer_seconds": 180,
            },
            {
                "step_order": 3,
                "description": "Season with salt and mix well.",
                "timer_seconds": 60,
            },
        ],
        "tags": ["Mexican", "Appetizer", "Vegan"],
        "time_minutes": 10,
        "difficulty": "Easy",
    },
    {
        "title": "Beef Stir Fry",
        "description": "Quick Asian-style beef stir fry with vegetables.",
        "ingredients": [
            {"name": "Beef sirloin", "amount": 400, "unit": "g"},
            {"name": "Bell peppers", "amount": 2, "unit": "pcs"},
            {"name": "Soy sauce", "amount": 3, "unit": "tbsp"},
            {"name": "Garlic cloves", "amount": 2, "unit": "pcs"},
            {"name": "Vegetable oil", "amount": 2, "unit": "tbsp"},
            {"name": "Cornstarch", "amount": 1, "unit": "tsp"},
        ],
        "steps": [
            {
                "step_order": 1,
                "description": "Slice beef thinly and coat with cornstarch.",
                "timer_seconds": 120,
            },
            {
                "step_order": 2,
                "description": "Heat oil, stir fry garlic until fragrant.",
                "timer_seconds": 60,
            },
            {
                "step_order": 3,
                "description": "Add beef and cook until browned.",
                "timer_seconds": 300,
            },
            {
                "step_order": 4,
                "description": "Add bell peppers and soy sauce, cook until vegetables soften.",
                "timer_seconds": 300,
            },
        ],
        "tags": ["Asian", "Quick", "Dinner"],
        "time_minutes": 20,
        "difficulty": "Medium",
    },
    {
        "title": "Chocolate Chip Cookies",
        "description": "Crispy on the edges, chewy in the center chocolate chip cookies.",
        "ingredients": [
            {"name": "All-purpose flour", "amount": 250, "unit": "g"},
            {"name": "Butter", "amount": 125, "unit": "g"},
            {"name": "Sugar", "amount": 100, "unit": "g"},
            {"name": "Brown sugar", "amount": 100, "unit": "g"},
            {"name": "Egg", "amount": 1, "unit": "pc"},
            {"name": "Vanilla extract", "amount": 1, "unit": "tsp"},
            {"name": "Chocolate chips", "amount": 150, "unit": "g"},
            {"name": "Baking soda", "amount": 1, "unit": "tsp"},
            {"name": "Salt", "amount": 0.5, "unit": "tsp"},
        ],
        "steps": [
            {
                "step_order": 1,
                "description": "Preheat oven to 180°C and line a baking tray.",
                "timer_seconds": 600,
            },
            {
                "step_order": 2,
                "description": "Cream butter and sugars, then add egg and vanilla.",
                "timer_seconds": 180,
            },
            {
                "step_order": 3,
                "description": "Mix in flour, baking soda, salt, and chocolate chips.",
                "timer_seconds": 300,
            },
            {
                "step_order": 4,
                "description": "Scoop dough onto tray and bake 10-12 minutes.",
                "timer_seconds": 720,
            },
        ],
        "tags": ["Dessert", "Sweet", "Baking"],
        "time_minutes": 25,
        "difficulty": "Easy",
    },
]
check = input("Are you sure you want to send POST to /recipes/new? n/Y: ").lower()
if check == "y":
    for recipe in recipes:
        response = niquests.post(
            "http://127.0.0.1:8000/recipe/new",
            headers={"Content-Type": "application/json"},
            data=json.dumps(recipe),
        )
        if response.status_code == 200:
            print(f"Successfully added: {recipe['title']}")
        else:
            print(
                f"Failed to add: {recipe['title']} | Status: {response.status_code} | Response: {response.text}"
            )

else:
    print("Aborting")