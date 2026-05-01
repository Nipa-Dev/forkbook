CREATE TABLE users (
    id TEXT PRIMARY KEY,

    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,

    hashed_password TEXT NOT NULL
);


CREATE TABLE recipes (
    id TEXT PRIMARY KEY,
    owner_id TEXT REFERENCES users(id) ON DELETE SET NULL,

    title TEXT NOT NULL,
    description TEXT,

    tags TEXT[] DEFAULT '{}',

    equipment JSONB DEFAULT '[]',
    notes JSONB DEFAULT '[]',
    storage JSONB DEFAULT '[]',

    time_minutes INTEGER,
    difficulty TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_time CHECK (time_minutes IS NULL OR time_minutes > 0)
);

CREATE TABLE recipe_components (
    id TEXT PRIMARY KEY,
    recipe_id TEXT REFERENCES recipes(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    component_order INTEGER NOT NULL,

    CONSTRAINT unique_component_order UNIQUE (recipe_id, component_order)
);

CREATE TABLE ingredients (
    id TEXT PRIMARY KEY,
    component_id TEXT REFERENCES recipe_components(id) ON DELETE CASCADE,
    name TEXT NOT NULL,

    amount TEXT,
    amount_value REAL,

    unit TEXT,

    CONSTRAINT positive_amount
        CHECK (amount_value IS NULL OR amount_value > 0)
);
CREATE TABLE steps (
    id TEXT PRIMARY KEY,
    component_id TEXT REFERENCES recipe_components(id) ON DELETE CASCADE,

    step_order INTEGER NOT NULL,
    description TEXT NOT NULL,
    timer_seconds INTEGER,

    CONSTRAINT unique_step_order UNIQUE (component_id, step_order)
);

CREATE TABLE recipe_ratings (
    id TEXT PRIMARY KEY,

    recipe_id TEXT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    rating INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
    CONSTRAINT rating_range CHECK (rating >= 1 AND rating <= 5),
    CONSTRAINT unique_user_recipe_rating UNIQUE (recipe_id, user_id)
);



CREATE INDEX idx_ingredients_name ON ingredients(name);
CREATE INDEX idx_ingredients_component ON ingredients(component_id);
CREATE INDEX idx_components_recipe_order ON recipe_components(recipe_id, component_order);
CREATE INDEX idx_steps_component ON steps(component_id);
CREATE INDEX idx_recipes_owner ON recipes(owner_id);
CREATE INDEX idx_ratings_recipe ON recipe_ratings(recipe_id);
CREATE INDEX idx_ratings_user ON recipe_ratings(user_id);

