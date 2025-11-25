"""Models package initialization"""
from .xgboost_model import XGBoostFraudModel
from .autoencoder_model import AutoencoderAnomalyDetector

__all__ = ['XGBoostFraudModel', 'AutoencoderAnomalyDetector']
