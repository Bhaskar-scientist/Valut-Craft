# 🏦 VaultCraft — Multi-Org Transaction and Ledger Backend

**VaultCraft** is a high-integrity, production-grade backend system designed to model **real-world financial operations** — including wallet transfers between organizations, double-entry accounting, event-driven architecture, and reconciliation jobs.

Inspired by systems powering **UPI**, **Stripe Treasury**, and **RazorpayX**, VaultCraft demonstrates how real companies **move money**, maintain **ledger consistency**, and ensure **backend safety at scale**.

---

## 📌 Project Overview

VaultCraft is a **multi-tenant financial backend** designed to:

- Handle **cross-organization wallet transactions**
- Maintain strict **double-entry accounting**
- Track **transaction state** with rollback safety
- Run **reconciliation jobs** to detect inconsistencies
- Emit **transaction events** for background processing (Kafka-compatible)
- Log every sensitive action with **audit trails**

This is not a CRUD API —  
VaultCraft is a **systems engineering showcase** for transactional consistency, drift detection, and org-level financial design.

---

## 🔍 Problem It Solves

Traditional backends don’t handle:

- Transactional failure mid-transfer
- Ledger mismatch or balance drift
- Cross-org settlements or delayed clearing
- Audit trails with fine-grained actor metadata

**VaultCraft solves these by modeling:**

- Atomic wallet transfers
- Double-entry DEBIT/CREDIT ledger
- Kafka-style event pipelines
- Scheduled reconciliation jobs
- Full audit logging for accountability

---

## 🧠 Core Concepts

| Entity           | Description |
| ---------------- | ----------- |
| **Organization** | A tenant (e.g., Razorpay, HDFC Bank) |
| **User**         | Belongs to one organization |
| **Wallet**       | Stores funds; owned by a user |
| **Transaction**  | Transfers between wallets |
| **LedgerEntry**  | DEBIT/CREDIT entries per transaction |
| **EventOutbox**  | Captures events for Kafka/RabbitMQ |
| **AuditLog**     | Records sensitive operations |
| **ReconcileJob** | Scheduled worker to detect drift |
| **SettlementLog** _(Optional)_ | Logs batch settlements between orgs |

---

## ⚙️ Tech Stack

| Category         | Tools Used                      |
| ---------------- | ------------------------------ |
| Language         | Python 3.11                     |
| Web Framework    | FastAPI                         |
| ORM              | SQLAlchemy 2.0                  |
| Validation       | Pydantic v2                     |
| Database         | PostgreSQL                      |
| Auth             | JWT + bcrypt                    |
| Messaging        | Kafka or RabbitMQ               |
| Workers          | Celery + Redis                  |
| Migrations       | Alembic                         |
| CI/CD            | GitHub Actions                  |
| Containerization | Docker + docker-compose         |
| Monitoring       | Prometheus + Grafana *(optional)* |
| Testing          | Pytest + httpx + factory_boy    |

---

## 🏗️ Architecture Diagram

```txt
[ Client / API Tester ]
          ↓
     FastAPI (API Layer)
          ↓
   Service Layer (Txn Engine, Auth)
          ↓
PostgreSQL (Wallet, Transaction, Ledger)
          ↓
   Event Outbox Table (DB Triggered)
          ↓
Kafka (Transaction Events)
          ↓
Celery Workers (Reconciliation, Logging)
          ↓
Drift Detection + Audit Trail + Settlement


## 📁 Folder Structure

vaultcraft/
├── app/
│   ├── api/              # FastAPI routes
│   ├── core/             # Config, settings, utils
│   ├── db/               # DB connection & session
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic models
│   ├── services/         # Business logic: txn, ledger, auth
│   ├── events/           # Outbox logic + Kafka producer
│   ├── workers/          # Celery: reconciliation, auditing
│   └── main.py           # App entrypoint
├── alembic/              # DB migrations
├── tests/                # Unit + integration tests
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── .env


✅ Key Features
🔐 Authentication
JWT access tokens

bcrypt password hashing

Optional: 2FA / OTP extensions

💸 Wallet Transfers
Supports inter-org wallet transactions

Validations for sufficient balance

Transaction statuses: PENDING, COMPLETED, FAILED

Atomic logic with rollback safety

🧾 Double-Entry Ledger
Every transaction creates a DEBIT and CREDIT ledger row

Wallet balances derived from ledger state

📦 Event-Driven Pipeline
Kafka-compatible event emission from EventOutbox

Outbox pattern ensures reliability even if brokers fail

🔍 Reconciliation Engine
Scheduled worker compares:

wallet.balance vs SUM(ledger entries)

Flags any drift/inconsistency

Logs results in ReconcileJob

🕵️ Audit Logging
Logs every action:

Actor ID

Timestamp

Operation (e.g., TRANSFER_FUNDS)

Metadata (wallet IDs, amount, org context)



| Type             | Examples                               |
| ---------------- | -------------------------------------- |
| ✅ Unit           | Wallet debit/credit logic, hashing     |
| ✅ Integration    | Full transaction → ledger → event flow |
| ✅ Auth           | JWT expiry, role-based access          |
| ✅ Edge Cases     | Transfer with insufficient balance     |
| ✅ Failures       | Kafka broker down → retry & fallback   |
| ✅ Reconciliation | Drift found → alert generated          |


🚀 Future Extensions
VaultCraft is designed to scale — both in features and complexity. Some next steps:

🧠 Fraud detection engine (based on ledger anomalies)

📈 Analytics dashboard (org-level balance, txn volume)

🧾 Settlement system (delayed clearing between orgs)

📲 OTP / 2FA flows for sensitive operations

🌐 Admin dashboard using Streamlit or React

📊 Prometheus metrics for drift and txn lag

🧭 Project Goals
VaultCraft is built to demonstrate your ability to:

Build production-aware systems, not toy APIs

Design around failure recovery, consistency, and scale

Work with event-driven pipelines and background jobs

Think in real-world accounting logic

It’s a backend engine that proves system design awareness, not just syntax.


🛠️ Getting Started
# 1. Clone the repo
git clone https://github.com/your-username/vaultcraft.git
cd vaultcraft

# 2. Create environment file
cp .env.example .env

# 3. Run with Docker
docker-compose up --build

📫 Contact
Built by Bhaskar Reddy.
DM me on LinkedIn or Twitter to chat backend, architecture, or system design.


