"""
Optimized LSTM Model for Low-Memory GPU (4GB VRAM)
Designed for RTX 2050 - uses smaller architecture and batch processing
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Check if TensorFlow is available
try:
    import os
    os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices=false' # Disable XLA devices to stop spill warnings
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Suppress TF info/warnings
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
    
    # Configure TensorFlow for low memory
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            # Enable memory growth to avoid allocating all GPU memory
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            
            # Set memory limit to 3GB (leave 1GB for system)
            tf.config.set_logical_device_configuration(
                gpus[0],
                [tf.config.LogicalDeviceConfiguration(memory_limit=3072)]
            )
            logger.info(f"GPU configured with 3GB memory limit for {len(gpus)} GPU(s)")
        except RuntimeError as e:
            logger.warning(f"GPU configuration failed: {e}")
    else:
        logger.info("No GPU found, using CPU")
        
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow not available, using simple moving average fallback")


class OptimizedLSTMModel:
    """
    Lightweight LSTM for low-memory systems
    - Reduced model size (32 units instead of 128)
    - Batch processing
    - Mixed precision training
    - CPU fallback
    """
    
    def __init__(self, sequence_length: int = 30, features: int = 5):
        """
        Initialize optimized model
        
        Args:
            sequence_length: Number of days to look back (reduced from 60 to 30)
            features: Number of input features (reduced from 8 to 5)
        """
        self.sequence_length = sequence_length
        self.features = features
        self.model = None
        self.scaler = None
        
    def build_model(self):
        """Build lightweight LSTM architecture"""
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available, model not built")
            return
        
        # Use mixed precision for faster training (if GPU available)
        policy = tf.keras.mixed_precision.Policy('mixed_float16')
        tf.keras.mixed_precision.set_global_policy(policy)
        
        # Smaller architecture for low memory
        inputs = keras.Input(shape=(self.sequence_length, self.features))
        
        # Single LSTM layer with 32 units, added L2 regularization and higher dropout
        x = layers.LSTM(
            32, 
            return_sequences=False, 
            dropout=0.3,
            kernel_regularizer=keras.regularizers.l2(0.01)
        )(inputs)
        
        # Smaller dense layer with L2
        x = layers.Dense(16, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01))(x)
        x = layers.Dropout(0.3)(x)
        
        # Multi-output (1d, 7d, 30d predictions)
        outputs = layers.Dense(3, activation='linear', dtype='float32')(x)
        
        self.model = keras.Model(inputs=inputs, outputs=outputs)
        
        # Use Adam with lower learning rate
        optimizer = keras.optimizers.Adam(learning_rate=0.0005)
        self.model.compile(
            optimizer=optimizer,
            loss='huber',
            metrics=['mae']
        )
        
        logger.info(f"Model built with {self.model.count_params()} parameters")
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        batch_size: int = 16,  # Small batch size for low memory
        epochs: int = 20,
        validation_split: float = 0.2
    ):
        """
        Train model with memory-efficient settings
        
        Args:
            X_train: Training sequences
            y_train: Training targets
            batch_size: Batch size (keep small for low memory)
            epochs: Number of epochs
            validation_split: Validation data percentage
        """
        if not TENSORFLOW_AVAILABLE or self.model is None:
            logger.warning("Cannot train: TensorFlow not available or model not built")
            return
        
        # Early stopping to prevent overfitting
        early_stop = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        )
        
        # Reduce learning rate on plateau
        reduce_lr = keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=0.00001
        )
        
        # Train with small batches
        history = self.model.fit(
            X_train, y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_split=validation_split,
            callbacks=[early_stop, reduce_lr],
            verbose=0
        )
        
        logger.info(f"Training complete. Final loss: {history.history['loss'][-1]:.4f}")
    
    def predict_batch(
        self,
        sequences: np.ndarray,
        batch_size: int = 8  # Very small batch for inference
    ) -> np.ndarray:
        """
        Predict in small batches to avoid OOM
        
        Args:
            sequences: Input sequences
            batch_size: Batch size for prediction
            
        Returns:
            Predictions array
        """
        if not TENSORFLOW_AVAILABLE or self.model is None:
            logger.warning("Model not available, using fallback")
            return self._fallback_predict(sequences)
        
        predictions = []
        num_batches = int(np.ceil(len(sequences) / batch_size))
        
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(sequences))
            batch = sequences[start_idx:end_idx]
            
            pred = self.model.predict(batch, verbose=0)
            predictions.append(pred)
        
        return np.concatenate(predictions, axis=0)
    
    def _fallback_predict(self, sequences: np.ndarray) -> np.ndarray:
        """Simple moving average fallback when GPU not available"""
        # Use last known prices and simple trend
        predictions = []
        
        for seq in sequences:
            last_prices = seq[:, 0]  # Assume first feature is close price
            
            # Simple trend calculation
            recent_avg = np.mean(last_prices[-5:])
            trend = (last_prices[-1] - last_prices[-10]) / last_prices[-10]
            
            # Predict with simple linear trend
            pred_1d = recent_avg * (1 + trend * 0.2)
            pred_7d = recent_avg * (1 + trend * 0.5)
            pred_30d = recent_avg * (1 + trend * 1.0)
            
            predictions.append([pred_1d, pred_7d, pred_30d])
        
        return np.array(predictions)


def quick_lstm_prediction(
    price_df: pd.DataFrame,
    current_price: float,
    use_gpu: bool = True
) -> Dict:
    """
    Quick LSTM prediction optimized for low memory
    
    Args:
        price_df: DataFrame with close and volume
        current_price: Current stock price
        use_gpu: Whether to attempt GPU usage
        
    Returns:
        Dictionary with predictions
    """
    try:
        # Prepare minimal feature set (only 5 features)
        df = price_df.copy().tail(100)  # Use only last 100 days
        
        if len(df) < 30:
            logger.warning("Insufficient data for LSTM, using simple forecast")
            return _simple_forecast(current_price)
        
        # Calculate only essential features
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(10).std()
        df['volume_ma'] = df['volume'].rolling(10).mean()
        df = df.dropna()
        
        # Z-Score Standardization (CS229 best practice)
        # Centers data at 0 with unit variance, better for optimization
        features = ['close', 'volume', 'returns', 'volatility', 'volume_ma']
        normalized = df[features].copy()
        
        feature_stats = {} # Store for denormalization if needed
        
        for col in features:
            mean = normalized[col].mean()
            std = normalized[col].std()
            feature_stats[col] = {'mean': mean, 'std': std}
            
            if std > 0:
                # Standardize
                z_score = (normalized[col] - mean) / std
                # Robust outlier handling: Clip to 3 sigma (CS229)
                normalized[col] = z_score.clip(-3, 3)
            else:
                normalized[col] = 0.0
        
        # Create sequence
        sequence = normalized.values[-30:].reshape(1, 30, 5)
        
        # Load or create model
        model = OptimizedLSTMModel(sequence_length=30, features=5)
        
        if TENSORFLOW_AVAILABLE and use_gpu:
            model.build_model()
            # Predict
            predictions = model.predict_batch(sequence, batch_size=1)
            
            # Denormalize predictions (approximate)
            pred_1d = current_price * (1 + (predictions[0][0] - 0.5) * 0.1)
            pred_7d = current_price * (1 + (predictions[0][1] - 0.5) * 0.2)
            pred_30d = current_price * (1 + (predictions[0][2] - 0.5) * 0.3)
        else:
            # CPU fallback
            predictions = model._fallback_predict(sequence)
            pred_1d, pred_7d, pred_30d = predictions[0]
        
        return {
            'predictions': {
                '1d': float(pred_1d),
                '7d': float(pred_7d),
                '30d': float(pred_30d),
                '90d': float(pred_30d * 1.1)  # Simple extrapolation
            },
            'confidence': 0.65,  # Lower confidence for lightweight model
            'model': 'optimized_lstm',
            'gpu_used': TENSORFLOW_AVAILABLE and use_gpu
        }
        
    except Exception as e:
        logger.error(f"LSTM prediction failed: {e}, using fallback")
        return _simple_forecast(current_price)


def _simple_forecast(current_price: float) -> Dict:
    """Simple fallback forecast"""
    return {
        'predictions': {
            '1d': current_price * 1.005,
            '7d': current_price * 1.02,
            '30d': current_price * 1.05,
            '90d': current_price * 1.08
        },
        'confidence': 0.5,
        'model': 'simple_ma_fallback',
        'gpu_used': False
    }
