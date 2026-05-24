CREATE TYPE recipe_difficulty AS ENUM (
    'easy',
    'medium',
    'hard'
);

CREATE TABLE users (
    user_id UUID PRIMARY KEY,

    username TEXT NOT NULL UNIQUE,
    username_normalized TEXT NOT NULL UNIQUE,

    email_bidx BYTEA NOT NULL UNIQUE,
    email_enc BYTEA NOT NULL,

    hashed_password TEXT NOT NULL,

    key_version INTEGER NOT NULL DEFAULT 1,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE recipes (
    id UUID PRIMARY KEY,
    owner_id UUID REFERENCES users(user_id) ON DELETE SET NULL,

    title TEXT NOT NULL,
    description TEXT,
    slug TEXT NOT NULL UNIQUE,

    tags TEXT[] DEFAULT '{}',

    equipment JSONB DEFAULT '[]',
    notes JSONB DEFAULT '[]',
    storage JSONB DEFAULT '[]',

    time_minutes INTEGER,
    difficulty recipe_difficulty,
    image_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT positive_time CHECK (time_minutes IS NULL OR time_minutes > 0),
    CONSTRAINT valid_slug CHECK (slug ~ '^[a-z0-9-]+$')
);

CREATE TABLE recipe_components (
    id UUID PRIMARY KEY,
    recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    component_order INTEGER NOT NULL,

    CONSTRAINT unique_component_order UNIQUE (recipe_id, component_order)
);

CREATE TABLE ingredients (
    id UUID PRIMARY KEY,
    component_id UUID REFERENCES recipe_components(id) ON DELETE CASCADE,
    name TEXT NOT NULL,

    amount TEXT,
    amount_value NUMERIC(10,3),

    unit TEXT,

    CONSTRAINT positive_amount
        CHECK (amount_value IS NULL OR amount_value > 0)
);
CREATE TABLE steps (
    id UUID PRIMARY KEY,
    component_id UUID REFERENCES recipe_components(id) ON DELETE CASCADE,

    step_order INTEGER NOT NULL,
    description TEXT NOT NULL,
    timer_seconds INTEGER,

    CONSTRAINT unique_step_order UNIQUE (component_id, step_order)
);

CREATE TABLE recipe_ratings (
    id UUID PRIMARY KEY,

    recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    rating INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    CONSTRAINT rating_range CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT unique_user_recipe_rating UNIQUE (recipe_id, user_id)
);

CREATE TABLE refresh_token_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    last_used_at TIMESTAMPTZ,

    revoked_at TIMESTAMPTZ,
    
    rotated_from UUID REFERENCES refresh_token_sessions(id),
    
    user_agent TEXT,
    ip_address TEXT
);

CREATE INDEX idx_refresh_user_id ON refresh_token_sessions(user_id);
CREATE INDEX idx_refresh_token_hash ON refresh_token_sessions(token_hash);

CREATE INDEX idx_ingredients_name ON ingredients(name);
CREATE INDEX idx_ingredients_component ON ingredients(component_id);

CREATE INDEX idx_components_recipe_order ON recipe_components(recipe_id, component_order);
CREATE INDEX idx_steps_component ON steps(component_id);

CREATE INDEX idx_ratings_recipe ON recipe_ratings(recipe_id);
CREATE INDEX idx_ratings_user ON recipe_ratings(user_id);

CREATE INDEX idx_recipes_owner ON recipes(owner_id);
CREATE INDEX idx_recipes_tags ON recipes USING GIN (tags);

