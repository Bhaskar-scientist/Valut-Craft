# 🏦 VaultCraft — Multi-Org Transaction and Ledger Backend

**VaultCraft** is a high-integrity, production-grade backend system designed to model **real-world financial operations** — including wallet transfers between organizations, double-entry accounting, event-driven architecture, and reconciliation jobs.

Inspired by systems powering **UPI**, **Stripe Treasury**, and **RazorpayX**, VaultCraft demonstrates how real companies **move money**, maintain **ledger consistency**, and ensure **backend safety at scale**.

---

## 🚀 **Current Status: Phase 1 Complete!**

VaultCraft Phase 1 is now a **transactionally consistent, multi-tenant, ledger-backed financial core** for internal (same-org) wallet operations. Think of it like the internal ops layer in RazorpayX, Stripe Treasury, or a private UPI bank node.

### ✅ **What's Built (Phase 1 Complete)**

- **🔐 Multi-Tenant Authentication System**
  - JWT-based authentication with bcrypt password hashing
  - Organization and user management with proper isolation
  - Protected routes with tenant scoping

- **💰 Wallet Management Engine**
  - Multi-wallet support per user (PRIMARY, BONUS, SYSTEM)
  - Balance tracking with atomic operations
  - Wallet status management (ACTIVE, LOCKED, CLOSED)

- **🔁 Transaction Engine**
  - Atomic internal transfers between wallets
  - Double-entry ledger system (DEBIT/CREDIT)
  - Transaction status management (PENDING, COMPLETED, FAILED, CANCELLED)
  - Rollback safety and consistency guarantees

- **📊 API Layer**
  - RESTful API with proper HTTP status codes
  - OpenAPI documentation with Swagger UI
  - Comprehensive error handling and validation
  - Pagination and filtering support

- **🏗️ Infrastructure**
  - Docker and docker-compose setup
  - PostgreSQL with SQLAlchemy 2.0 async ORM
  - Alembic database migrations
  - GitHub Actions CI/CD pipeline

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

Traditional backends don't handle:

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

## ⚙️ Tech Stack (Phase 1)

| Category         | Tools Used                      |
| ---------------- | ------------------------------ |
| Language         | Python 3.11                     |
| Web Framework    | FastAPI                         |
| ORM              | SQLAlchemy 2.0                  |
| Validation       | Pydantic v2                     |
| Database         | PostgreSQL                      |
| Auth             | JWT + bcrypt                    |
| Containerization | Docker + docker-compose         |
| Migrations       | Alembic                         |
| CI/CD            | GitHub Actions                  |
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
Kafka (Transaction Events) [Future]
          ↓
Celery Workers (Reconciliation, Logging) [Future]
          ↓
Drift Detection + Audit Trail + Settlement [Future]

```

---

## 📁 Folder Structure

```txt
vaultcraft/
├── app/
│   ├── api/              # FastAPI routes
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── wallets.py    # Wallet management
│   │   └── transactions.py # Transaction engine
│   ├── core/             # Config, settings, utils
│   │   ├── config.py     # Application configuration
│   │   └── auth.py       # JWT and auth utilities
│   ├── db/               # DB connection & session
│   │   └── session.py    # Database session management
│   ├── models/           # SQLAlchemy models
│   │   ├── base.py       # Base model class
│   │   ├── organization.py # Organization model
│   │   ├── user.py       # User model
│   │   ├── wallet.py     # Wallet model
│   │   ├── transaction.py # Transaction model
│   │   └── ledger_entry.py # Ledger entry model
│   ├── schemas/          # Pydantic models
│   │   ├── auth.py       # Auth request/response schemas
│   │   ├── wallet.py     # Wallet schemas
│   │   └── transaction.py # Transaction schemas
│   ├── services/         # Business logic
│   │   ├── auth_service.py # Authentication service
│   │   ├── wallet_service.py # Wallet operations
│   │   └── transaction_service.py # Transaction engine
│   └── main.py           # App entrypoint
├── alembic/              # DB migrations
├── tests/                # Unit + integration tests
├── docker-compose.yml    # Local development setup
├── Dockerfile            # Container configuration
├── requirements.txt      # Python dependencies
├── pytest.ini           # Test configuration
├── .github/workflows/    # CI/CD pipeline
└── README.md
```

---

## ✅ Key Features (Phase 1)

### 🔐 Authentication
- JWT access tokens with configurable expiration
- bcrypt password hashing
- Multi-tenant user isolation
- Organization-based access control

### 💸 Wallet Operations
- Create multiple wallet types (PRIMARY, BONUS, SYSTEM)
- Atomic balance updates via transactions only
- Wallet status management
- Multi-currency support (INR default)

### 🔁 Transaction Engine
- Internal transfers between wallets
- Atomic operations with rollback safety
- Double-entry ledger (DEBIT/CREDIT)
- Transaction status tracking
- Comprehensive audit trail

### 📦 API Design
- RESTful endpoints with proper HTTP status codes
- Request/response validation with Pydantic
- Pagination and filtering support
- Comprehensive error handling
- OpenAPI documentation

### 🧪 Testing & Quality
- Pytest test suite with async support
- Test coverage reporting
- GitHub Actions CI/CD pipeline
- Code quality checks (linting, security)

---

## 🚀 Getting Started

### Prerequisites
- Docker and docker-compose
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/vaultcraft.git
   cd vaultcraft
   ```

2. **Setup environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup database**
   ```bash
   # Create PostgreSQL database
   createdb vaultcraft
   
   # Run migrations
   alembic upgrade head
   ```

3. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### Test Coverage
- Unit tests for services and utilities
- Integration tests for API endpoints
- Database transaction testing
- Authentication flow testing

---

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/auth/me` - Current user info

### Wallet Endpoints
- `POST /api/v1/wallets/` - Create wallet
- `GET /api/v1/wallets/` - List user wallets
- `GET /api/v1/wallets/{id}` - Get wallet details
- `POST /api/v1/wallets/transfer` - Transfer funds
- `GET /api/v1/wallets/summary` - Organization summary

### Transaction Endpoints
- `POST /api/v1/transactions/transfer` - Create transfer
- `GET /api/v1/transactions/` - List transactions
- `GET /api/v1/transactions/{id}` - Get transaction details
- `GET /api/v1/transactions/{id}/ledger` - Get ledger entries
- `POST /api/v1/transactions/{id}/cancel` - Cancel transaction

---

## 🔮 Future Roadmap

### Phase 2: Event System & Background Jobs
- [ ] Outbox pattern implementation
- [ ] Kafka/RabbitMQ integration
- [ ] Celery worker setup
- [ ] Event-driven transaction processing

### Phase 3: Advanced Features
- [ ] Reconciliation engine
- [ ] Cross-organization settlements
- [ ] Fraud detection system
- [ ] Analytics dashboard

### Phase 4: Production Features
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Advanced monitoring
- [ ] Performance optimization

---

## 🛠️ Development

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints throughout
- Write comprehensive docstrings
- Maintain test coverage above 80%

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

## 📫 Contact

Built by [Bhaskar Reddy](bento.me/bhaskar-reddy).

DM me on [LinkedIn](https://www.linkedin.com/in/bhaskar-reddy-sde/) or [X](https://x.com/ShipWithBhaskar) to chat backend, architecture, or system design.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


