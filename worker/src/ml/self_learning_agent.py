import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import logging
from typing import Dict, Any, List, Optional
import os
import json

logger = logging.getLogger(__name__)

class SelfLearningAgent:
    """
    Self-Learning Agent that uses:
    1. Unsupervised Learning (K-Means) to find hidden market regimes.
    2. Reinforcement Learning logic to optimize model weights based on accuracy.
    """
    def __init__(self, history_file="data/learning_history.json"):
        self.history_file = history_file
        self.model = KMeans(n_clusters=5, random_state=42, n_init=10)
        self.regime_map = {
            0: "Quiet Accumulation",
            1: "Volatile Distribution",
            2: "Panic Exhaustion",
            3: "Institutional Trend",
            4: "Retail FOMO"
        }
        
    def discover_hidden_regime(self, current_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses unsupervised clustering to find which hidden regime the current market fits into.
        """
        try:
            # Load history to train/fit clustering
            if not os.path.exists(self.history_file):
                return {"regime": "Initial Learning", "confidence": 0.5, "id": -1}
                
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                history = data.get('history', [])
                
            if len(history) < 10:
                return {"regime": "Gathering Data", "confidence": 0.6, "id": -1}
                
            # Extract feature vectors for clustering
            # We focus on technical indicators and sentiment for regime discovery
            feature_list = []
            for entry in history:
                ctx = entry.get('context', {})
                tech = ctx.get('technicals', {})
                sent = ctx.get('sentiment', {}).get('score', 0)
                
                # Simplified vector: [RSI, ADX, Momentum, Sentiment]
                vec = [
                    tech.get('rsi', 50) / 100,
                    tech.get('adx', 25) / 100,
                    tech.get('mom', 0) / 10,
                    sent
                ]
                feature_list.append(vec)
                
            X = np.array(feature_list)
            self.model.fit(X)
            
            # Predict current
            curr_tech = current_features.get('technicals', {})
            curr_sent = current_features.get('sentiment', {}).get('score', 0)
            curr_vec = np.array([[
                curr_tech.get('rsi', 50) / 100,
                curr_tech.get('adx', 25) / 100,
                curr_tech.get('mom', 0) / 10,
                curr_sent
            ]])
            
            cluster_id = int(self.model.predict(curr_vec)[0])
            regime_name = self.regime_map.get(cluster_id, "Unknown Regime")
            
            return {
                "regime": regime_name,
                "cluster_id": cluster_id,
                "confidence": 0.85,
                "active_patterns": ["Low Volatility" if curr_tech.get('adx', 25) < 20 else "High Trend"]
            }
        except Exception as e:
            logger.error(f"UL Clustering Error: {e}")
            return {"regime": "Analysis Offline", "confidence": 0.0}

    def optimize_weights_rl(self, current_weights: Dict[str, float], performance_history: List[Dict]) -> Dict[str, float]:
        """
        Reinforcement Learning inspired weight adjustment.
        Increases weight of models that were correct in the detected regime.
        """
        if not performance_history:
            return current_weights
            
        new_weights = current_weights.copy()
        learning_rate = 0.05
        
        # In a real RL setup, this would be a policy gradient update
        # Here we use a simplified feedback loop:
        # If model gave BUY and price went UP -> Reward
        # If model gave SELL and price went DOWN -> Reward
        
        for entry in performance_history[-5:]: # Look at recent outcomes
            outcome = entry.get('outcome') # 'SUCCESS' or 'FAILURE'
            if outcome == 'SUCCESS':
                # Reward the primary model responsible
                responsible = entry.get('responsible_model', 'ml')
                if responsible in new_weights:
                    new_weights[responsible] = min(0.5, new_weights[responsible] + learning_rate)
            elif outcome == 'FAILURE':
                # Penalize
                responsible = entry.get('responsible_model', 'ml')
                if responsible in new_weights:
                    new_weights[responsible] = max(0.1, new_weights[responsible] - learning_rate)
                    
        # Normalize weights
        total = sum(new_weights.values())
        return {k: v/total for k, v in new_weights.items()}
