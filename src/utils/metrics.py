"""
Metrics and Evaluation Utilities
Functions for calculating fraud detection metrics
"""

import numpy as np
from typing import Dict, Tuple
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


def calculate_fraud_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_pred_proba: np.ndarray = None) -> Dict:
    """
    Calculate comprehensive fraud detection metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_pred_proba: Predicted probabilities (optional)
        
    Returns:
        Dictionary of metrics
    """
    metrics = {
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
        'f1_score': float(f1_score(y_true, y_pred, zero_division=0)),
    }
    
    # Add AUC-ROC if probabilities provided
    if y_pred_proba is not None:
        try:
            metrics['auc_roc'] = float(roc_auc_score(y_true, y_pred_proba))
        except ValueError:
            metrics['auc_roc'] = 0.0
    
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    metrics['confusion_matrix'] = {
        'true_negatives': int(tn),
        'false_positives': int(fp),
        'false_negatives': int(fn),
        'true_positives': int(tp)
    }
    
    # Additional metrics
    metrics['accuracy'] = float((tp + tn) / (tp + tn + fp + fn)) if (tp + tn + fp + fn) > 0 else 0.0
    metrics['false_positive_rate'] = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    metrics['false_negative_rate'] = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0
    
    return metrics


def calculate_business_metrics(y_true: np.ndarray, y_pred: np.ndarray, 
                               transaction_amounts: np.ndarray,
                               fraud_investigation_cost: float = 50.0,
                               fraud_loss_rate: float = 1.0) -> Dict:
    """
    Calculate business-oriented metrics for fraud detection.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        transaction_amounts: Transaction amounts
        fraud_investigation_cost: Cost to investigate each flagged transaction
        fraud_loss_rate: Fraction of transaction amount lost to fraud
        
    Returns:
        Dictionary of business metrics
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    # Calculate costs
    investigation_cost = fp * fraud_investigation_cost
    fraud_losses = fn * np.mean(transaction_amounts[y_true == 1]) * fraud_loss_rate if fn > 0 else 0
    fraud_prevented = tp * np.mean(transaction_amounts[y_true == 1]) * fraud_loss_rate if tp > 0 else 0
    
    total_cost = investigation_cost + fraud_losses
    net_savings = fraud_prevented - total_cost
    
    return {
        'investigation_cost': float(investigation_cost),
        'fraud_losses': float(fraud_losses),
        'fraud_prevented': float(fraud_prevented),
        'total_cost': float(total_cost),
        'net_savings': float(net_savings),
        'roi': float(net_savings / total_cost) if total_cost > 0 else 0.0
    }


def calculate_threshold_metrics(y_true: np.ndarray, y_pred_proba: np.ndarray, 
                                thresholds: np.ndarray = None) -> Dict:
    """
    Calculate metrics at different threshold values.
    
    Args:
        y_true: True labels
        y_pred_proba: Predicted probabilities
        thresholds: Array of thresholds to evaluate
        
    Returns:
        Dictionary with metrics for each threshold
    """
    if thresholds is None:
        thresholds = np.arange(0.1, 1.0, 0.1)
    
    results = []
    
    for threshold in thresholds:
        y_pred = (y_pred_proba >= threshold).astype(int)
        metrics = calculate_fraud_metrics(y_true, y_pred, y_pred_proba)
        metrics['threshold'] = float(threshold)
        results.append(metrics)
    
    return {
        'thresholds': thresholds.tolist(),
        'metrics': results
    }


if __name__ == "__main__":
    # Demo
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 0, 1, 1])
    y_pred = np.array([0, 0, 1, 0, 0, 1, 1, 0, 1, 1])
    y_pred_proba = np.array([0.1, 0.2, 0.9, 0.4, 0.1, 0.8, 0.6, 0.2, 0.95, 0.85])
    
    metrics = calculate_fraud_metrics(y_true, y_pred, y_pred_proba)
    print("Fraud Detection Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
