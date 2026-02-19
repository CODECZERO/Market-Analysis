"""
LSTM Price Prediction Model
Multi-horizon price forecasting: 1d, 7d, 30d, 90d
Uses TensorFlow/Keras with proper time series validation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    logging.warning("TensorFlow not available, LSTM predictions will be disabled")

logger = logging.getLogger(__name__)


class StockLSTMPredictor:
    """
    LSTM model for multi-horizon stock price prediction
    Trained on OHLCV + technical indicators + sentiment
    """
    
    def __init__(
        self,
        sequence_length: int = 60,
        n_features: int = 8,
        n_outputs: int = 4  # 1d, 7d, 30d, 90d
    ):
        """
        Initialize LSTM predictor
        
        Args:
            sequence_length: Number of days of historical data to use
            n_features: Number of input features
            n_outputs: Number of prediction horizons
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.n_outputs = n_outputs
        self.model = None
        self.scaler_X = MinMaxScaler(feature_range=(0, 1))
        self.scaler_y = MinMaxScaler(feature_range=(0, 1))
        
    def build_model(self):
        """Build LSTM architecture"""
        if not HAS_TENSORFLOW:
            raise ImportError("TensorFlow not installed")
        
        model = Sequential([
            Input(shape=(self.sequence_length, self.n_features)),
            LSTM(128, return_sequences=True, dropout=0.2),
            LSTM(64, return_sequences=True, dropout=0.2),
            LSTM(32, return_sequences=False, dropout=0.15),
            Dense(64, activation='relu'),
            Dropout(0.1),
            Dense(32, activation='relu'),
            Dense(self.n_outputs)  # Multi-output: 1d, 7d, 30d, 90d prices
        ])
        
        model.compile(
            optimizer='adam',
            loss='huber',  # Robust to outliers
            metrics=['mae', 'mse']
        )
        
        self.model = model
        return model
    
    def prepare_data(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_column: str = 'close'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare time series data for LSTM
        
        Args:
            df: DataFrame with price and feature data
            feature_columns: List of feature column names
            target_column: Column to predict (default 'close')
            
        Returns:
            X, y arrays ready for training
        """
        # Extract features
        features = df[feature_columns].values
        target = df[target_column].values
        
        # Scale features
        features_scaled = self.scaler_X.fit_transform(features)
        
        # Create sequences and multi-horizon targets
        X, y = [], []
        
        for i in range(self.sequence_length, len(df) - 90):  # Need 90 days ahead for longest prediction
            # Input sequence
            X.append(features_scaled[i - self.sequence_length:i])
            
            # Multi-horizon targets: 1d, 7d, 30d, 90d ahead
            targets = [
                target[i + 1],   # 1 day
                target[i + 7],   # 7 days
                target[i + 30],  # 30 days
                target[i + 90],  # 90 days
            ]
            y.append(targets)
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale targets
        y_scaled = self.scaler_y.fit_transform(y)
        
        return X, y_scaled
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        epochs: int = 100,
        batch_size: int = 32
    ) -> Dict[str, any]:
        """
        Train LSTM model with early stopping
        
        Args:
            X_train, y_train: Training data
            X_val, y_val: Validation data
            epochs: Maximum epochs
            batch_size: Batch size
            
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
        
        # Callbacks
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6
        )
        
        # Train
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop, reduce_lr],
            verbose=0
        )
        
        return {
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1]),
            'epochs_trained': len(history.history['loss']),
            'stopped_early': len(history.history['loss']) < epochs
        }
    
    def predict(
        self,
        X: np.ndarray,
        confidence_level: float = 0.95
    ) -> Dict[str, any]:
        """
        Make predictions with uncertainty estimates
        
        Args:
            X: Input sequences
            confidence_level: Confidence level for intervals (default 0.95)
            
        Returns:
            Predictions with confidence intervals
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Make predictions
        y_pred_scaled = self.model.predict(X, verbose=0)
        
        # Inverse transform
        y_pred = self.scaler_y.inverse_transform(y_pred_scaled)
        
        # MC Dropout for uncertainty (run inference 50 times with dropout ON)
        mc_predictions = []
        for _ in range(50):
            mc_pred_scaled = self.model(X, training=True)  # training=True keeps dropout active
            mc_pred = self.scaler_y.inverse_transform(mc_pred_scaled.numpy())
            mc_predictions.append(mc_pred)
        
        mc_predictions = np.array(mc_predictions)
        
        # Calculate confidence intervals
        mean_pred = np.mean(mc_predictions, axis=0)
        std_pred = np.std(mc_predictions, axis=0)
        
        # For 95% CI, use 1.96 standard deviations
        z_score = 1.96 if confidence_level == 0.95 else 2.58 if confidence_level == 0.99 else 1.645
        ci_lower = mean_pred - z_score * std_pred
        ci_upper = mean_pred + z_score * std_pred
        
        # Return latest prediction
        latest_idx = -1
        
        return {
            'predictions': {
                '1d': float(y_pred[latest_idx][0]),
                '7d': float(y_pred[latest_idx][1]),
                '30d': float(y_pred[latest_idx][2]),
                '90d': float(y_pred[latest_idx][3]),
            },
            'confidence_intervals': {
                '1d': {
                    'lower': float(ci_lower[latest_idx][0]),
                    'upper': float(ci_upper[latest_idx][0]),
                },
                '7d': {
                    'lower': float(ci_lower[latest_idx][1]),
                    'upper': float(ci_upper[latest_idx][1]),
                },
                '30d': {
                    'lower': float(ci_lower[latest_idx][2]),
                    'upper': float(ci_upper[latest_idx][2]),
                },
                '90d': {
                    'lower': float(ci_lower[latest_idx][3]),
                    'upper': float(ci_upper[latest_idx][3]),
                },
            },
            'uncertainty': {
                '1d': float(std_pred[latest_idx][0]),
                '7d': float(std_pred[latest_idx][1]),
                '30d': float(std_pred[latest_idx][2]),
                '90d': float(std_pred[latest_idx][3]),
            },
            'confidence_level': confidence_level,
        }
    
    def save_model(self, filepath: str):
        """Save trained model"""
        if self.model:
            self.model.save(filepath)
    
    def load_model(self, filepath: str):
        """Load trained model"""
        if HAS_TENSORFLOW:
            self.model = load_model(filepath)


def quick_lstm_prediction(
    price_df: pd.DataFrame,
    current_price: float,
    feature_columns: Optional[List[str]] = None
) -> Dict[str, any]:
    """
    Quick LSTM prediction with pretrained model or simple forecast
    
    Args:
        price_df: DataFrame with historical OHLCV data
        current_price: Current price
        feature_columns: Feature columns to use
        
    Returns:
        Price predictions for multiple horizons
    """
    if not HAS_TENSORFLOW:
        # Fallback to simple moving average projection
        logger.warning("TensorFlow not available, using simple MA projection")
        returns_7d = price_df['close'].pct_change(7).mean()
        returns_30d = price_df['close'].pct_change(30).mean()
        
        return {
            'predictions': {
                '1d': current_price * (1 + returns_7d / 7),
                '7d': current_price * (1 + returns_7d),
                '30d': current_price * (1 + returns_30d),
                '90d': current_price * (1 + returns_30d * 3),
            },
            'confidence': 0.3,  # Low confidence for simple projection
            'model': 'MA_FALLBACK'
        }
    
    # For production, you would load a pre-trained model here
    # For now, return simple projection
    logger.info("Using simple projection (pre-trained model not implemented in quick mode)")
    
    returns_7d = price_df['close'].pct_change(7).mean()
    returns_30d = price_df['close'].pct_change(30).mean()
    volatility = price_df['close'].pct_change().std()
    
    return {
        'predictions': {
            '1d': current_price * (1 + returns_7d / 7),
            '7d': current_price * (1 + returns_7d),
            '30d': current_price * (1 + returns_30d),
            '90d': current_price * (1 + returns_30d * 3),
        },
        'volatility': float(volatility),
        'confidence': 0.4,
        'model': 'SIMPLE_PROJECTION',
        'note': 'Train full LSTM model for production use'
    }
