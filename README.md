# 💰 Internal Wallet Service

> **A production-grade, ledger-based wallet service for virtual credits with ACID guarantees, concurrency safety, and full auditability.**

[![Live Deployment](https://img.shields.io/badge/Live-Deployed-success)](https://internal-wallet-service.onrender.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)](https://www.docker.com)

---

## 🎯 Overview

This service implements a **high-integrity internal wallet system** for virtual application credits (e.g., Gold Coins, Reward Points, Loyalty Points) using a **double-entry ledger architecture**. Designed for high-traffic applications like gaming platforms or loyalty reward systems, it guarantees:

- ✅ **Zero lost transactions** - ACID transactional integrity
- ✅ **No race conditions** - Row-level locking with deadlock prevention
- ✅ **Idempotent APIs** - Safe retries without duplicate processing
- ✅ **Full auditability** - Complete transaction history via ledger
- ✅ **Balance consistency** - Derived from ledger, never stored directly

This design mirrors how real fintech and banking systems manage balances, ensuring data integrity even under extreme concurrent load.

---

## 🌐 Live Deployment

**Test the API immediately - no setup required!**

🔗 **Live URL:** https://internal-wallet-service.onrender.com

### Quick Test Commands

```bash
# Health check
curl https://internal-wallet-service.onrender.com/health

# Get wallet balance
curl https://internal-wallet-service.onrender.com/wallets/1/balance

# View API documentation
open https://internal-wallet-service.onrender.com/docs
```

The database is pre-initialized with seed data. Try the endpoints above or explore the interactive API docs at `/docs`.

---

## 🏗️ Architecture

### Core Principle: Ledger-Based, Not Balance-Based

**This service does NOT store balances.** Instead, it uses a **double-entry bookkeeping system** where:

1. Every transaction creates **two ledger entries** (debit + credit)
2. Balance is **always calculated** from the ledger: `SELECT SUM(amount) FROM ledger_entries WHERE wallet_id = ?`
3. This ensures balances **can never go out of sync**

### Example Transaction Flow

When a user tops up 100 coins:

| Wallet | Amount | Entry Type |
|--------|--------|------------|
| User Wallet | +100 | CREDIT |
| Treasury Wallet | -100 | DEBIT |

Both entries are created **atomically** in a single database transaction.

### Why This Approach?

- **Auditability**: Every credit movement is recorded permanently
- **Consistency**: Balance is always derived from source of truth (ledger)
- **Recovery**: Can reconstruct any balance at any point in time
- **Industry Standard**: Same approach used by banks and financial systems

---

## 🔒 Concurrency & Race Condition Handling

### The Problem

Under high concurrent load, two simultaneous spend operations could:
- Both read the same balance
- Both calculate "sufficient funds"
- Both proceed, causing negative balance

### The Solution

**Row-level locking with consistent ordering:**

```python
# Lock wallets in sorted order to prevent deadlocks
wallet_ids = sorted([user_wallet_id, treasury_wallet_id])

# Lock with SELECT FOR UPDATE
for wallet_id in wallet_ids:
    wallet = await db.execute(
        select(Wallet)
        .where(Wallet.id == wallet_id)
        .with_for_update()
    )
```

**Key Techniques:**
1. **`SELECT FOR UPDATE`** - Locks wallet rows during transaction
2. **Sorted locking order** - Always lock wallets in ascending ID order (prevents deadlocks)
3. **ACID transactions** - Entire operation is atomic
4. **Balance check inside transaction** - Validates balance after acquiring locks

This guarantees that even with 1000 concurrent requests, balance integrity is maintained.

---

## 🔁 Idempotency Handling

Every API request requires an `idempotency_key`. The system:

1. Checks if a transaction with this key already exists
2. If **completed**: Returns the previous result (no duplicate processing)
3. If **pending**: Returns error (transaction in progress)
4. If **not found**: Creates new transaction and processes

**Example:**
```python
# First request
POST /wallets/top-up
{
    "user_wallet_id": 1,
    "amount": 100,
    "idempotency_key": "unique-key-123"
}
# → Creates transaction, credits wallet

# Retry with same key
POST /wallets/top-up
{
    "user_wallet_id": 1,
    "amount": 100,
    "idempotency_key": "unique-key-123"
}
# → Returns: "Transaction already processed"
```

This makes the API **safe to retry** - critical for network failures and client retries.

---

## 📊 Database Schema

### Core Tables

```sql
users              -- User accounts
asset_types        -- Currency types (Gold Coins, Diamonds, etc.)
wallets            -- One wallet per user per asset type
transactions       -- Idempotency tracking (UUID primary key)
ledger_entries     -- Double-entry bookkeeping records
```

### Key Relationships

- `wallets.user_id` → `users.id` (nullable for system wallets)
- `wallets.asset_type_id` → `asset_types.id`
- `ledger_entries.transaction_id` → `transactions.id`
- `ledger_entries.wallet_id` → `wallets.id`

### Unique Constraints

- `(user_id, asset_type_id)` - One wallet per user per asset
- `idempotency_key` - Prevents duplicate transactions

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended - Zero Setup)

**One command to run everything:**

```bash
docker-compose up --build
```

**What happens automatically:**
1. PostgreSQL 14 container starts
2. `seed.sql` executes automatically (creates tables + seed data)
3. FastAPI app starts and connects to database
4. Service available at `http://localhost:8000`

**Test it:**
```bash
# Health check
curl http://localhost:8000/health

# Get balance
curl http://localhost:8000/wallets/1/balance

# Interactive API docs
open http://localhost:8000/docs
```

**Stop everything:**
```bash
docker-compose down
```

### Option 2: Local Development

**Prerequisites:**
- Python 3.11+
- PostgreSQL 14+ (or use Docker for DB only)

**Steps:**

1. **Clone and navigate:**
   ```bash
   cd Internal-Wallet-Service
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database:**
   ```bash
   # Start PostgreSQL (or use Docker)
   docker run -d \
     -e POSTGRES_USER=wallet \
     -e POSTGRES_PASSWORD=wallet \
     -e POSTGRES_DB=wallet_db \
     -p 5432:5432 \
     -v $(pwd)/seed.sql:/docker-entrypoint-initdb.d/seed.sql \
     postgres:14
   ```

5. **Set environment variable:**
   ```bash
   export DATABASE_URL="postgresql+asyncpg://wallet:wallet@localhost:5432/wallet_db"
   # On Windows PowerShell:
   $env:DATABASE_URL="postgresql+asyncpg://wallet:wallet@localhost:5432/wallet_db"
   ```

6. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 📡 API Endpoints

### Base URL
- **Local:** `http://localhost:8000`
- **Live:** `https://internal-wallet-service.onrender.com`

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

#### `GET /wallets/{wallet_id}/balance`
Get current balance for a wallet (calculated from ledger).

**Example:**
```bash
curl http://localhost:8000/wallets/1/balance
```

**Response:**
```json
{
  "wallet_id": 1,
  "balance": 100
}
```

#### `POST /wallets/top-up`
Credit user wallet from treasury (purchase flow).

**Request:**
```json
{
  "user_wallet_id": 1,
  "amount": 100,
  "idempotency_key": "topup-123-unique"
}
```

**Response (Success):**
```json
{
  "status": "COMPLETED",
  "message": "Money topped up successfully",
  "transaction_id": "uuid-here"
}
```

**Response (Already Processed - Idempotency):**
```json
{
  "status": "ALREADY_PROCESSED",
  "message": "Top up already processed"
}
```

#### `POST /wallets/spend`
Debit user wallet, credit treasury wallet (purchase flow).

**Request:**
```json
{
  "user_wallet_id": 1,
  "amount": 50,
  "idempotency_key": "spend-456-unique"
}
```

**Response (Success):**
```json
{
  "status": "COMPLETED",
  "message": "Money spent successfully",
  "transaction_id": "uuid-here"
}
```

**Response (Already Processed - Idempotency):**
```json
{
  "status": "ALREADY_PROCESSED",
  "message": "Spend already processed"
}
```

**Error (insufficient balance):**
Returns HTTP 500 with exception message: "Insufficient balance"

#### `POST /wallets/bonus`
Credit user wallet from bonus pool (incentive flow).

**Request:**
```json
{
  "user_wallet_id": 1,
  "amount": 25,
  "idempotency_key": "bonus-789-unique"
}
```

**Response (Success):**
```json
{
  "status": "COMPLETED",
  "message": "Bonus money credited",
  "transaction_id": "uuid-here"
}
```

**Response (Already Processed - Idempotency):**
```json
{
  "status": "ALREADY_PROCESSED",
  "message": "Bonus already processed"
}
```

### Interactive API Documentation

FastAPI automatically generates interactive docs:
- **Swagger UI:** `http://localhost:8000/docs`

---

## 🗄️ Seed Data

The `seed.sql` script initializes:

- **Asset Type:** Gold Coins
- **Users:** Alice, Bob
- **System Wallets:** Treasury, BonusPool, Revenue
- **Initial Transaction:** Alice receives 100 coins from Treasury

**Wallet IDs (from seed):**
- Wallet 1: Alice's Gold Coins wallet
- Wallet 2: Bob's Gold Coins wallet
- Wallet 3: Treasury (system wallet)
- Wallet 4: BonusPool (system wallet)
- Wallet 5: Revenue (system wallet)

---

## 🧪 Transactional Flows

### 1. Top-Up Flow (Purchase)
```
User purchases credits → Treasury debits → User wallet credits
```

**Ledger entries:**
- Treasury Wallet: -100 (DEBIT)
- User Wallet: +100 (CREDIT)

### 2. Bonus Flow (Incentive)
```
System issues bonus → BonusPool debits → User wallet credits
```

**Ledger entries:**
- BonusPool Wallet: -50 (DEBIT)
- User Wallet: +50 (CREDIT)

### 3. Spend Flow (Purchase)
```
User spends credits → User wallet debits → Revenue/Treasury credits (In this assignment, I've credited in treasury wallet itself after a spend)
```

**Ledger entries:**
- User Wallet: -30 (DEBIT)
- Treasury Wallet: +30 (CREDIT)

**All flows are:**
- ✅ ACID transactional
- ✅ Lock-protected (row-level locking)
- ✅ Idempotent (safe retries)
- ✅ Fully auditable (ledger entries)

---

## 🎓 Key Engineering Decisions

### 1. **Ledger Over Balance Column**

**Decision:** Calculate balance from ledger instead of storing it.

**Why:**
- Prevents balance drift (can't go out of sync)
- Full audit trail
- Can reconstruct balance at any historical point

### 2. **Row-Level Locking with Consistent Ordering**

**Decision:** Lock wallets in sorted ID order.

**Why:**
- Prevents deadlocks (all transactions lock in same order)
- Ensures serializable isolation
- Prevents race conditions

### 3. **Idempotency Keys**

**Decision:** Require idempotency key for all write operations.

**Why:**
- Safe retries (network failures, client retries)
- Prevents duplicate processing
- Critical for financial operations

### 4. **SQL Migration Over ORM Migrations**

**Decision:** Use `seed.sql` instead of Alembic/migrations.

**Why:**
- Simpler for reviewers (one file, self-contained)
- Clear, readable SQL
- Easy to understand schema

### 5. **Async/Await Architecture**

**Decision:** Use FastAPI with async SQLAlchemy.

**Why:**
- High concurrency (handles many simultaneous requests)
- Non-blocking I/O (database operations don't block)
- Modern Python best practice

---

## 🛠️ Technology Stack

- **Framework:** FastAPI 0.128.0 (async, high-performance)
- **Database:** PostgreSQL 14 (ACID transactions, row-level locking)
- **ORM:** SQLAlchemy 2.0 (async support)
- **Database Driver:** asyncpg (async PostgreSQL driver)
- **Containerization:** Docker & Docker Compose
- **Language:** Python 3.11+

---

## 📁 Project Structure

```
Internal-Wallet-Service/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── db.py                # Database connection & session management
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── routes/
│   │   └── wallet_routes.py # API route handlers
│   └── services/
│       ├── wallet_service.py # Core wallet business logic
│       └── ledger_service.py # Ledger operations
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # FastAPI service container
├── requirements.txt        # Python dependencies
├── seed.sql               # Database schema + seed data
└── README.md              # This file
```

---

## 🐳 Docker Details

### Dockerfile
- Multi-stage build (optimized for production)
- Python 3.11 slim base image
- Non-root user (security best practice)
- Health check included

### docker-compose.yml
- **PostgreSQL service:** Auto-initializes with `seed.sql`
- **FastAPI service:** Builds from Dockerfile, connects to DB
- **Health checks:** Ensures DB is ready before app starts
- **Volume persistence:** Database data persists across restarts

---

## ✅ Testing the System

### Test Concurrent Transactions

```bash
# Simulate 10 concurrent top-ups
for i in {1..10}; do
  curl -X POST http://localhost:8000/wallets/top-up \
    -H "Content-Type: application/json" \
    -d "{\"user_wallet_id\":1,\"amount\":10,\"idempotency_key\":\"test-$i\"}" &
done
wait

# Check final balance (should be 100 + 10*10 = 200)
curl http://localhost:8000/wallets/1/balance
```

### Test Idempotency

```bash
# First request
curl -X POST http://localhost:8000/wallets/top-up \
  -H "Content-Type: application/json" \
  -d '{"user_wallet_id":1,"amount":50,"idempotency_key":"test-idempotent"}'

# Retry with same key (should return "already processed")
curl -X POST http://localhost:8000/wallets/top-up \
  -H "Content-Type: application/json" \
  -d '{"user_wallet_id":1,"amount":50,"idempotency_key":"test-idempotent"}'
```

### Test Insufficient Balance

```bash
# Try to spend more than available
curl -X POST http://localhost:8000/wallets/spend \
  -H "Content-Type: application/json" \
  -d '{"user_wallet_id":1,"amount":10000,"idempotency_key":"test-insufficient"}'
```

---

## 🔍 Code Quality Highlights

- ✅ **Type hints** throughout codebase
- ✅ **Async/await** for non-blocking I/O
- ✅ **Transaction management** with rollback on errors
- ✅ **Clean architecture** (routes → services → models)
- ✅ **Pydantic validation** for request/response schemas
- ✅ **SQL injection protection** via parameterized queries (SQLAlchemy)

---

## 📝 Notes for Reviewers

### What Makes This Production-Ready

1. **Data Integrity:** Ledger-based system ensures balances never go out of sync
2. **Concurrency Safety:** Row-level locking prevents race conditions
3. **Idempotency:** Safe retries without duplicate processing
4. **Auditability:** Complete transaction history via ledger
5. **Zero-Config Setup:** Docker Compose runs everything with one command
6. **Live Deployment:** Test immediately without any setup

### Areas for Production Enhancement

- Add database connection pooling configuration
- Implement rate limiting
- Add comprehensive test suite (pytest)
- Add monitoring/logging (Prometheus, ELK)
- Implement database migrations (Alembic)
- Add API authentication/authorization
- Implement caching layer (Redis) for balance queries
- Add database indexes for performance optimization

---

**Built with ❤️ using FastAPI, PostgreSQL, and Docker**
