"""
Transformer Model for Price Prediction
Uses Multi-Head Attention to capture long-term dependencies in price data.
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, LayerNormalization, MultiHeadAttention, Dropout, GlobalAveragePooling1D
from tensorflow.keras.models import Model
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class TransformerModel:
    def __init__(self, seq_len=60, d_model=128, num_heads=4, num_layers=2, dff=256, dropout_rate=0.1):
        self.seq_len = seq_len
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.dff = dff
        self.dropout_rate = dropout_rate
        self.model = self._build_model()
        
    def _build_model(self) -> Model:
        inputs = Input(shape=(self.seq_len, self.d_model))
        x = inputs
        
        for _ in range(self.num_layers):
            # Multi-Head Attention
            attn_output = MultiHeadAttention(num_heads=self.num_heads, key_dim=self.d_model)(x, x)
            x = LayerNormalization(epsilon=1e-6)(x + attn_output)
            x = Dropout(self.dropout_rate)(x)
            
            # Feed Forward Network
            ffn = Dense(self.dff, activation="relu")(x)
            ffn = Dense(self.d_model)(ffn)
            x = LayerNormalization(epsilon=1e-6)(x + ffn)
            x = Dropout(self.dropout_rate)(x)
            
        # Output Head
        x = GlobalAveragePooling1D()(x)
        x = Dense(64, activation="relu")(x)
        x = Dropout(0.1)(x)
        outputs = Dense(4)(x) # 1d, 7d, 30d, 90d forecasts
        
        model = Model(inputs=inputs, outputs=outputs, name="price_transformer")
        model.compile(optimizer="adam", loss="mse", metrics=["mae"])
        return model

    def train(self, X_train, y_train, epochs=20, batch_size=32, validation_data=None):
        logger.info("🧠 Training Transformer model...")
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=validation_data,
            verbose=1
        )
        return history

    def predict(self, X) -> Dict[str, float]:
        preds = self.model.predict(X)[0] # Taking first sample
        return {
            "1d": float(preds[0]),
            "7d": float(preds[1]),
            "30d": float(preds[2]),
            "90d": float(preds[3]),
            "confidence": 0.85 # Placeholder, needs MC Dropout for real calc
        }
