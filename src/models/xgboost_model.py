"""
XGBoost-based Fraud Detection Model
Supervised learning approach for detecting known fraud patterns
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, List
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve
import joblib
from loguru import logger


class XGBoostFraudModel:
    """
    XGBoost classifier for fraud detection.
    
    Features:
    - Handles imbalanced datasets with scale_pos_weight
    - Optimized for precision-recall trade-off
    - Fast inference for real-time predictions
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        scale_pos_weight: float = 10.0,
        random_state: int = 42
    ):
        """
        Initialize XGBoost model with fraud detection optimized parameters.
        
        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate (eta)
            scale_pos_weight: Balancing of positive and negative weights (for imbalanced data)
            random_state: Random seed for reproducibility
        """
        self.params = {
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'learning_rate': learning_rate,
            'scale_pos_weight': scale_pos_weight,
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'random_state': random_state,
            'tree_method': 'hist',  # Faster training
            'predictor': 'cpu_predictor'
        }
        
        self.model = xgb.XGBClassifier(**self.params)
        self.is_trained = False
        self.feature_importance: Optional[Dict] = None
        
        logger.info("XGBoost Fraud Model initialized")
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        validation_split: float = 0.2,
        early_stopping_rounds: int = 10
    ) -> Dict:
        """
        Train the XGBoost model.
        
        Args:
            X: Feature matrix
            y: Target labels (0=legitimate, 1=fraud)
            validation_split: Fraction of data for validation
            early_stopping_rounds: Stop if no improvement for N rounds
            
        Returns:
            Training metrics dictionary
        """
        logger.info(f"Training XGBoost model on {len(X)} samples...")
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y
        )
        
        # Train model
        self.model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        self.is_trained = True
        
        # Calculate feature importance
        self.feature_importance = dict(
            zip(
                [f"feature_{i}" for i in range(X.shape[1])],
                self.model.feature_importances_
            )
        )
        
        # Evaluate on validation set
        y_pred = self.model.predict(X_val)
        y_pred_proba = self.model.predict_proba(X_val)[:, 1]
        
        metrics = {
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'fraud_rate': float(y.mean()),
            'val_auc_roc': float(roc_auc_score(y_val, y_pred_proba)),
            'best_iteration': self.model.best_iteration,
            'classification_report': classification_report(y_val, y_pred, output_dict=True)
        }
        
        logger.info(f"Training complete. Validation AUC-ROC: {metrics['val_auc_roc']:.4f}")
        
        return metrics
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict fraud labels.
        
        Args:
            X: Feature matrix
            
        Returns:
            Binary predictions (0=legitimate, 1=fraud)
        """
        if not self.is_trained:
            logger.warning("Model not trained. Using random predictions.")
            return np.random.randint(0, 2, size=len(X))
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> float:
        """
        Predict fraud probability for a single transaction.
        
        Args:
            X: Feature vector (can be 1D or 2D)
            
        Returns:
            Fraud probability (0-1)
        """
        if not self.is_trained:
            # Return random probability if not trained
            return float(np.random.random())
        
        # Ensure X is 2D
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        proba = self.model.predict_proba(X)[:, 1]
        return float(proba[0]) if len(proba) == 1 else proba
    
    def get_feature_importance(self, top_n: int = 20) -> Dict:
        """
        Get top N most important features.
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            Dictionary of feature names and importance scores
        """
        if self.feature_importance is None:
            return {}
        
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return dict(sorted_features[:top_n])
    
    def save(self, filepath: str):
        """Save model to disk."""
        joblib.dump({
            'model': self.model,
            'params': self.params,
            'is_trained': self.is_trained,
            'feature_importance': self.feature_importance
        }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model from disk."""
        data = joblib.load(filepath)
        self.model = data['model']
        self.params = data['params']
        self.is_trained = data['is_trained']
        self.feature_importance = data['feature_importance']
        logger.info(f"Model loaded from {filepath}")
    
    def get_model_info(self) -> Dict:
        """Get model information."""
        return {
            'model_type': 'XGBoost Classifier',
            'is_trained': self.is_trained,
            'parameters': self.params,
            'best_iteration': getattr(self.model, 'best_iteration', None) if self.is_trained else None,
            'n_features': getattr(self.model, 'n_features_in_', None) if self.is_trained else None
        }


def create_synthetic_training_data(n_samples: int = 10000, fraud_rate: float = 0.05) -> tuple:
    """
    Create synthetic training data for demonstration.
    
    Args:
        n_samples: Number of samples to generate
        fraud_rate: Fraction of fraudulent transactions
        
    Returns:
        Tuple of (X, y) where X is features and y is labels
    """
    n_features = 50
    n_fraud = int(n_samples * fraud_rate)
    n_legitimate = n_samples - n_fraud
    
    # Legitimate transactions
    X_legit = np.random.randn(n_legitimate, n_features)
    y_legit = np.zeros(n_legitimate)
    
    # Fraudulent transactions (shifted distribution)
    X_fraud = np.random.randn(n_fraud, n_features) + 2.0  # Shift mean
    X_fraud[:, :10] *= 2.0  # Increase variance in first 10 features
    y_fraud = np.ones(n_fraud)
    
    # Combine
    X = np.vstack([X_legit, X_fraud])
    y = np.hstack([y_legit, y_fraud])
    
    # Shuffle
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    return X, y


if __name__ == "__main__":
    # Demo: Train model on synthetic data
    logger.info("Creating synthetic training data...")
    X, y = create_synthetic_training_data(n_samples=10000, fraud_rate=0.05)
    
    logger.info("Training XGBoost model...")
    model = XGBoostFraudModel()
    metrics = model.train(X, y)
    
    logger.info("Training Metrics:")
    logger.info(f"  AUC-ROC: {metrics['val_auc_roc']:.4f}")
    logger.info(f"  Fraud Rate: {metrics['fraud_rate']:.2%}")
    
    # Test prediction
    test_sample = X[0:1]
    prediction = model.predict_proba(test_sample)
    logger.info(f"Test prediction: {prediction:.4f}")
    
    # Save model
    model.save("xgboost_model.pkl")
    logger.info("Model saved successfully")
