BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 0ba812a746cd

CREATE TABLE users (
    id UUID NOT NULL, 
    phone VARCHAR(20) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    company_name VARCHAR(100), 
    industry VARCHAR(50), 
    credits_balance INTEGER DEFAULT 0, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    UNIQUE (phone)
);

CREATE UNIQUE INDEX ix_users_phone ON users (phone);

CREATE TABLE plans (
    id UUID NOT NULL, 
    name VARCHAR(50) NOT NULL, 
    monthly_price NUMERIC(10, 2) NOT NULL, 
    credits_per_month INTEGER NOT NULL, 
    features JSONB, 
    status VARCHAR(20) DEFAULT 'active', 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id)
);

CREATE TABLE templates (
    id UUID NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    industry VARCHAR(50) NOT NULL, 
    thumbnail_url VARCHAR(500), 
    preview_video_url VARCHAR(500), 
    config JSONB, 
    status VARCHAR(20) DEFAULT 'active', 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id)
);

CREATE TABLE avatars (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    name VARCHAR(50) NOT NULL, 
    photo_urls JSONB, 
    material_id VARCHAR(100), 
    character_id VARCHAR(50), 
    status VARCHAR(20) DEFAULT 'pending', 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE subscriptions (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    plan_id UUID NOT NULL, 
    started_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    expired_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    status VARCHAR(20) DEFAULT 'active', 
    PRIMARY KEY (id), 
    FOREIGN KEY(plan_id) REFERENCES plans (id), 
    FOREIGN KEY(user_id) REFERENCES users (id), 
    UNIQUE (user_id)
);

CREATE TABLE credit_logs (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    amount INTEGER NOT NULL, 
    balance INTEGER NOT NULL, 
    type VARCHAR(20) NOT NULL, 
    source VARCHAR(100), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE video_tasks (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    avatar_id UUID NOT NULL, 
    template_id UUID NOT NULL, 
    script_text TEXT NOT NULL, 
    tts_audio_url VARCHAR(500), 
    video_url VARCHAR(500), 
    status VARCHAR(20) DEFAULT 'queued', 
    cost_credits INTEGER DEFAULT 0, 
    error_message TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    completed_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(avatar_id) REFERENCES avatars (id), 
    FOREIGN KEY(template_id) REFERENCES templates (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

INSERT INTO alembic_version (version_num) VALUES ('0ba812a746cd') RETURNING alembic_version.version_num;

COMMIT;

