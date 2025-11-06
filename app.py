#!/usr/bin/env python3
"""
Clean Webhook Transaction Processor
Meets all assessment requirements with minimal complexity - No Redis needed!
"""

import asyncio
import logging
import threading
import time
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/webhook_processor")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
client = AsyncIOMotorClient(MONGODB_URL)
db = client.webhook_processor

# Pydantic Models
class WebhookRequest(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    source_account: str = Field(..., description="Source account identifier")
    destination_account: str = Field(..., description="Destination account identifier")
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO currency code")

class TransactionResponse(BaseModel):
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str
    status: str
    created_at: str
    processed_at: Optional[str] = None

class HealthResponse(BaseModel):
    status: str = "HEALTHY"
    current_time: str

# Background Processing Function
def process_transaction_background(transaction_id: str):
    """Process transaction with 30-second delay in background thread"""
    try:
        logger.info(f"Starting background processing for transaction: {transaction_id}")
        
        # 30-second delay as required
        time.sleep(30)
        
        # Update transaction status using synchronous MongoDB client
        from pymongo import MongoClient
        sync_client = MongoClient(MONGODB_URL)
        sync_db = sync_client.webhook_processor
        
        result = sync_db.transactions.update_one(
            {"transaction_id": transaction_id},
            {"$set": {
                "status": "PROCESSED",
                "processed_at": datetime.utcnow().isoformat() + "Z"
            }}
        )
        
        if result.modified_count > 0:
            logger.info(f"Transaction processed successfully: {transaction_id}")
        else:
            logger.warning(f"Failed to update transaction: {transaction_id}")
            
        sync_client.close()
        
    except Exception as e:
        logger.error(f"Error processing transaction {transaction_id}: {e}")

def start_background_processing(transaction_id: str):
    """Start background processing in a separate thread"""
    thread = threading.Thread(
        target=process_transaction_background, 
        args=(transaction_id,),
        daemon=True
    )
    thread.start()
    logger.info(f"Background processing thread started for: {transaction_id}")

# FastAPI App
app = FastAPI(
    title="Webhook Transaction Processor",
    description="Receives transaction webhooks and processes them reliably",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.on_event("startup")
async def startup_event():
    """Create database indexes on startup"""
    try:
        # Create unique index on transaction_id for idempotency
        await db.transactions.create_index("transaction_id", unique=True)
        logger.info("Database indexes created")
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="HEALTHY",
        current_time=datetime.utcnow().isoformat() + "Z"
    )

@app.post("/v1/webhooks/transactions", status_code=status.HTTP_202_ACCEPTED)
async def receive_webhook(webhook_data: WebhookRequest):
    """
    Receive transaction webhook
    - Returns 202 Accepted within 500ms
    - Handles idempotency (duplicate webhooks)
    - Queues background processing
    """
    try:
        logger.info(f"Received webhook for transaction: {webhook_data.transaction_id}")
        
        # Prepare transaction document
        transaction_doc = {
            "transaction_id": webhook_data.transaction_id,
            "source_account": webhook_data.source_account,
            "destination_account": webhook_data.destination_account,
            "amount": webhook_data.amount,
            "currency": webhook_data.currency,
            "status": "PROCESSING",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "processed_at": None
        }
        
        # Try to insert (handles idempotency with unique index)
        try:
            await db.transactions.insert_one(transaction_doc)
            logger.info(f"New transaction created: {webhook_data.transaction_id}")
            
            # Start background processing thread
            start_background_processing(webhook_data.transaction_id)
            logger.info(f"Background processing started for: {webhook_data.transaction_id}")
            
        except Exception as e:
            if "duplicate key" in str(e).lower():
                logger.info(f"Duplicate webhook ignored: {webhook_data.transaction_id}")
            else:
                raise e
        
        return {"message": "Webhook received"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )

@app.get("/v1/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_status(transaction_id: str):
    """Get transaction status"""
    try:
        logger.info(f"Getting status for transaction: {transaction_id}")
        
        # Find transaction in database
        transaction = await db.transactions.find_one({"transaction_id": transaction_id})
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction not found: {transaction_id}"
            )
        
        # Remove MongoDB _id field for response
        transaction.pop("_id", None)
        
        return TransactionResponse(**transaction)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction status"
        )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Webhook Transaction Processor...")
    print("📍 API available at: http://localhost:8000")
    print("📖 Documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)