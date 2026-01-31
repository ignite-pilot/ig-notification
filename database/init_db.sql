-- Create database if not exists
-- Note: This should be run manually or through a migration tool
-- CREATE DATABASE `ig-notification`;

-- The tables will be created automatically by SQLAlchemy
-- But here's the schema for reference (MySQL compatible):

CREATE TABLE IF NOT EXISTS email_logs (
    id CHAR(36) PRIMARY KEY,
    sender_email VARCHAR(255) NOT NULL,
    recipient_emails JSON NOT NULL,
    cc_emails JSON,
    bcc_emails JSON,
    subject VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    smtp_host VARCHAR(255) NOT NULL,
    smtp_port INTEGER NOT NULL,
    use_ssl VARCHAR(10) DEFAULT 'true',
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    attachment_count INTEGER DEFAULT 0,
    total_attachment_size BIGINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME
);

CREATE INDEX IF NOT EXISTS idx_email_logs_created_at ON email_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_email_logs_status ON email_logs(status);

