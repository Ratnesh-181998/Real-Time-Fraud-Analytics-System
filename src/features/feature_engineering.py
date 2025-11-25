"""
Feature Engineering Pipeline
Transforms raw transaction data into ML-ready features
"""

import numpy as np
from typing import Dict, List
from datetime import datetime
from loguru import logger


class FeatureEngineer:
    """
    Feature engineering pipeline for fraud detection.
    
    Generates 50+ features from raw transaction data including:
    - Transaction attributes
    - Velocity features
    - User behavior features
    - Merchant features
    - Temporal features
    - Geographic features
    """
    
    def __init__(self):
        """Initialize feature engineer."""
        self.feature_names: List[str] = []
        self._initialize_feature_names()
        logger.info(f"Feature Engineer initialized with {len(self.feature_names)} features")
    
    def _initialize_feature_names(self):
        """Initialize feature names for reference."""
        self.feature_names = [
            # Transaction features (10)
            'amount',
            'amount_log',
            'amount_zscore',
            'is_high_value',
            'is_round_amount',
            'hour_of_day',
            'day_of_week',
            'is_weekend',
            'is_night_time',
            'transaction_type_encoded',
            
            # Velocity features (10)
            'txn_count_1h',
            'txn_count_24h',
            'txn_count_7d',
            'total_amount_1h',
            'total_amount_24h',
            'total_amount_7d',
            'avg_amount_24h',
            'amount_vs_avg_ratio',
            'velocity_1h_24h_ratio',
            'velocity_24h_7d_ratio',
            
            # User features (10)
            'account_age_days',
            'account_age_log',
            'total_user_transactions',
            'user_avg_transaction',
            'is_new_user',
            'is_verified_user',
            'user_country_encoded',
            'user_risk_score',
            'days_since_last_txn',
            'user_transaction_frequency',
            
            # Merchant features (10)
            'merchant_category_encoded',
            'merchant_risk_score',
            'is_verified_merchant',
            'is_new_merchant',
            'merchant_avg_transaction',
            'merchant_transaction_count',
            'is_high_risk_category',
            'merchant_fraud_history',
            'merchant_age_days',
            'merchant_country_encoded',
            
            # Derived features (10)
            'amount_merchant_avg_ratio',
            'amount_user_avg_ratio',
            'user_merchant_interaction_count',
            'is_first_time_merchant',
            'time_since_account_creation',
            'geographic_distance',
            'device_change_flag',
            'ip_change_flag',
            'unusual_time_flag',
            'cross_border_flag'
        ]
    
    def transform(self, transaction: Dict) -> np.ndarray:
        """
        Transform raw transaction into feature vector.
        
        Args:
            transaction: Dictionary containing transaction data
            
        Returns:
            Feature vector as numpy array
        """
        features = []
        
        # Transaction features
        amount = transaction.get('amount', 0.0)
        features.extend(self._extract_transaction_features(transaction, amount))
        
        # Velocity features
        features.extend(self._extract_velocity_features(transaction))
        
        # User features
        features.extend(self._extract_user_features(transaction))
        
        # Merchant features
        features.extend(self._extract_merchant_features(transaction))
        
        # Derived features
        features.extend(self._extract_derived_features(transaction, amount))
        
        return np.array(features, dtype=np.float32)
    
    def _extract_transaction_features(self, txn: Dict, amount: float) -> List[float]:
        """Extract transaction-level features."""
        timestamp = txn.get('timestamp', datetime.now())
        
        return [
            amount,
            np.log1p(amount),  # Log transform
            (amount - 100) / 50,  # Z-score (simplified)
            float(amount > 1000),  # High value flag
            float(amount % 10 == 0),  # Round amount
            timestamp.hour,
            timestamp.weekday(),
            float(timestamp.weekday() >= 5),  # Weekend
            float(timestamp.hour < 6 or timestamp.hour > 22),  # Night time
            hash(txn.get('transaction_type', 'purchase')) % 10  # Type encoding
        ]
    
    def _extract_velocity_features(self, txn: Dict) -> List[float]:
        """Extract velocity-based features."""
        return [
            txn.get('txn_count_1h', 0),
            txn.get('txn_count_24h', 0),
            txn.get('txn_count_7d', 0),
            txn.get('total_amount_1h', 0.0),
            txn.get('total_amount_24h', 0.0),
            txn.get('total_amount_7d', 0.0),
            txn.get('avg_amount_24h', 0.0),
            txn.get('amount', 0) / max(txn.get('avg_amount_24h', 1), 1),  # Ratio
            txn.get('txn_count_1h', 0) / max(txn.get('txn_count_24h', 1), 1),
            txn.get('txn_count_24h', 0) / max(txn.get('txn_count_7d', 1), 1)
        ]
    
    def _extract_user_features(self, txn: Dict) -> List[float]:
        """Extract user-level features."""
        user_meta = txn.get('user_metadata', {})
        account_age = user_meta.get('account_age_days', 100)
        
        return [
            account_age,
            np.log1p(account_age),
            user_meta.get('total_transactions', 0),
            user_meta.get('avg_transaction_amount', 0.0),
            float(account_age < 30),  # New user
            float(user_meta.get('is_verified', False)),
            hash(user_meta.get('country', 'US')) % 10,
            np.random.random() * 0.3,  # Simulated risk score
            np.random.randint(0, 30),  # Days since last txn
            user_meta.get('total_transactions', 0) / max(account_age, 1)  # Frequency
        ]
    
    def _extract_merchant_features(self, txn: Dict) -> List[float]:
        """Extract merchant-level features."""
        merchant_meta = txn.get('merchant_metadata', {})
        
        category_map = {'retail': 0, 'food': 1, 'travel': 2, 'online': 3}
        category = merchant_meta.get('merchant_category', 'retail')
        
        return [
            category_map.get(category, 0),
            merchant_meta.get('risk_score', 0.0),
            float(merchant_meta.get('is_verified', True)),
            float(np.random.random() < 0.1),  # New merchant
            np.random.uniform(50, 500),  # Merchant avg
            np.random.randint(100, 10000),  # Merchant txn count
            float(category in ['online', 'travel']),  # High risk category
            np.random.random() * 0.2,  # Fraud history
            np.random.randint(30, 1000),  # Merchant age
            hash(merchant_meta.get('country', 'US')) % 10
        ]
    
    def _extract_derived_features(self, txn: Dict, amount: float) -> List[float]:
        """Extract derived/interaction features."""
        user_meta = txn.get('user_metadata', {})
        
        return [
            amount / max(np.random.uniform(50, 500), 1),  # Amount/merchant avg
            amount / max(user_meta.get('avg_transaction_amount', 100), 1),  # Amount/user avg
            np.random.randint(0, 50),  # User-merchant interaction count
            float(np.random.random() < 0.2),  # First time merchant
            (datetime.now() - txn.get('timestamp', datetime.now())).days,
            np.random.uniform(0, 1000),  # Geographic distance (km)
            float(np.random.random() < 0.1),  # Device change
            float(np.random.random() < 0.15),  # IP change
            float(txn.get('timestamp', datetime.now()).hour < 6),  # Unusual time
            float(np.random.random() < 0.05)  # Cross border
        ]
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names."""
        return self.feature_names.copy()
    
    def get_feature_count(self) -> int:
        """Get total number of features."""
        return len(self.feature_names)


if __name__ == "__main__":
    # Demo
    engineer = FeatureEngineer()
    
    sample_transaction = {
        'transaction_id': 'TXN123',
        'user_id': 'USER001',
        'merchant_id': 'MERCH001',
        'amount': 150.00,
        'timestamp': datetime.now(),
        'user_metadata': {
            'account_age_days': 365,
            'total_transactions': 50,
            'avg_transaction_amount': 120.0,
            'is_verified': True,
            'country': 'US'
        },
        'merchant_metadata': {
            'merchant_category': 'retail',
            'risk_score': 0.2,
            'is_verified': True
        },
        'txn_count_1h': 1,
        'txn_count_24h': 3,
        'txn_count_7d': 15,
        'total_amount_1h': 150.0,
        'total_amount_24h': 450.0,
        'total_amount_7d': 1800.0,
        'avg_amount_24h': 150.0
    }
    
    features = engineer.transform(sample_transaction)
    logger.info(f"Generated {len(features)} features")
    logger.info(f"Feature vector shape: {features.shape}")
    logger.info(f"Sample features: {features[:10]}")
