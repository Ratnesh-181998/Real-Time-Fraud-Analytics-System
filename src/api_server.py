"""
FastAPI Server for Real-Time Fraud Detection
Provides REST API endpoints for fraud checking and system monitoring
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import uvicorn
from loguru import logger
import sys
import asyncio

# Add parent directory to path
sys.path.append('..')

from fraud_detector import FraudDetector

# Configure logger
logger.add("logs/api_server.log", rotation="100 MB", level="INFO")

# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Fraud Analytics API",
    description="Enterprise-grade fraud detection system for fintech applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize fraud detector
fraud_detector = FraudDetector(
    xgboost_weight=0.7,
    autoencoder_weight=0.3,
    fraud_threshold=0.5,
    high_risk_threshold=0.75
)

# Global statistics
stats = {
    'total_requests': 0,
    'fraud_detected': 0,
    'legitimate_transactions': 0,
    'avg_processing_time_ms': 0.0,
    'uptime_start': datetime.now()
}


# Pydantic models for request/response
class Transaction(BaseModel):
    """Transaction data model."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    user_id: str = Field(..., description="User identifier")
    merchant_id: str = Field(..., description="Merchant identifier")
    amount: float = Field(..., gt=0, description="Transaction amount")
    timestamp: Optional[str] = Field(None, description="Transaction timestamp (ISO format)")
    transaction_type: Optional[str] = Field("purchase", description="Type of transaction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN123456",
                "user_id": "USER001",
                "merchant_id": "MERCH001",
                "amount": 150.00,
                "timestamp": "2025-11-26T00:47:38Z",
                "transaction_type": "purchase"
            }
        }


class FraudCheckResponse(BaseModel):
    """Fraud check response model."""
    transaction_id: str
    fraud_score: float
    xgboost_score: float
    autoencoder_score: float
    is_fraud: bool
    risk_level: str
    risk_factors: List[str]
    processing_time_ms: float
    timestamp: str


class BatchTransactionRequest(BaseModel):
    """Batch transaction request model."""
    transactions: List[Transaction]


class SystemStats(BaseModel):
    """System statistics model."""
    total_requests: int
    fraud_detected: int
    legitimate_transactions: int
    fraud_rate: float
    avg_processing_time_ms: float
    uptime_seconds: float
    detector_stats: Dict


