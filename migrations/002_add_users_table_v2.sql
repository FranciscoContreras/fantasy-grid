-- Migration: Add users table for authentication (v2 - handles existing data)
-- Created: 2025-10-02
-- Purpose: Implement user authentication system with data migration

-- Step 1: Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMP,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- Step 3: Create a default/system user for existing rosters
INSERT INTO users (id, email, username, password_hash, first_name, is_active)
VALUES (1, 'system@fantasy-grid.local', 'default_user', 'PLACEHOLDER_HASH', 'Default User', true)
ON CONFLICT (id) DO NOTHING;

-- Step 4: Create new user_id_new column that's an integer
ALTER TABLE rosters ADD COLUMN IF NOT EXISTS user_id_new INTEGER;

-- Step 5: Migrate existing data (set all to default user ID 1)
UPDATE rosters SET user_id_new = 1 WHERE user_id_new IS NULL;

-- Step 6: Drop old user_id column and rename new one
ALTER TABLE rosters DROP COLUMN IF EXISTS user_id CASCADE;
ALTER TABLE rosters RENAME COLUMN user_id_new TO user_id;

-- Step 7: Add foreign key constraint
ALTER TABLE rosters
    ADD CONSTRAINT fk_rosters_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Step 8: Add NOT NULL constraint
ALTER TABLE rosters ALTER COLUMN user_id SET NOT NULL;

-- Step 9: Create index on rosters.user_id
CREATE INDEX IF NOT EXISTS idx_rosters_user_id ON rosters(user_id);

-- Step 10: Update user_preferences table similarly
ALTER TABLE user_preferences ADD COLUMN IF NOT EXISTS user_id_new INTEGER;
UPDATE user_preferences SET user_id_new = 1 WHERE user_id_new IS NULL;
ALTER TABLE user_preferences DROP COLUMN IF EXISTS user_id CASCADE;
ALTER TABLE user_preferences RENAME COLUMN user_id_new TO user_id;
ALTER TABLE user_preferences
    ADD CONSTRAINT fk_user_preferences_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE user_preferences ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE user_preferences ADD CONSTRAINT user_preferences_user_id_unique UNIQUE (user_id);

-- Step 11: Create sessions table for JWT token blacklisting (logout)
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_token_jti ON user_sessions(token_jti);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Step 12: Create password reset tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);

-- Success message
SELECT 'Migration 002 completed successfully' AS status;
