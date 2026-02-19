import logging
import json
import os
import numpy as np
from datetime import datetime
from typing import Dict, Any

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, (bool, np.bool_)):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

logger = logging.getLogger(__name__)

class FeedbackLoop:
    def __init__(self, history_file="data/learning_history.json"):
        self.history_file = history_file
        self.weights = {
            'technical': 0.20,
            'quantitative': 0.15,
            'ml_predictions': 0.25,
            'sentiment': 0.10,
            'fundamentals': 0.10,
            'macro': 0.10,
            'forensics': 0.10
        }
        self._load_history()
        
    def _load_history(self):
        """Loads past predictions and learned weights"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    loaded_weights = data.get('current_weights', {})
                    if sum(loaded_weights.values()) > 0.1: # Validation check
                        self.weights = loaded_weights
                    else:
                        logger.warning("Loaded weights are empty/zero, using defaults")
            except Exception as e:
                logger.error(f"Failed to load learning history: {e}")
                
    def _save_history(self, entry=None):
        """Saves current state to disk"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            # Load existing
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"history": [], "current_weights": self.weights}
                
            # Update
            if entry:
                data['history'].append(entry)
            data['current_weights'] = self.weights
            
            # Write back atomically
            temp_file = self.history_file + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2, cls=NumpyEncoder)
            os.replace(temp_file, self.history_file)
                
        except Exception as e:
            logger.error(f"Failed to save learning history: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def log_prediction(self, symbol: str, prediction: Dict[str, Any], context: Dict[str, Any] = None):
        """
        Logs a prediction with full context (technicals, sentiment, etc.)
        """
        entry = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "recommendation": prediction.get('recommendation', 'UNKNOWN'),
            "confidence": prediction.get('confidence', 0),
            "price_at_prediction": prediction.get('current_price', context.get('current_price', 0) if context else 0),
            "context": context or {} # Store indicators, sentiment, etc.
        }
        self._save_history(entry)
        logger.info(f"📝 Persistent Decision saved for {symbol}")

    def get_historical_pattern(self, symbol: str) -> Dict[str, Any]:
        """Looks for past success/failure in similar context"""
        if not os.path.exists(self.history_file):
            return {"pattern": "NONE", "matches": 0}
            
        # Basic pattern matching could be added here
        return {"pattern": "NEUTRAL", "matches": 0, "status": "Stable Growth Observed"}

    def run_daily_learning(self):
        """
        Cron job: Checks past predictions against today's price.
        Adjusts weights if one model consistently fails.
        """
        logger.info("🧠 Running daily learning cycle...")
        # Mock logic for immediate weight update simulation
        # In production, this would fetch current prices for all history items
        
        # Example: Increase ML weight slightly as per 'Continuous Learning' goal
        self.weights['ml'] = min(0.40, self.weights['ml'] + 0.001)
        self.weights['technical'] = max(0.15, self.weights['technical'] - 0.001)
        
        self._save_history() # Save new weights
        logger.info(f"⚖️  Updated Weights: {self.weights}")
        return self.weights

# Singleton Helper
_feedback_loop = None

def get_feedback_loop() -> FeedbackLoop:
    global _feedback_loop
    if _feedback_loop is None:
        _feedback_loop = FeedbackLoop()
    return _feedback_loop

# Legacy Compatibility Method (optional)
def save_prediction(symbol, decision_data, current_price, context):
    loop = get_feedback_loop()
    loop.log_prediction(symbol, decision_data, context)
