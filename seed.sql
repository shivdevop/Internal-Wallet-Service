-- Enable uuid
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- USERS
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- ASSET TYPES (Gold Coins etc.)
CREATE TABLE asset_types (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- WALLETS
CREATE TABLE wallets (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    asset_type_id INT REFERENCES asset_types(id),
    wallet_type TEXT NOT NULL, -- USER / SYSTEM
    UNIQUE(user_id, asset_type_id)
);

-- TRANSACTIONS (Idempotency)
CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    idempotency_key TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- LEDGER (Double Entry)
CREATE TABLE ledger_entries (
    id SERIAL PRIMARY KEY,
    transaction_id UUID REFERENCES transactions(id),
    wallet_id INT REFERENCES wallets(id),
    amount BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);


-- SEED DATA

-- Asset
INSERT INTO asset_types (name) VALUES ('Gold Coins');

-- Users
INSERT INTO users (name) VALUES ('Alice'), ('Bob');

-- System users (for wallets)
INSERT INTO users (name) VALUES ('Treasury'), ('BonusPool'), ('Revenue');

-- Create wallets for all users for Gold Coins
INSERT INTO wallets (user_id, asset_type_id, wallet_type)
SELECT id, 1,
       CASE
           WHEN name IN ('Treasury','BonusPool','Revenue') THEN 'SYSTEM'
           ELSE 'USER'
       END
FROM users;

-- Give Alice initial 100 coins from Treasury
WITH txn AS (
    INSERT INTO transactions (id, idempotency_key, status)
    VALUES (uuid_generate_v4(), 'initial-seed', 'COMPLETED')
    RETURNING id
)
INSERT INTO ledger_entries (transaction_id, wallet_id, amount)
SELECT txn.id, w.id,
       CASE
           WHEN u.name = 'Alice' THEN 100
           WHEN u.name = 'Treasury' THEN -100
       END
FROM wallets w
JOIN users u ON w.user_id = u.id, txn
WHERE u.name IN ('Alice', 'Treasury');
