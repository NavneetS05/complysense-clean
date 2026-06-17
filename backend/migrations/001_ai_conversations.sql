-- Use: Database migration script that creates the `ai_conversations` table for storing AI chatbot session histories.

-- Master-plan addition. Run only if the deployed Neon schema does not already include this table.
CREATE TABLE IF NOT EXISTS ai_conversations (
    conversation_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id    UUID REFERENCES institutions(institution_id),
    user_id           UUID REFERENCES users(user_id),
    agent_type        VARCHAR(100) NOT NULL,
    messages          JSONB NOT NULL DEFAULT '[]',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_conversations_user ON ai_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_type ON ai_conversations(agent_type);
