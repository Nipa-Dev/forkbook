CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    username_normalized TEXT NOT NULL UNIQUE,
    email_bidx BLOB NOT NULL UNIQUE,
    email_enc BLOB NOT NULL,
    hashed_password TEXT NOT NULL,
    key_version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS recipes (
    id TEXT PRIMARY KEY,
    owner_id TEXT REFERENCES users(user_id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    slug TEXT NOT NULL UNIQUE,

    tags TEXT NOT NULL DEFAULT '[]',
    equipment TEXT NOT NULL DEFAULT '[]',
    notes TEXT NOT NULL DEFAULT '[]',
    storage TEXT NOT NULL DEFAULT '[]',

    cook_time_minutes INTEGER,
    prep_time_minutes INTEGER,
    servings INTEGER,

    difficulty TEXT,

    image_hero_filename TEXT,
    image_thumb_filename TEXT,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_time_cook
        CHECK (
            cook_time_minutes IS NULL
            OR cook_time_minutes >= 0
        ),

    CONSTRAINT positive_time_prep
        CHECK (
            prep_time_minutes IS NULL
            OR prep_time_minutes >= 0
        ),

    CONSTRAINT positive_servings
        CHECK (
            servings IS NULL
            OR servings > 0
        )
);


CREATE TABLE IF NOT EXISTS recipe_components (
    id TEXT PRIMARY KEY,
    recipe_id TEXT NOT NULL
        REFERENCES recipes(id)
        ON DELETE CASCADE,
    name TEXT NOT NULL,
    component_order INTEGER NOT NULL,

    CONSTRAINT unique_component_order
        UNIQUE (recipe_id, component_order)
);


CREATE TABLE IF NOT EXISTS ingredients (
    id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL
        REFERENCES recipe_components(id)
        ON DELETE CASCADE,

    raw TEXT NOT NULL,
    name TEXT,
    amount TEXT,

    amount_value NUMERIC,

    unit TEXT,

    CONSTRAINT positive_amount
        CHECK (
            amount_value IS NULL
            OR amount_value > 0
        )
);


CREATE TABLE IF NOT EXISTS steps (
    id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL
        REFERENCES recipe_components(id)
        ON DELETE CASCADE,

    step_order INTEGER NOT NULL,
    description TEXT NOT NULL,
    timer_seconds INTEGER,

    CONSTRAINT unique_step_order
        UNIQUE (component_id, step_order),

    CONSTRAINT non_negative_timer
        CHECK (
            timer_seconds IS NULL
            OR timer_seconds >= 0
        )
);


CREATE TABLE IF NOT EXISTS recipe_ratings (
    id TEXT PRIMARY KEY,

    recipe_id TEXT NOT NULL
        REFERENCES recipes(id)
        ON DELETE CASCADE,

    user_id TEXT NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    rating INTEGER NOT NULL,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT rating_range
        CHECK (rating BETWEEN 1 AND 5),

    CONSTRAINT unique_user_recipe_rating
        UNIQUE (recipe_id, user_id)
);


CREATE TABLE IF NOT EXISTS refresh_token_sessions (
    id TEXT PRIMARY KEY,

    user_id TEXT NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    token_hash TEXT NOT NULL UNIQUE,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT NOT NULL,
    last_used_at TEXT,
    revoked_at TEXT,

    rotated_from TEXT
        REFERENCES refresh_token_sessions(id),

    user_agent TEXT,
    ip_address TEXT
);


CREATE TABLE IF NOT EXISTS recipe_flags (
    id TEXT PRIMARY KEY,

    user_id TEXT NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    recipe_id TEXT NOT NULL
        REFERENCES recipes(id)
        ON DELETE CASCADE,

    flag_type TEXT NOT NULL,

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_user_recipe_flag
        UNIQUE (user_id, recipe_id, flag_type)
);


CREATE VIEW IF NOT EXISTS recipe_rating_stats AS
SELECT
    r.id AS recipe_id,
    COALESCE(AVG(rr.rating), 0.0) AS average_rating,
    COUNT(rr.id) AS total_ratings
FROM recipes r
LEFT JOIN recipe_ratings rr
    ON r.id = rr.recipe_id
GROUP BY r.id;


CREATE VIEW IF NOT EXISTS recipes_with_ratings AS
SELECT
    r.*,
    v.average_rating,
    v.total_ratings
FROM recipes r
JOIN recipe_rating_stats v
    ON r.id = v.recipe_id;


CREATE INDEX IF NOT EXISTS idx_refresh_user_id
    ON refresh_token_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_token_hash
    ON refresh_token_sessions(token_hash);
CREATE INDEX IF NOT EXISTS idx_ingredients_name
    ON ingredients(name);
CREATE INDEX IF NOT EXISTS idx_ingredients_component
    ON ingredients(component_id);
CREATE INDEX IF NOT EXISTS idx_components_recipe_order
    ON recipe_components(recipe_id, component_order);
CREATE INDEX IF NOT EXISTS idx_steps_component
    ON steps(component_id);
CREATE INDEX IF NOT EXISTS idx_ratings_recipe
    ON recipe_ratings(recipe_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user
    ON recipe_ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_recipes_owner
    ON recipes(owner_id);
