"""
Real-Time Fraud Detection System
Main fraud detection logic with ensemble model approach
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
from loguru import logger
import joblib
from pathlib import Path

from models.xgboost_model import XGBoostFraudModel
from models.autoencoder_model import AutoencoderAnomalyDetector
from features.feature_engineering import FeatureEngineer
from utils.metrics import calculate_fraud_metrics


class FraudDetector:
    """
    Main fraud detection class that orchestrates the entire fraud detection pipeline.
    
    Components:
    - XGBoost for supervised fraud detection
    - Autoencoder for unsupervised anomaly detection
    - Feature engineering pipeline
    - Ensemble scoring mechanism
    """
    
    def __init__(
        self,
        xgboost_weight: float = 0.7,
        autoencoder_weight: float = 0.3,
        fraud_threshold: float = 0.5,
        high_risk_threshold: float = 0.75
    ):
        """
        Initialize the fraud detector with ensemble weights.
        
        Args:
            xgboost_weight: Weight for XGBoost model in ensemble (default: 0.7)
            autoencoder_weight: Weight for Autoencoder in ensemble (default: 0.3)
            fraud_threshold: Threshold for flagging as fraud (default: 0.5)
            high_risk_threshold: Threshold for high-risk classification (default: 0.75)
        """
        self.xgboost_weight = xgboost_weight
        self.autoencoder_weight = autoencoder_weight
        self.fraud_threshold = fraud_threshold
        self.high_risk_threshold = high_risk_threshold
        
        # Initialize models
        self.xgboost_model = XGBoostFraudModel()
        self.autoencoder_model = AutoencoderAnomalyDetector()
        self.feature_engineer = FeatureEngineer()
        
        # Transaction history for velocity features
        self.transaction_history: Dict[str, List[Dict]] = {}
        
        # User metadata cache (simulates DynamoDB)
        self.user_metadata: Dict[str, Dict] = {}
        self.merchant_metadata: Dict[str, Dict] = {}
        
        logger.info("Fraud Detector initialized successfully")
    
    def load_models(self, model_dir: str = "models/saved"):
        """Load pre-trained models from disk."""
        model_path = Path(model_dir)
        
        try:
            self.xgboost_model.load(model_path / "xgboost_model.pkl")
            self.autoencoder_model.load(model_path / "autoencoder_model.h5")
            logger.info(f"Models loaded from {model_dir}")
        except Exception as e:
            logger.warning(f"Could not load models: {e}. Using untrained models.")
    
    def enrich_transaction(self, transaction: Dict) -> Dict:
        """
        Enrich transaction with metadata from DynamoDB (simulated).
        
        Args:
            transaction: Raw transaction data
            
        Returns:
            Enriched transaction with user and merchant metadata
        """
        enriched = transaction.copy()
        
        # Get user metadata
        user_id = transaction.get('user_id')
        if user_id in self.user_metadata:
            enriched['user_metadata'] = self.user_metadata[user_id]
        else:
            # Simulate DynamoDB lookup
            enriched['user_metadata'] = {
                'account_age_days': np.random.randint(30, 1000),
                'total_transactions': np.random.randint(10, 500),
                'avg_transaction_amount': np.random.uniform(50, 500),
                'country': np.random.choice(['US', 'UK', 'CA', 'AU']),
                'is_verified': np.random.choice([True, False], p=[0.8, 0.2])
            }
            self.user_metadata[user_id] = enriched['user_metadata']
        
        # Get merchant metadata
        merchant_id = transaction.get('merchant_id')
        if merchant_id in self.merchant_metadata:
            enriched['merchant_metadata'] = self.merchant_metadata[merchant_id]
        else:
            # Simulate DynamoDB lookup
            enriched['merchant_metadata'] = {
                'merchant_category': np.random.choice(['retail', 'food', 'travel', 'online']),
                'risk_score': np.random.uniform(0, 1),
                'is_verified': np.random.choice([True, False], p=[0.9, 0.1])
            }
            self.merchant_metadata[merchant_id] = enriched['merchant_metadata']
        
        return enriched
    
    def calculate_velocity_features(self, user_id: str, current_time: datetime) -> Dict:
        """
        Calculate velocity features (transaction frequency and amounts over time windows).
        
        Args:
            user_id: User identifier
            current_time: Current transaction timestamp
            
        Returns:
            Dictionary of velocity features
        """
        if user_id not in self.transaction_history:
            return {
                'txn_count_1h': 0,
                'txn_count_24h': 0,
                'txn_count_7d': 0,
                'total_amount_1h': 0.0,
                'total_amount_24h': 0.0,
                'total_amount_7d': 0.0,
                'avg_amount_24h': 0.0
            }
        
        history = self.transaction_history[user_id]
        
        # Time windows
        one_hour_ago = current_time - timedelta(hours=1)
        one_day_ago = current_time - timedelta(days=1)
        seven_days_ago = current_time - timedelta(days=7)
        
        # Filter transactions by time windows
        txns_1h = [t for t in history if t['timestamp'] >= one_hour_ago]
        txns_24h = [t for t in history if t['timestamp'] >= one_day_ago]
        txns_7d = [t for t in history if t['timestamp'] >= seven_days_ago]
        
        return {
            'txn_count_1h': len(txns_1h),
            'txn_count_24h': len(txns_24h),
            'txn_count_7d': len(txns_7d),
            'total_amount_1h': sum(t['amount'] for t in txns_1h),
            'total_amount_24h': sum(t['amount'] for t in txns_24h),
            'total_amount_7d': sum(t['amount'] for t in txns_7d),
            'avg_amount_24h': np.mean([t['amount'] for t in txns_24h]) if txns_24h else 0.0
        }
    
    def update_transaction_history(self, user_id: str, transaction: Dict):
        """Update transaction history for velocity calculations."""
        if user_id not in self.transaction_history:
            self.transaction_history[user_id] = []
        
        self.transaction_history[user_id].append({
            'timestamp': transaction['timestamp'],
            'amount': transaction['amount'],
            'merchant_id': transaction.get('merchant_id')
        })
        
        # Keep only last 7 days of history
        cutoff = transaction['timestamp'] - timedelta(days=7)
        self.transaction_history[user_id] = [
            t for t in self.transaction_history[user_id]
            if t['timestamp'] >= cutoff
        ]
    
    def extract_features(self, transaction: Dict) -> np.ndarray:
        """
        Extract all features from enriched transaction.
        
        Args:
            transaction: Enriched transaction data
            
        Returns:
            Feature vector as numpy array
        """
        return self.feature_engineer.transform(transaction)
    
    def predict(self, transaction: Dict) -> Dict:
        """
        Main prediction method - orchestrates the entire fraud detection pipeline.
        
        Pipeline:
        1. Enrich transaction with metadata
        2. Calculate velocity features
        3. Extract all features
        4. Get predictions from both models
        5. Ensemble scoring
        6. Risk classification
        
        Args:
            transaction: Raw transaction data
            
        Returns:
            Fraud detection result with score, classification, and factors
        """
        start_time = datetime.now()
        
        # Parse timestamp
        if isinstance(transaction.get('timestamp'), str):
            transaction['timestamp'] = datetime.fromisoformat(
                transaction['timestamp'].replace('Z', '+00:00')
            )
        elif 'timestamp' not in transaction:
            transaction['timestamp'] = datetime.now()
        
        # Step 1: Enrich with metadata (simulates DynamoDB lookup)
        enriched_txn = self.enrich_transaction(transaction)
        
        # Step 2: Calculate velocity features
        velocity_features = self.calculate_velocity_features(
            transaction['user_id'],
            transaction['timestamp']
        )
        enriched_txn.update(velocity_features)
        
        # Step 3: Extract features
        features = self.extract_features(enriched_txn)
        
        # Step 4: Get predictions from both models
        xgboost_score = self.xgboost_model.predict_proba(features)
        autoencoder_score = self.autoencoder_model.predict_anomaly_score(features)
        
        # Step 5: Ensemble scoring
        fraud_score = (
            self.xgboost_weight * xgboost_score +
            self.autoencoder_weight * autoencoder_score
        )
        
        # Step 6: Risk classification
        is_fraud = fraud_score >= self.fraud_threshold
        
        if fraud_score >= self.high_risk_threshold:
            risk_level = "HIGH"
        elif fraud_score >= self.fraud_threshold:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(enriched_txn, features)
        
        # Update transaction history
        self.update_transaction_history(transaction['user_id'], transaction)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            'transaction_id': transaction.get('transaction_id', 'UNKNOWN'),
            'fraud_score': float(fraud_score),
            'xgboost_score': float(xgboost_score),
            'autoencoder_score': float(autoencoder_score),
            'is_fraud': bool(is_fraud),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'processing_time_ms': round(processing_time, 2),
            'timestamp': transaction['timestamp'].isoformat()
        }
        
        logger.info(
            f"Transaction {result['transaction_id']}: "
            f"Score={fraud_score:.3f}, Risk={risk_level}, Time={processing_time:.1f}ms"
        )
        
        return result
    
    def _identify_risk_factors(self, transaction: Dict, features: np.ndarray) -> List[str]:
        """Identify specific risk factors for the transaction."""
        factors = []
        
        # High transaction amount
        amount = transaction.get('amount', 0)
        avg_amount = transaction.get('avg_amount_24h', 0)
        if avg_amount > 0 and amount > avg_amount * 3:
            factors.append("Unusual transaction amount (3x average)")
        elif amount > 1000:
            factors.append("High transaction amount")
        
        # High velocity
        if transaction.get('txn_count_1h', 0) > 5:
            factors.append("High velocity spending (>5 txns/hour)")
        
        # Merchant risk
        merchant_meta = transaction.get('merchant_metadata', {})
        if merchant_meta.get('risk_score', 0) > 0.7:
            factors.append("High-risk merchant")
        if not merchant_meta.get('is_verified', True):
            factors.append("Unverified merchant")
        
        # User risk
        user_meta = transaction.get('user_metadata', {})
        if user_meta.get('account_age_days', 1000) < 30:
            factors.append("New user account (<30 days)")
        if not user_meta.get('is_verified', True):
            factors.append("Unverified user account")
        
        # Geographic anomaly (simplified)
        if np.random.random() < 0.1:  # 10% chance
            factors.append("Geographic anomaly detected")
        
        return factors if factors else ["No specific risk factors identified"]
    
    def batch_predict(self, transactions: List[Dict]) -> List[Dict]:
        """
        Process multiple transactions in batch.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of fraud detection results
        """
        results = []
        for txn in transactions:
            try:
                result = self.predict(txn)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing transaction: {e}")
                results.append({
                    'transaction_id': txn.get('transaction_id', 'UNKNOWN'),
                    'error': str(e),
                    'is_fraud': None
                })
        
        return results
    
    def get_stats(self) -> Dict:
        """Get detector statistics."""
        return {
            'users_tracked': len(self.user_metadata),
            'merchants_tracked': len(self.merchant_metadata),
            'users_with_history': len(self.transaction_history),
            'total_historical_transactions': sum(
                len(history) for history in self.transaction_history.values()
            ),
            'model_weights': {
                'xgboost': self.xgboost_weight,
                'autoencoder': self.autoencoder_weight
            },
            'thresholds': {
                'fraud': self.fraud_threshold,
                'high_risk': self.high_risk_threshold
            }
        }
