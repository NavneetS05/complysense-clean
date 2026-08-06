-- Create the persisted notifications table used by the notification repository.
CREATE TABLE IF NOT EXISTS notifications (
    notification_id text PRIMARY KEY,
    institution_id text NOT NULL,
    user_id text NOT NULL,
    title text NOT NULL,
    message text,
    notification_type text,
    related_entity_type text,
    related_entity_id text,
    is_read boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_created
    ON notifications (institution_id, user_id, created_at DESC);
