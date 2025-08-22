# VaultCraft API - How to Use Guide

**Complete Step-by-Step Guide for Performing Transactions**

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Prerequisites](#prerequisites)
3. [Step 1: User Registration](#step-1-user-registration)
4. [Step 2: User Login](#step-2-user-login)
5. [Step 3: Create Wallets](#step-3-create-wallets)
6. [Step 4: Check Wallet Balance](#step-4-check-wallet-balance)
7. [Step 5: Perform Transaction](#step-5-perform-transaction)
8. [Step 6: View Transaction History](#step-6-view-transaction-history)
9. [API Reference](#api-reference)
10. [Error Handling](#error-handling)
11. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

VaultCraft is a multi-tenant financial backend system that allows you to:
- Create and manage user accounts and organizations
- Create multiple wallet types (PRIMARY, BONUS, SYSTEM)
- Perform secure internal transfers between wallets
- Maintain complete audit trails and transaction history

**Base URL:** `http://localhost:8000`

---

## 🔧 Prerequisites

Before starting, ensure:
1. VaultCraft application is running on `http://localhost:8000`
2. You have a tool to make HTTP requests (Postman, curl, PowerShell, etc.)
3. Basic understanding of REST APIs and JSON

**Quick Health Check:**
```bash
GET http://localhost:8000/health
```
Expected response:
```json
{
  "status": "healthy",
  "service": "VaultCraft",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 📝 Step 1: User Registration

**Purpose:** Create a new user account and organization to get started with VaultCraft.

### Request Details:
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/v1/auth/signup`
- **Content-Type:** `application/json`

### Request Body:
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123",
  "organization_name": "Acme Corporation"
}
```

### Example using PowerShell:
```powershell
$signupData = @{
    email = "john.doe@example.com"
    password = "SecurePassword123"
    organization_name = "Acme Corporation"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/signup" -Method Post -Body $signupData -ContentType "application/json"
$token = $response.access_token
Write-Host "Access Token: $token"
```

### Example using curl:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "SecurePassword123",
    "organization_name": "Acme Corporation"
  }'
```

### Expected Response (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john.doe@example.com",
    "org_id": "660e8400-e29b-41d4-a716-446655440001"
  }
}
```

**⚠️ Important:** Save the `access_token` - you'll need it for all subsequent requests!

---

## 🔐 Step 2: User Login

**Purpose:** Authenticate with existing credentials to get a fresh access token.

### Request Details:
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/v1/auth/login`
- **Content-Type:** `application/json`

### Request Body:
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123"
}
```

### Example using PowerShell:
```powershell
$loginData = @{
    email = "john.doe@example.com"
    password = "SecurePassword123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $loginData -ContentType "application/json"
$token = $response.access_token
Write-Host "Access Token: $token"
```

### Expected Response (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john.doe@example.com",
    "org_id": "660e8400-e29b-41d4-a716-446655440001"
  }
}
```

---

## 💼 Step 3: Create Wallets

**Purpose:** Create wallets to hold funds and perform transactions. You need at least 2 wallets to perform transfers.

### Wallet Types Available:
- **PRIMARY**: Main wallet (one per user, created automatically)
- **BONUS**: For bonus/reward funds
- **SYSTEM**: For system-related transactions

### Request Details:
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/v1/wallets/`
- **Content-Type:** `application/json`
- **Authorization:** `Bearer YOUR_ACCESS_TOKEN`

### Create First Wallet (BONUS):

#### Request Body:
```json
{
  "name": "Bonus Wallet",
  "type": "BONUS",
  "currency": "INR"
}
```

#### Example using PowerShell:
```powershell
$token = "YOUR_ACCESS_TOKEN_HERE"
$walletData = @{
    name = "Bonus Wallet"
    type = "BONUS"
    currency = "INR"
} | ConvertTo-Json

$wallet1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/wallets/" -Method Post -Body $walletData -ContentType "application/json" -Headers @{"Authorization" = "Bearer $token"}
Write-Host "Bonus Wallet ID: $($wallet1.id)"
```

#### Expected Response (201 Created):
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "balance": "0.00",
  "currency": "INR",
  "org_id": "660e8400-e29b-41d4-a716-446655440001",
  "type": "BONUS",
  "status": "ACTIVE",
  "created_at": "2025-01-01T10:00:00.000000"
}
```

### Create Second Wallet (SYSTEM):

#### Request Body:
```json
{
  "name": "System Wallet",
  "type": "SYSTEM",
  "currency": "INR"
}
```

#### Example using PowerShell:
```powershell
$walletData2 = @{
    name = "System Wallet"
    type = "SYSTEM"
    currency = "INR"
} | ConvertTo-Json

$wallet2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/wallets/" -Method Post -Body $walletData2 -ContentType "application/json" -Headers @{"Authorization" = "Bearer $token"}
Write-Host "System Wallet ID: $($wallet2.id)"
```

**💡 Save both wallet IDs - you'll need them for transactions!**

---

## 💰 Step 4: Check Wallet Balance

**Purpose:** Verify wallet balance before performing transactions.

### Request Details:
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/v1/wallets/{wallet_id}/balance`
- **Authorization:** `Bearer YOUR_ACCESS_TOKEN`

### Example using PowerShell:
```powershell
$walletId = "770e8400-e29b-41d4-a716-446655440002"
$balance = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/wallets/$walletId/balance" -Method Get -Headers @{"Authorization" = "Bearer $token"}
Write-Host "Wallet Balance: $($balance.balance) $($balance.currency)"
```

### Expected Response (200 OK):
```json
{
  "wallet_id": "770e8400-e29b-41d4-a716-446655440002",
  "balance": "0.00",
  "currency": "INR",
  "last_updated": "2025-01-01T10:00:00.000000"
}
```

**📝 Note:** New wallets start with 0.00 balance. In a production system, you would need to fund wallets through external payment gateways or administrative functions.

---

## 🔄 Step 5: Perform Transaction

**Purpose:** Transfer funds between your wallets.

### Request Details:
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/v1/transactions/transfer`
- **Content-Type:** `application/json`
- **Authorization:** `Bearer YOUR_ACCESS_TOKEN`

### Request Body:
```json
{
  "sender_wallet_id": "770e8400-e29b-41d4-a716-446655440002",
  "receiver_wallet_id": "880e8400-e29b-41d4-a716-446655440003",
  "amount": "100.00",
  "description": "Bonus transfer to system wallet",
  "reference_id": "TXN-2025-001"
}
```

### Example using PowerShell:
```powershell
$transactionData = @{
    sender_wallet_id = "770e8400-e29b-41d4-a716-446655440002"
    receiver_wallet_id = "880e8400-e29b-41d4-a716-446655440003"
    amount = "100.00"
    description = "Bonus transfer to system wallet"
    reference_id = "TXN-2025-001"
} | ConvertTo-Json

$transaction = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/transactions/transfer" -Method Post -Body $transactionData -ContentType "application/json" -Headers @{"Authorization" = "Bearer $token"}
Write-Host "Transaction ID: $($transaction.transaction_id)"
```

### Expected Response (200 OK):
```json
{
  "transaction_id": "990e8400-e29b-41d4-a716-446655440004",
  "status": "COMPLETED",
  "message": "Transfer completed successfully",
  "sender_wallet_id": "770e8400-e29b-41d4-a716-446655440002",
  "receiver_wallet_id": "880e8400-e29b-41d4-a716-446655440003",
  "amount": "100.00",
  "timestamp": "2025-01-01T10:30:00.000000"
}
```

### Common Error Response (400 Bad Request):
```json
{
  "detail": "Insufficient balance in sender wallet"
}
```

**🚨 Important Business Rules:**
- Sender wallet must have sufficient balance
- Sender and receiver wallets must be different
- Amount must be positive
- Both wallets must belong to the authenticated user

---

## 📊 Step 6: View Transaction History

**Purpose:** View all transactions for audit and tracking purposes.

### Request Details:
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/v1/transactions/`
- **Authorization:** `Bearer YOUR_ACCESS_TOKEN`

### Query Parameters (Optional):
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

### Example using PowerShell:
```powershell
$transactions = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/transactions/?page=1&page_size=10" -Method Get -Headers @{"Authorization" = "Bearer $token"}
Write-Host "Total Transactions: $($transactions.total_count)"
$transactions.transactions | Format-Table
```

### Expected Response (200 OK):
```json
{
  "transactions": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "type": "TRANSFER",
      "status": "COMPLETED",
      "amount": "100.00",
      "currency": "INR",
      "description": "Bonus transfer to system wallet",
      "reference_id": "TXN-2025-001",
      "sender_wallet_id": "770e8400-e29b-41d4-a716-446655440002",
      "receiver_wallet_id": "880e8400-e29b-41d4-a716-446655440003",
      "created_at": "2025-01-01T10:30:00.000000",
      "completed_at": "2025-01-01T10:30:01.000000"
    }
  ],
  "total_count": 1,
  "page": 1,
  "page_size": 20
}
```

---

## 📚 API Reference

### Authentication Endpoints:
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register new user and organization |
| POST | `/api/v1/auth/login` | Login with existing credentials |

### Wallet Endpoints:
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/wallets/` | Create a new wallet |
| GET | `/api/v1/wallets/` | List all user wallets |
| GET | `/api/v1/wallets/{wallet_id}` | Get specific wallet details |
| GET | `/api/v1/wallets/{wallet_id}/balance` | Get wallet balance |

### Transaction Endpoints:
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/transactions/transfer` | Create internal transfer |
| GET | `/api/v1/transactions/` | List all transactions |
| GET | `/api/v1/transactions/{transaction_id}` | Get specific transaction |

### Health Check:
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Application health status |
| GET | `/api/v1/health` | API health status |

---

## ⚠️ Error Handling

### Common HTTP Status Codes:
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server error

### Common Error Responses:

#### Validation Error (422):
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required"
    }
  ]
}
```

#### Authentication Error (401):
```json
{
  "detail": "Could not validate credentials"
}
```

#### Business Logic Error (400):
```json
{
  "detail": "User already has an active primary wallet"
}
```

---

## 🔧 Troubleshooting

### Issue: "Could not validate credentials"
**Solution:** 
- Ensure you're including the Authorization header
- Check that your token hasn't expired
- Verify the token format: `Bearer YOUR_TOKEN`

### Issue: "Insufficient balance in sender wallet"
**Solution:**
- Check wallet balance using the balance endpoint
- Ensure you're transferring from a wallet with sufficient funds
- In development, you may need to manually fund wallets

### Issue: "User already has an active primary wallet"
**Solution:**
- Users can only have one PRIMARY wallet
- Use BONUS or SYSTEM wallet types for additional wallets

### Issue: "Sender and receiver wallets must be different"
**Solution:**
- Ensure you're not transferring to the same wallet
- Double-check wallet IDs in your request

### Issue: Connection errors
**Solution:**
- Verify VaultCraft is running: `GET http://localhost:8000/health`
- Check Docker containers are up: `docker ps`
- Ensure correct port (8000) is being used

---

## 🎯 Complete Example Workflow

Here's a complete PowerShell script that demonstrates the entire transaction flow:

```powershell
# 1. Register new user
$signupData = @{
    email = "demo.user@example.com"
    password = "DemoPassword123"
    organization_name = "Demo Corp"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/signup" -Method Post -Body $signupData -ContentType "application/json"
$token = $response.access_token
Write-Host "✅ User registered. Token: $($token.Substring(0,20))..."

# 2. Create first wallet (BONUS)
$wallet1Data = @{
    name = "Demo Bonus Wallet"
    type = "BONUS"
    currency = "INR"
} | ConvertTo-Json

$wallet1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/wallets/" -Method Post -Body $wallet1Data -ContentType "application/json" -Headers @{"Authorization" = "Bearer $token"}
Write-Host "✅ Bonus wallet created: $($wallet1.id)"

# 3. Create second wallet (SYSTEM)
$wallet2Data = @{
    name = "Demo System Wallet"
    type = "SYSTEM"
    currency = "INR"
} | ConvertTo-Json

$wallet2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/wallets/" -Method Post -Body $wallet2Data -ContentType "application/json" -Headers @{"Authorization" = "Bearer $token"}
Write-Host "✅ System wallet created: $($wallet2.id)"

# 4. Check wallet balances
$balance1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/wallets/$($wallet1.id)/balance" -Method Get -Headers @{"Authorization" = "Bearer $token"}
$balance2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/wallets/$($wallet2.id)/balance" -Method Get -Headers @{"Authorization" = "Bearer $token"}
Write-Host "💰 Bonus wallet balance: $($balance1.balance) $($balance1.currency)"
Write-Host "💰 System wallet balance: $($balance2.balance) $($balance2.currency)"

# 5. Attempt transaction (will fail with insufficient balance)
$transactionData = @{
    sender_wallet_id = $wallet1.id
    receiver_wallet_id = $wallet2.id
    amount = "50.00"
    description = "Demo transfer"
    reference_id = "DEMO-TXN-001"
} | ConvertTo-Json

try {
    $transaction = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/transactions/transfer" -Method Post -Body $transactionData -ContentType "application/json" -Headers @{"Authorization" = "Bearer $token"}
    Write-Host "✅ Transaction completed: $($transaction.transaction_id)"
} catch {
    Write-Host "❌ Transaction failed: $($_.Exception.Response.StatusDescription)"
    Write-Host "   This is expected for new wallets with 0 balance"
}

# 6. View transaction history
$history = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/transactions/" -Method Get -Headers @{"Authorization" = "Bearer $token"}
Write-Host "📊 Total transactions: $($history.total_count)"
```

---

## 📞 Support

For technical issues or questions:
- Check the application logs for detailed error messages
- Verify all prerequisites are met
- Ensure proper JSON formatting in requests
- Test with the health endpoint first

**API Documentation:** Available at `http://localhost:8000/docs` when the application is running.

---

**Happy transacting with VaultCraft! 🚀**
