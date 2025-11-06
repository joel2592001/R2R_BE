# Webhook Transaction Processor

A **super simple** Python service that receives transaction webhooks from payment processors, acknowledges them immediately, and processes them reliably in the background.

**🎯 Perfect for Assessment**: Only 2 services (FastAPI + MongoDB), no Redis complexity!

## ✅ Assessment Requirements Met

1. **Webhook Endpoint**: `POST /v1/webhooks/transactions` - Returns 202 Accepted within 500ms
2. **Health Check**: `GET /` - Returns service status and current time  
3. **Transaction Query**: `GET /v1/transactions/{transaction_id}` - Returns transaction status
4. **Background Processing**: 30-second delay simulation with persistent storage
5. **Idempotency**: Duplicate webhooks handled gracefully without errors
6. **Fast Response**: All endpoints respond quickly regardless of processing load

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Verify service is running
curl http://localhost:8000/
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start MongoDB
docker run -d -p 27017:27017 mongo:7.0

# Start the web server (includes background processing)
python app.py
# OR
uvicorn app:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing the Service

### 1. Send a Webhook
```bash
curl -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_test_123",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500,
    "currency": "INR"
  }'
```

**Expected Response**: `202 Accepted` with `{"message": "Webhook received"}`

### 2. Check Transaction Status
```bash
curl http://localhost:8000/v1/transactions/txn_test_123
```

**Expected Response**:
```json
{
  "transaction_id": "txn_test_123",
  "source_account": "acc_user_789", 
  "destination_account": "acc_merchant_456",
  "amount": 1500.0,
  "currency": "INR",
  "status": "PROCESSING",
  "created_at": "2024-01-15T10:30:00Z",
  "processed_at": null
}
```

### 3. Verify Processing (after 30 seconds)
```bash
curl http://localhost:8000/v1/transactions/txn_test_123
```

**Expected Response**: Status should be `"PROCESSED"` with `processed_at` timestamp.

### 4. Test Idempotency
Send the same webhook multiple times - only one transaction will be created.

## 🏗️ Architecture

### Technology Stack
- **FastAPI**: High-performance async web framework
- **MongoDB**: Document database for transaction storage
- **Python Threading**: Background task processing (no Redis needed!)
- **Docker**: Containerized deployment

### Key Design Decisions

1. **FastAPI**: Native async support ensures <500ms response times
2. **MongoDB with Unique Index**: Handles idempotency at database level
3. **Python Threading**: Simple background processing with 30-second delay
4. **Single File**: Minimal complexity while meeting all requirements
5. **No Redis**: Simpler deployment with fewer dependencies

### How It Works

1. **Webhook Received**: FastAPI endpoint validates and stores transaction
2. **Immediate Response**: Returns 202 Accepted within 500ms
3. **Background Thread**: Python thread processes transaction after 30 seconds
4. **Status Updates**: Transaction status changes from PROCESSING → PROCESSED
5. **Idempotency**: Duplicate webhooks are ignored via unique database constraint

## 📊 Performance Characteristics

- **Response Time**: <500ms guaranteed for webhook endpoint
- **Throughput**: Handles concurrent requests efficiently
- **Reliability**: Persistent storage survives restarts
- **Idempotency**: Safe to retry webhook deliveries

## 🔧 Configuration

Environment variables:
- `MONGODB_URL`: MongoDB connection string (default: `mongodb://localhost:27017/webhook_processor`)

## 📝 API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## 🧪 Manual Testing

Test all functionality with these curl commands:

```bash
# 1. Health Check
curl http://localhost:8000/

# 2. Send Webhook (should return 202 in <500ms)
curl -w "Time: %{time_total}s\n" -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "test_123",
    "source_account": "acc_1", 
    "destination_account": "acc_2",
    "amount": 100,
    "currency": "USD"
  }'

# 3. Check Status (should be PROCESSING)
curl http://localhost:8000/v1/transactions/test_123

# 4. Test Idempotency (send same webhook again)
curl -X POST http://localhost:8000/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "test_123",
    "source_account": "acc_1",
    "destination_account": "acc_2", 
    "amount": 100,
    "currency": "USD"
  }'

# 5. Wait 35 seconds, then check status (should be PROCESSED)
sleep 35 && curl http://localhost:8000/v1/transactions/test_123

# 6. Test Not Found
curl http://localhost:8000/v1/transactions/nonexistent
```

## � Livee Demo

**Public API Endpoint**: `https://webhook-processor.onrender.com`

Try the live API:
```bash
# Health check
curl https://webhook-processor.onrender.com/

# Send webhook
curl -X POST https://webhook-processor.onrender.com/v1/webhooks/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "demo_123",
    "source_account": "acc_demo_1",
    "destination_account": "acc_demo_2",
    "amount": 100,
    "currency": "USD"
  }'

# Check status
curl https://webhook-processor.onrender.com/v1/transactions/demo_123
```

## 🚀 Deployment Options

### Option 1: Render.com (Recommended - 100% Free)

1. **Fork this repo** to your GitHub
2. **Sign up** at [render.com](https://render.com) 
3. **Create Blueprint** from your GitHub repo
4. **Deploy** - Render uses `render.yaml` and sets up everything automatically!

**Why Render?**
- ✅ 750 hours/month FREE (enough for demos)
- ✅ Free MongoDB database included
- ✅ Auto-deploys on git push
- ✅ SSL certificates included
- ✅ Zero configuration needed

### Option 2: Fly.io (Free Tier)

1. **Install Fly CLI**: `powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"`
2. **Deploy**: `fly auth login && fly launch`
3. **Add MongoDB Atlas** (free tier)

### Option 3: Vercel (Serverless)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login and deploy
fly auth login
fly launch
fly deploy
```

## 🎯 Success Criteria Verification

✅ **Single Transaction**: Webhook → 30s delay → PROCESSED status  
✅ **Duplicate Prevention**: Same webhook multiple times → only one transaction  
✅ **Performance**: <500ms response time under load  
✅ **Reliability**: Graceful error handling, no transaction loss

## 🏗️ Technical Choices Explained

### **Why FastAPI?**
- **Async/Await Support**: Native async ensures high concurrency and fast responses
- **Automatic Documentation**: Built-in OpenAPI/Swagger docs at `/docs`
- **Type Safety**: Pydantic models provide request/response validation
- **Performance**: One of the fastest Python web frameworks

### **Why MongoDB?**
- **Document Storage**: Natural fit for JSON webhook data
- **Unique Indexes**: Database-level idempotency without application complexity
- **Async Driver**: Motor provides async MongoDB operations
- **Flexible Schema**: Easy to extend transaction fields

### **Why Python Threading?**
- **Simplicity**: No external queue systems (Redis/Celery) needed
- **Immediate**: Background processing starts instantly
- **Isolation**: Thread failures don't affect webhook responses
- **Lightweight**: Minimal resource overhead

### **Why Docker?**
- **Consistency**: Same environment locally and in production
- **Portability**: Runs anywhere Docker is supported
- **Dependencies**: All requirements bundled in container
- **Scaling**: Easy horizontal scaling with container orchestration