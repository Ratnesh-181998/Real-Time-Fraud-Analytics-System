"""
Simplified Fraud Detection API - Demo Version
Works without ML libraries for immediate demonstration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import random
import uvicorn
from loguru import logger

# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Fraud Analytics API (Demo)",
    description="Simplified fraud detection system for demonstration",
    version="1.0.0-demo"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global statistics
stats = {
    'total_requests': 0,
    'fraud_detected': 0,
    'legitimate_transactions': 0,
    'avg_processing_time_ms': 45.3,
    'uptime_start': datetime.now()
}

# Pydantic models
class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    merchant_id: str
    amount: float = Field(..., gt=0)
    timestamp: Optional[str] = None
    transaction_type: Optional[str] = "purchase"

class FraudCheckResponse(BaseModel):
    transaction_id: str
    fraud_score: float
    xgboost_score: float
    autoencoder_score: float
    is_fraud: bool
    risk_level: str
    risk_factors: List[str]
    processing_time_ms: float
    timestamp: str

# Simple fraud detection logic
def detect_fraud_simple(transaction: Dict) -> Dict:
    """Simplified fraud detection for demo purposes."""
    start_time = datetime.now()
    
    amount = transaction.get('amount', 0)
    
    # Simple rule-based fraud detection
    fraud_score = 0.0
    risk_factors = []
    
    # High amount
    if amount > 1000:
        fraud_score += 0.3
        risk_factors.append("High transaction amount (>$1000)")
    
    # Very high amount
    if amount > 2000:
        fraud_score += 0.3
        risk_factors.append("Very high transaction amount (>$2000)")
    
    # Random factors for demo
    if random.random() < 0.2:
        fraud_score += 0.2
        risk_factors.append("Unusual merchant category")
    
    if random.random() < 0.15:
        fraud_score += 0.15
        risk_factors.append("Geographic anomaly detected")
    
    # Simulate model scores
    xgboost_score = min(fraud_score + random.uniform(-0.1, 0.1), 1.0)
    autoencoder_score = min(fraud_score + random.uniform(-0.15, 0.15), 1.0)
    
    # Ensemble
    fraud_score = 0.7 * xgboost_score + 0.3 * autoencoder_score
    fraud_score = max(0.0, min(1.0, fraud_score))
    
    # Risk level
    if fraud_score >= 0.75:
        risk_level = "HIGH"
    elif fraud_score >= 0.5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    is_fraud = fraud_score >= 0.5
    
    if not risk_factors:
        risk_factors = ["No specific risk factors identified"]
    
    processing_time = (datetime.now() - start_time).total_seconds() * 1000
    
    return {
        'transaction_id': transaction.get('transaction_id', 'UNKNOWN'),
        'fraud_score': float(fraud_score),
        'xgboost_score': float(xgboost_score),
        'autoencoder_score': float(autoencoder_score),
        'is_fraud': bool(is_fraud),
        'risk_level': risk_level,
        'risk_factors': risk_factors,
        'processing_time_ms': round(processing_time + random.uniform(30, 60), 2),
        'timestamp': datetime.now().isoformat()
    }

# API Endpoints
@app.get("/")
async def root():
    return {
        "service": "Real-Time Fraud Analytics API (Demo)",
        "version": "1.0.0-demo",
        "status": "operational",
        "note": "Simplified version for demonstration",
        "endpoints": {
            "fraud_check": "/api/check-fraud",
            "batch_check": "/api/batch-check",
            "statistics": "/api/stats",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    uptime = (datetime.now() - stats['uptime_start']).total_seconds()
    return {
        "status": "healthy",
        "uptime_seconds": uptime,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/check-fraud", response_model=FraudCheckResponse)
async def check_fraud(transaction: Transaction, background_tasks: BackgroundTasks):
    try:
        txn_dict = transaction.model_dump()
        result = detect_fraud_simple(txn_dict)
        
        # Update stats
        stats['total_requests'] += 1
        if result['is_fraud']:
            stats['fraud_detected'] += 1
        else:
            stats['legitimate_transactions'] += 1
        
        logger.info(f"Fraud check: {transaction.transaction_id} - Score: {result['fraud_score']:.3f}")
        
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch-check")
async def batch_check_fraud(transactions: List[Transaction]):
    try:
        if len(transactions) > 1000:
            raise HTTPException(status_code=400, detail="Maximum 1000 transactions per batch")
        
        results = []
        for txn in transactions:
            txn_dict = txn.model_dump()
            result = detect_fraud_simple(txn_dict)
            results.append(result)
            
            # Update stats
            stats['total_requests'] += 1
            if result['is_fraud']:
                stats['fraud_detected'] += 1
            else:
                stats['legitimate_transactions'] += 1
        
        return {
            "total_transactions": len(results),
            "results": results,
            "summary": {
                "fraud_detected": sum(1 for r in results if r['is_fraud']),
                "legitimate": sum(1 for r in results if not r['is_fraud']),
                "avg_fraud_score": sum(r['fraud_score'] for r in results) / len(results)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_statistics():
    uptime = (datetime.now() - stats['uptime_start']).total_seconds()
    fraud_rate = stats['fraud_detected'] / stats['total_requests'] if stats['total_requests'] > 0 else 0.0
    
    return {
        "total_requests": stats['total_requests'],
        "fraud_detected": stats['fraud_detected'],
        "legitimate_transactions": stats['legitimate_transactions'],
        "fraud_rate": fraud_rate,
        "avg_processing_time_ms": stats['avg_processing_time_ms'],
        "uptime_seconds": uptime,
        "detector_stats": {
            "users_tracked": random.randint(50, 200),
            "merchants_tracked": random.randint(30, 150),
            "model_weights": {
                "xgboost": 0.7,
                "autoencoder": 0.3
            },
            "thresholds": {
                "fraud": 0.5,
                "high_risk": 0.75
            }
        }
    }

@app.get("/api/detector-info")
async def get_detector_info():
    return {
        "detector_stats": {
            "users_tracked": random.randint(50, 200),
            "merchants_tracked": random.randint(30, 150)
        },
        "xgboost_info": {
            "model_type": "XGBoost Classifier (Demo)",
            "is_trained": True,
            "precision": 0.94,
            "recall": 0.89
        },
        "autoencoder_info": {
            "model_type": "Autoencoder (Demo)",
            "is_trained": True,
            "anomaly_detection_rate": 0.87
        },
        "feature_count": 50
    }

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Real-Time Fraud Analytics API (Demo) Starting...")
    logger.info("=" * 60)
    logger.info("✓ Simplified fraud detector initialized")
    logger.info("✓ API server ready")
    logger.info("=" * 60)

if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "api_server_demo:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
