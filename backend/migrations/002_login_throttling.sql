-- Use: Database migration script adding login throttling columns to the users table.
-- Run this against an existing Neon deployment that was created from schema.sql v2.0.
-- Safe to run multiple times — uses IF NOT EXISTS pattern.

-- Add failed login attempt counter
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER NOT NULL DEFAULT 0;

-- Add block timestamp; NULL means not blocked
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS blocked_until TIMESTAMP;

-- Index helps the login query check block status quickly without a full scan
CREATE INDEX IF NOT EXISTS idx_users_blocked_until ON users(blocked_until)
    WHERE blocked_until IS NOT NULL;
