-- WOPR Config Service Database Schema
-- Version: 0.1.0

-- Configuration table
CREATE TABLE IF NOT EXISTS config (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT NOT NULL,
    value_type VARCHAR(50) NOT NULL DEFAULT 'string',
    description TEXT,
    environment VARCHAR(50) NOT NULL DEFAULT 'default',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Config history table for audit trail
CREATE TABLE IF NOT EXISTS config_history (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL,
    old_value TEXT,
    new_value TEXT NOT NULL,
    value_type VARCHAR(50) NOT NULL,
    environment VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100),
    change_reason TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_config_environment ON config(environment);
CREATE INDEX IF NOT EXISTS idx_config_updated_at ON config(updated_at);
CREATE INDEX IF NOT EXISTS idx_history_key ON config_history(key);
CREATE INDEX IF NOT EXISTS idx_history_changed_at ON config_history(changed_at);

-- Trigger to maintain history
CREATE OR REPLACE FUNCTION config_update_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO config_history (key, old_value, new_value, value_type, environment, changed_by)
    VALUES (OLD.key, OLD.value, NEW.value, NEW.value_type, NEW.environment, NEW.updated_by);
    
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS config_update_history ON config;
CREATE TRIGGER config_update_history
    BEFORE UPDATE ON config
    FOR EACH ROW
    EXECUTE FUNCTION config_update_trigger();

-- Insert default config values
INSERT INTO config (key, value, value_type, description, environment, updated_by)
VALUES 
    ('storage.base_path', '/mnt/nas/wopr/games', 'string', 'Base path for game storage', 'default', 'system'),
    ('camera.default_resolution', '4k', 'string', 'Default camera resolution', 'default', 'system'),
    ('camera.resolutions.4k.width', '3840', 'integer', '4K resolution width', 'default', 'system'),
    ('camera.resolutions.4k.height', '2160', 'integer', '4K resolution height', 'default', 'system'),
    ('camera.resolutions.1080p.width', '1920', 'integer', '1080p resolution width', 'default', 'system'),
    ('camera.resolutions.1080p.height', '1080', 'integer', '1080p resolution height', 'default', 'system'),
    ('logging.level', 'INFO', 'string', 'Default logging level', 'default', 'system'),
    ('logging.format', 'json', 'string', 'Log format (json or text)', 'default', 'system')
ON CONFLICT (key) DO NOTHING;
