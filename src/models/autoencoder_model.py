"""
Autoencoder-based Anomaly Detection Model
Unsupervised learning approach for detecting novel fraud patterns
"""

import numpy as np
from typing import Optional, Dict, Tuple
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import StandardScaler
from loguru import logger


class AutoencoderAnomalyDetector:
    """
    Autoencoder neural network for anomaly detection in transactions.
    
    The model learns to reconstruct normal transactions. High reconstruction
    error indicates anomalous (potentially fraudulent) transactions.
    
    Architecture:
    - Encoder: [input_dim → 32 → 16 → 8 (latent)]
    - Decoder: [8 → 16 → 32 → input_dim]
    """
    
    def __init__(
        self,
        input_dim: int = 50,
        latent_dim: int = 8,
        hidden_dims: list = [32, 16],
        dropout_rate: float = 0.2,
        learning_rate: float = 0.001
    ):
        """
        Initialize Autoencoder model.
        
        Args:
            input_dim: Number of input features
            latent_dim: Dimension of latent space
            hidden_dims: List of hidden layer dimensions
            dropout_rate: Dropout rate for regularization
            learning_rate: Learning rate for optimizer
        """
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.hidden_dims = hidden_dims
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        
        self.model: Optional[Model] = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.reconstruction_threshold: Optional[float] = None
        
        self._build_model()
        
        logger.info("Autoencoder Anomaly Detector initialized")
    
    def _build_model(self):
        """Build the autoencoder architecture."""
        # Input layer
        input_layer = layers.Input(shape=(self.input_dim,))
        
        # Encoder
        x = input_layer
        for dim in self.hidden_dims:
            x = layers.Dense(dim, activation='relu')(x)
            x = layers.Dropout(self.dropout_rate)(x)
        
        # Latent space
        latent = layers.Dense(self.latent_dim, activation='relu', name='latent')(x)
        
        # Decoder
        x = latent
        for dim in reversed(self.hidden_dims):
            x = layers.Dense(dim, activation='relu')(x)
            x = layers.Dropout(self.dropout_rate)(x)
        
        # Output layer
        output_layer = layers.Dense(self.input_dim, activation='linear')(x)
        
        # Create model
        self.model = Model(inputs=input_layer, outputs=output_layer, name='autoencoder')
        
        # Compile
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        logger.info(f"Autoencoder architecture built: {self.input_dim} → {self.hidden_dims} → {self.latent_dim}")
    
    def train(
        self,
        X: np.ndarray,
        validation_split: float = 0.2,
        epochs: int = 50,
        batch_size: int = 256,
        verbose: int = 0
    ) -> Dict:
        """
        Train the autoencoder on normal (non-fraudulent) transactions.
        
        Args:
            X: Feature matrix (should contain only legitimate transactions)
            validation_split: Fraction of data for validation
            epochs: Number of training epochs
            batch_size: Batch size for training
            verbose: Verbosity level
            
        Returns:
            Training history dictionary
        """
        logger.info(f"Training Autoencoder on {len(X)} samples...")
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=0
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                verbose=0
            )
        ]
        
        # Train (autoencoder tries to reconstruct input)
        history = self.model.fit(
            X_scaled,
            X_scaled,  # Target is same as input
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose
        )
        
        self.is_trained = True
        
        # Calculate reconstruction threshold (95th percentile of training errors)
        reconstructions = self.model.predict(X_scaled, verbose=0)
        reconstruction_errors = np.mean(np.square(X_scaled - reconstructions), axis=1)
        self.reconstruction_threshold = float(np.percentile(reconstruction_errors, 95))
        
        metrics = {
            'train_samples': len(X),
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1]),
            'reconstruction_threshold': self.reconstruction_threshold,
            'epochs_trained': len(history.history['loss'])
        }
        
        logger.info(
            f"Training complete. Final loss: {metrics['final_loss']:.6f}, "
            f"Threshold: {self.reconstruction_threshold:.6f}"
        )
        
        return metrics
    
    def predict_anomaly_score(self, X: np.ndarray) -> float:
        """
        Predict anomaly score for a single transaction.
        
        Higher score = more anomalous = more likely fraud
        
        Args:
            X: Feature vector (can be 1D or 2D)
            
        Returns:
            Anomaly score (0-1 range, normalized by threshold)
        """
        if not self.is_trained:
            # Return random score if not trained
            return float(np.random.random())
        
        # Ensure X is 2D
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get reconstruction
        reconstruction = self.model.predict(X_scaled, verbose=0)
        
        # Calculate reconstruction error (MSE)
        reconstruction_error = np.mean(np.square(X_scaled - reconstruction), axis=1)[0]
        
        # Normalize by threshold to get 0-1 score
        if self.reconstruction_threshold is not None and self.reconstruction_threshold > 0:
            anomaly_score = min(reconstruction_error / self.reconstruction_threshold, 1.0)
        else:
            anomaly_score = min(reconstruction_error, 1.0)
        
        return float(anomaly_score)
    
    def predict_batch(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomaly scores for multiple transactions.
        
        Args:
            X: Feature matrix
            
        Returns:
            Array of anomaly scores
        """
        if not self.is_trained:
            return np.random.random(len(X))
        
        X_scaled = self.scaler.transform(X)
        reconstructions = self.model.predict(X_scaled, verbose=0)
        reconstruction_errors = np.mean(np.square(X_scaled - reconstructions), axis=1)
        
        # Normalize by threshold
        if self.reconstruction_threshold is not None and self.reconstruction_threshold > 0:
            anomaly_scores = np.minimum(
                reconstruction_errors / self.reconstruction_threshold,
                1.0
            )
        else:
            anomaly_scores = np.minimum(reconstruction_errors, 1.0)
        
        return anomaly_scores
    
    def get_latent_representation(self, X: np.ndarray) -> np.ndarray:
        """
        Get latent space representation of transactions.
        
        Useful for visualization and clustering.
        
        Args:
            X: Feature matrix
            
        Returns:
            Latent representations
        """
        if not self.is_trained:
            return np.random.randn(len(X), self.latent_dim)
        
        X_scaled = self.scaler.transform(X)
        
        # Create encoder model
        encoder = Model(
            inputs=self.model.input,
            outputs=self.model.get_layer('latent').output
        )
        
        return encoder.predict(X_scaled, verbose=0)
    
    def save(self, filepath: str):
        """Save model to disk."""
        import joblib
        
        # Save Keras model
        self.model.save(filepath)
        
        # Save scaler and metadata
        metadata_path = filepath.replace('.h5', '_metadata.pkl')
        joblib.dump({
            'scaler': self.scaler,
            'reconstruction_threshold': self.reconstruction_threshold,
            'is_trained': self.is_trained,
            'input_dim': self.input_dim,
            'latent_dim': self.latent_dim,
            'hidden_dims': self.hidden_dims
        }, metadata_path)
        
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model from disk."""
        import joblib
        
        # Load Keras model
        self.model = keras.models.load_model(filepath)
        
        # Load scaler and metadata
        metadata_path = filepath.replace('.h5', '_metadata.pkl')
        metadata = joblib.load(metadata_path)
        
        self.scaler = metadata['scaler']
        self.reconstruction_threshold = metadata['reconstruction_threshold']
        self.is_trained = metadata['is_trained']
        self.input_dim = metadata['input_dim']
        self.latent_dim = metadata['latent_dim']
        self.hidden_dims = metadata['hidden_dims']
        
        logger.info(f"Model loaded from {filepath}")
    
    def get_model_info(self) -> Dict:
        """Get model information."""
        return {
            'model_type': 'Autoencoder Anomaly Detector',
            'is_trained': self.is_trained,
            'input_dim': self.input_dim,
            'latent_dim': self.latent_dim,
            'hidden_dims': self.hidden_dims,
            'reconstruction_threshold': self.reconstruction_threshold,
            'total_parameters': self.model.count_params() if self.model else 0
        }


def create_synthetic_normal_data(n_samples: int = 10000, n_features: int = 50) -> np.ndarray:
    """
    Create synthetic normal transaction data for training.
    
    Args:
        n_samples: Number of samples
        n_features: Number of features
        
    Returns:
        Feature matrix of normal transactions
    """
    # Generate from normal distribution
    X = np.random.randn(n_samples, n_features)
    
    # Add some correlations between features
    X[:, 1] = X[:, 0] * 0.5 + np.random.randn(n_samples) * 0.5
    X[:, 2] = X[:, 0] * 0.3 + X[:, 1] * 0.3 + np.random.randn(n_samples) * 0.4
    
    return X


if __name__ == "__main__":
    # Demo: Train autoencoder on synthetic data
    logger.info("Creating synthetic normal transaction data...")
    X_normal = create_synthetic_normal_data(n_samples=10000, n_features=50)
    
    logger.info("Training Autoencoder...")
    model = AutoencoderAnomalyDetector(input_dim=50)
    metrics = model.train(X_normal, epochs=30, verbose=1)
    
    logger.info("Training Metrics:")
    logger.info(f"  Final Loss: {metrics['final_loss']:.6f}")
    logger.info(f"  Reconstruction Threshold: {metrics['reconstruction_threshold']:.6f}")
    
    # Test on normal and anomalous samples
    normal_sample = X_normal[0:1]
    anomalous_sample = np.random.randn(1, 50) * 3  # Anomalous (different distribution)
    
    normal_score = model.predict_anomaly_score(normal_sample)
    anomalous_score = model.predict_anomaly_score(anomalous_sample)
    
    logger.info(f"Normal transaction score: {normal_score:.4f}")
    logger.info(f"Anomalous transaction score: {anomalous_score:.4f}")
    
    # Save model
    model.save("autoencoder_model.h5")
    logger.info("Model saved successfully")
