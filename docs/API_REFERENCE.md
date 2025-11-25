# API Reference

Complete API documentation for the Real-Time Fraud Analytics System.

**Base URL**: `http://localhost:8000`

---

## Table of Contents

1. [Health & Status](#health--status)
2. [Fraud Detection](#fraud-detection)
3. [Monitoring & Statistics](#monitoring--statistics)
4. [System Information](#system-information)

---

## Health & Status

### GET `/`
Root endpoint - API information

**Response:**
```json
{
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
```

### GET `/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "uptime_seconds": 3600.5,
  "timestamp": "2025-11-26T00:47:38.123Z"
}
```

---

## Fraud Detection

### POST `/api/check-fraud`
Check a single transaction for fraud

**Request Body:**
```json
{
  "transaction_id": "TXN123456",
  "user_id": "USER001",
  "merchant_id": "MERCH001",
  "amount": 150.00,
  "timestamp": "2025-11-26T00:47:38Z",
  "transaction_type": "purchase"
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| transaction_id | string | Yes | Unique transaction identifier |
| user_id | string | Yes | User identifier |
| merchant_id | string | Yes | Merchant identifier |
| amount | float | Yes | Transaction amount (must be > 0) |
| timestamp | string | No | ISO 8601 timestamp (defaults to current time) |
| transaction_type | string | No | Type of transaction (default: "purchase") |

**Response:**
```json
{
  "transaction_id": "TXN123456",
  "fraud_score": 0.87,
  "xgboost_score": 0.92,
  "autoencoder_score": 0.73,
  "is_fraud": true,
  "risk_level": "HIGH",
  "risk_factors": [
    "Unusual transaction amount (3x average)",
    "High velocity spending (>5 txns/hour)",
    "High-risk merchant"
  ],
  "processing_time_ms": 45.23,
  "timestamp": "2025-11-26T00:47:38.123Z"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| transaction_id | string | Transaction identifier |
| fraud_score | float | Overall fraud score (0-1) |
| xgboost_score | float | XGBoost model score (0-1) |
| autoencoder_score | float | Autoencoder anomaly score (0-1) |
| is_fraud | boolean | Whether transaction is classified as fraud |
| risk_level | string | Risk classification: LOW, MEDIUM, or HIGH |
| risk_factors | array | List of identified risk factors |
| processing_time_ms | float | Processing time in milliseconds |
| timestamp | string | Processing timestamp |

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Server error

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/check-fraud \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN123456",
    "user_id": "USER001",
    "merchant_id": "MERCH001",
    "amount": 150.00
  }'
```

---

### POST `/api/batch-check`
Check multiple transactions in batch

**Request Body:**
```json
{
  "transactions": [
    {
      "transaction_id": "TXN001",
      "user_id": "USER001",
      "merchant_id": "MERCH001",
      "amount": 150.00
    },
    {
      "transaction_id": "TXN002",
      "user_id": "USER002",
      "merchant_id": "MERCH002",
      "amount": 250.00
    }
  ]
}
```

**Limits:**
- Maximum 1000 transactions per request

**Response:**
```json
{
  "total_transactions": 2,
  "results": [
    {
      "transaction_id": "TXN001",
      "fraud_score": 0.23,
      "is_fraud": false,
      "risk_level": "LOW",
      ...
    },
    {
      "transaction_id": "TXN002",
      "fraud_score": 0.89,
      "is_fraud": true,
      "risk_level": "HIGH",
      ...
    }
  ],
  "summary": {
    "fraud_detected": 1,
    "legitimate": 1,
    "avg_fraud_score": 0.56
  }
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/api/batch-check \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {"transaction_id": "TXN001", "user_id": "USER001", "merchant_id": "MERCH001", "amount": 150.00},
      {"transaction_id": "TXN002", "user_id": "USER002", "merchant_id": "MERCH002", "amount": 250.00}
    ]
  }'
```

---

## Monitoring & Statistics

### GET `/api/stats`
Get system statistics and performance metrics

**Response:**
```json
{
  "total_requests": 1523,
  "fraud_detected": 87,
  "legitimate_transactions": 1436,
  "fraud_rate": 0.057,
  "avg_processing_time_ms": 45.3,
  "uptime_seconds": 7234.5,
  "detector_stats": {
    "users_tracked": 234,
    "merchants_tracked": 156,
    "users_with_history": 189,
    "total_historical_transactions": 1523,
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
```

**Example cURL:**
```bash
curl http://localhost:8000/api/stats
```

---

### GET `/api/detector-info`
Get detailed fraud detector configuration

**Response:**
```json
{
  "detector_stats": {
    "users_tracked": 234,
    "merchants_tracked": 156,
    ...
  },
  "xgboost_info": {
    "model_type": "XGBoost Classifier",
    "is_trained": true,
    "parameters": {
      "n_estimators": 100,
      "max_depth": 6,
      "learning_rate": 0.1
    },
    "best_iteration": 87,
    "n_features": 50
  },
  "autoencoder_info": {
    "model_type": "Autoencoder Anomaly Detector",
    "is_trained": true,
    "input_dim": 50,
    "latent_dim": 8,
    "hidden_dims": [32, 16],
    "reconstruction_threshold": 0.0234,
    "total_parameters": 4832
  },
  "feature_count": 50
}
```

---

### POST `/api/reset-stats`
Reset system statistics (for testing)

**Response:**
```json
{
  "message": "Statistics reset successfully"
}
```

**Note**: This endpoint is for testing purposes only.

---

## System Information

### Interactive Documentation

Visit **http://localhost:8000/docs** for interactive API documentation powered by Swagger UI.

Features:
- Try out API endpoints directly
- View request/response schemas
- See example payloads
- Test authentication

### Alternative Documentation

Visit **http://localhost:8000/redoc** for alternative documentation powered by ReDoc.

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Endpoint doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server-side error |

### Example Error Response

```json
{
  "detail": "Maximum 1000 transactions per batch request"
}
```

---

## Rate Limiting

Currently, there are no rate limits enforced. In production, consider implementing:
- Rate limiting per API key
- Throttling based on IP address
- Queue-based processing for high loads

---

## Authentication

The current implementation does not require authentication. For production deployment, implement:
- API key authentication
- OAuth 2.0
- JWT tokens
- IP whitelisting

---

## Best Practices

### 1. Transaction ID
Always use unique transaction IDs to avoid duplicate processing.

### 2. Timestamps
Provide accurate timestamps for better velocity feature calculation.

### 3. Batch Processing
Use batch endpoint for processing multiple transactions efficiently.

### 4. Error Handling
Always handle API errors gracefully in your application.

### 5. Monitoring
Regularly check `/api/stats` to monitor system health.

---

## Performance Considerations

### Latency
- Target: < 100ms per transaction
- Typical: 40-60ms
- p99: < 120ms

### Throughput
- Single transaction: 1000+ requests/second
- Batch processing: 10,000+ transactions/second

### Optimization Tips
1. Use batch endpoint for multiple transactions
2. Implement client-side caching
3. Use connection pooling
4. Enable HTTP/2 if supported

---

## Examples

### Python Example

```python
import requests

# Check single transaction
response = requests.post(
    'http://localhost:8000/api/check-fraud',
    json={
        'transaction_id': 'TXN123',
        'user_id': 'USER001',
        'merchant_id': 'MERCH001',
        'amount': 150.00
    }
)

result = response.json()
print(f"Fraud Score: {result['fraud_score']}")
print(f"Is Fraud: {result['is_fraud']}")
```

### JavaScript Example

```javascript
// Check single transaction
fetch('http://localhost:8000/api/check-fraud', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    transaction_id: 'TXN123',
    user_id: 'USER001',
    merchant_id: 'MERCH001',
    amount: 150.00
  })
})
.then(response => response.json())
.then(data => {
  console.log('Fraud Score:', data.fraud_score);
  console.log('Is Fraud:', data.is_fraud);
});
```

### cURL Example

```bash
# Check fraud
curl -X POST http://localhost:8000/api/check-fraud \
  -H "Content-Type: application/json" \
  -d '{"transaction_id":"TXN123","user_id":"USER001","merchant_id":"MERCH001","amount":150.00}'

# Get statistics
curl http://localhost:8000/api/stats

# Health check
curl http://localhost:8000/health
```

---

## Webhooks (Future Feature)

Planned webhook support for real-time fraud alerts:

```json
{
  "event": "fraud_detected",
  "transaction_id": "TXN123",
  "fraud_score": 0.89,
  "timestamp": "2025-11-26T00:47:38Z"
}
```

---

## Support

For API issues or questions:
- Check interactive docs: http://localhost:8000/docs
- Review this documentation
- Open an issue on GitHub

---

**Last Updated**: November 2025  
**API Version**: 1.0.0
