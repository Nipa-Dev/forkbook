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
    time_minutes INTEGER,
    difficulty TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_time CHECK (time_minutes IS NULL OR time_minutes > 0)
);

CREATE TABLE ingredients (
    id TEXT PRIMARY KEY,
    recipe_id TEXT REFERENCES recipes(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    amount REAL,
    unit TEXT,
    CONSTRAINT positive_amount CHECK (amount IS NULL OR amount > 0)
);

CREATE TABLE steps (
    id TEXT PRIMARY KEY,
    recipe_id TEXT REFERENCES recipes(id) ON DELETE CASCADE,

    step_order INTEGER NOT NULL,
    description TEXT NOT NULL,
    timer_seconds INTEGER,

    CONSTRAINT unique_step_order UNIQUE (recipe_id, step_order)
);


CREATE INDEX idx_ingredients_name ON ingredients(name);
CREATE INDEX idx_ingredients_recipe ON ingredients(recipe_id);
CREATE INDEX idx_steps_recipe ON steps(recipe_id);
CREATE INDEX idx_recipes_owner ON recipes(owner_id);