# API Endpoints

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information."""
    return {
        "service": "Real-Time Fraud Analytics API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "fraud_check": "/api/check-fraud",
            "batch_check": "/api/batch-check",
            "statistics": "/api/stats",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    uptime = (datetime.now() - stats['uptime_start']).total_seconds()
    
    return {
        "status": "healthy",
        "uptime_seconds": uptime,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/check-fraud", response_model=FraudCheckResponse, tags=["Fraud Detection"])
async def check_fraud(transaction: Transaction, background_tasks: BackgroundTasks):
    """
    Check a single transaction for fraud.
    
    This endpoint processes a transaction through the fraud detection pipeline:
    1. Enriches with metadata (DynamoDB simulation)
    2. Calculates velocity features
    3. Runs through ML models (XGBoost + Autoencoder)
    4. Returns fraud score and risk classification
    
    **Processing Time**: Typically < 100ms
    """
    try:
        # Convert to dict
        txn_dict = transaction.model_dump()
        
        # Run fraud detection
        result = fraud_detector.predict(txn_dict)
        
        # Update statistics
        background_tasks.add_task(update_stats, result)
        
        logger.info(
            f"Fraud check: {transaction.transaction_id} - "
            f"Score: {result['fraud_score']:.3f}, "
            f"Fraud: {result['is_fraud']}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch-check", tags=["Fraud Detection"])
async def batch_check_fraud(request: BatchTransactionRequest, background_tasks: BackgroundTasks):
    """
    Check multiple transactions in batch.
    
    Processes multiple transactions efficiently. Useful for:
    - Bulk transaction processing
    - Historical data analysis
    - Batch reconciliation
    
    **Limit**: Maximum 1000 transactions per request
    """
    try:
        if len(request.transactions) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Maximum 1000 transactions per batch request"
            )
        
        # Convert to list of dicts
        txn_dicts = [txn.model_dump() for txn in request.transactions]
        
        # Process batch
        results = fraud_detector.batch_predict(txn_dicts)
        
        # Update statistics for each result
        for result in results:
            background_tasks.add_task(update_stats, result)
        
        logger.info(f"Batch processed: {len(results)} transactions")
        
        return {
            "total_transactions": len(results),
            "results": results,
            "summary": {
                "fraud_detected": sum(1 for r in results if r.get('is_fraud')),
                "legitimate": sum(1 for r in results if not r.get('is_fraud')),
                "avg_fraud_score": sum(r.get('fraud_score', 0) for r in results) / len(results)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=SystemStats, tags=["Monitoring"])
async def get_statistics():
    """
    Get system statistics and performance metrics.
    
    Returns:
    - Total requests processed
    - Fraud detection counts
    - Average processing time
    - System uptime
    - Detector statistics
    """
    uptime = (datetime.now() - stats['uptime_start']).total_seconds()
    fraud_rate = (
        stats['fraud_detected'] / stats['total_requests']
        if stats['total_requests'] > 0 else 0.0
    )
    
    return {
        "total_requests": stats['total_requests'],
        "fraud_detected": stats['fraud_detected'],
        "legitimate_transactions": stats['legitimate_transactions'],
        "fraud_rate": fraud_rate,
        "avg_processing_time_ms": stats['avg_processing_time_ms'],
        "uptime_seconds": uptime,
        "detector_stats": fraud_detector.get_stats()
    }


@app.get("/api/detector-info", tags=["Monitoring"])
async def get_detector_info():
    """Get detailed information about the fraud detector configuration."""
    return {
        "detector_stats": fraud_detector.get_stats(),
        "xgboost_info": fraud_detector.xgboost_model.get_model_info(),
        "autoencoder_info": fraud_detector.autoencoder_model.get_model_info(),
        "feature_count": fraud_detector.feature_engineer.get_feature_count()
    }


@app.post("/api/reset-stats", tags=["Monitoring"])
async def reset_statistics():
    """Reset system statistics (for testing purposes)."""
    global stats
    stats = {
        'total_requests': 0,
        'fraud_detected': 0,
        'legitimate_transactions': 0,
        'avg_processing_time_ms': 0.0,
        'uptime_start': datetime.now()
    }
    
    logger.info("Statistics reset")
    return {"message": "Statistics reset successfully"}


# Helper functions

def update_stats(result: Dict):
    """Update global statistics (runs in background)."""
    stats['total_requests'] += 1
    
    if result.get('is_fraud'):
        stats['fraud_detected'] += 1
    else:
        stats['legitimate_transactions'] += 1
    
    # Update running average of processing time
    current_avg = stats['avg_processing_time_ms']
    new_time = result.get('processing_time_ms', 0)
    n = stats['total_requests']
    stats['avg_processing_time_ms'] = (current_avg * (n - 1) + new_time) / n


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("=" * 60)
    logger.info("Real-Time Fraud Analytics API Starting...")
    logger.info("=" * 60)
    
    # Try to load pre-trained models
    try:
        fraud_detector.load_models("models/saved")
        logger.info("✓ Pre-trained models loaded successfully")
    except Exception as e:
        logger.warning(f"⚠ Could not load pre-trained models: {e}")
        logger.info("Using untrained models (for demonstration)")
    
    logger.info("✓ Fraud Detector initialized")
    logger.info("✓ API server ready")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("API server shutting down...")
    logger.info(f"Total requests processed: {stats['total_requests']}")
    logger.info(f"Fraud detected: {stats['fraud_detected']}")


if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
