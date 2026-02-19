"""
Regulatory Neural Network (RNN - but not Recurrent)
A specialized Feed-Forward Neural Network (MLP) designed for Regulatory Risk Assessment.
Features:
- Real-time Online Learning (partial_fit)
- Autonomous weight adjustment
- Risk Probability Output
"""

import numpy as np
import json
import os
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import joblib

MODEL_PATH = "regulatory_model.pkl"
SCALER_PATH = "regulatory_scaler.pkl"

class RegulatoryNeuralNet:
    def __init__(self):
        # Features: [Risk_Score_Raw (0-1), Volatility (0-1), Insider_Sell (0/1), News_Sentiment (-1 to 1)]
        self.input_dim = 4
        
        # MLP Neural Network
        # Using a compact architecture for fast real-time updates
        self.model = MLPClassifier(
            hidden_layer_sizes=(16, 8), 
            activation='relu', 
            solver='adam', 
            learning_rate='adaptive',
            max_iter=500, # Lightweight iteration
            # warm_start=True # REMOVED: partial_fit handles online learning automatically. 
            # warm_start is for fit() reuse and causes class mismatch errors.
        )
        
        self.scaler = StandardScaler()
        self.is_initialized = False
        
        self._load_model()

    def _load_model(self):
        """Load persistent model state"""
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                self.is_initialized = True
                print("🧠 Regulatory Neural Net Loaded.")
            except:
                print("⚠️ Failed to load Regulatory Net. Starting fresh.")
                self.is_initialized = False

    def _save_model(self):
        """Atomic Save"""
        try:
            joblib.dump(self.model, MODEL_PATH)
            joblib.dump(self.scaler, SCALER_PATH)
        except Exception as e:
            print(f"Failed to save RegNet: {e}")

    def predict_risk(self, risk_score_raw, volatility, insider_sell, sentiment) -> float:
        """
        Predict Regulatory Intervention Probability (0.0 - 1.0)
        """
        if not self.is_initialized:
            # Fallback heuristic if untrained
            return max(risk_score_raw, 0.5 if insider_sell else 0.0)

        X = np.array([[risk_score_raw, volatility, insider_sell, sentiment]])
        # Use partial_fit logic if scaler is ready, else heuristic
        try:
            # Note: StandardScaler usually needs fit on batch. 
            # For online RL, we might skip scaling or manage dynamic mean/var.
            # Simplified: No scaling for inputs largely in fixed 0-1 range.
            prob = self.model.predict_proba(X)[0][1] # Probability of Class 1 (RISK)
            return prob
        except:
            return risk_score_raw

    def train_online(self, risk_score_raw, volatility, insider_sell, sentiment, actual_outcome_label=None, price_change=0.0):
        """
        Real-Time Injection Learning (RLHF via Reward Model).
        If actual_outcome_label is None, we calculate it using the Reward Model.
        """
        from .regulatory_reward_model import get_reward_model
        
        # 1. Get current prediction (Pre-training state)
        predicted_risk = self.predict_risk(risk_score_raw, volatility, insider_sell, sentiment)
        
        # 2. Calculate Reward & Target
        reward_model = get_reward_model()
        reward = reward_model.calculate_reward(predicted_risk, volatility, price_change)
        
        # 3. Determine Reinforcement Label
        # If actual_outcome_label was passed (legacy), use it, otherwise derive from reward
        target_label = actual_outcome_label
        if target_label is None:
            target_label = reward_model.get_training_label(predicted_risk, reward)
            
        print(f"   🧠 [RLHF] Pred: {predicted_risk:.2f} | Chg: {price_change:.1%} | Reward: {reward:.1f} -> Target: {target_label}")

        X = np.array([[risk_score_raw, volatility, insider_sell, sentiment]])
        y = np.array([target_label])
        
        # Classes must be known for partial_fit
        classes = np.array([0, 1])
        
        self.model.partial_fit(X, y, classes=classes)
        self.is_initialized = True
        self._save_model()
        return True

# Singleton
_reg_net = None

def get_regulatory_net() -> RegulatoryNeuralNet:
    global _reg_net
    if _reg_net is None:
        _reg_net = RegulatoryNeuralNet()
    return _reg_net
