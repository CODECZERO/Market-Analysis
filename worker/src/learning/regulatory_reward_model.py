"""
Regulatory Reward Model (RLHF Component)
mathematically calculates the 'Reward' for the Regulatory Neural Network.
Based on 'Constitutional AI' principles:
- Reward = (Risk Avoidance * Impact) + (Profitability * Weight) - False_Positive_Penalty
"""

import numpy as np

class RegulatoryRewardModel:
    def __init__(self):
        # Principles inspired by Safe RL
        self.risk_aversion_factor = 2.0
        self.false_positive_penalty = 0.5
        
    def calculate_reward(self, predicted_risk: float, actual_volatility: float, price_change: float) -> float:
        """
        Calculates a scaler reward (-1.0 to +1.0) for the network's action.
        
        Math Model:
        If Predicted High Risk (>0.5):
            Reward = +1 if Price Crashed (Avoided Loss)
            Reward = -1 if Price Rallied (Missed Opportunity/False Positive)
            
        If Predicted Low Risk (<0.5):
            Reward = +1 if Price Rallied (Captured Gain)
            Reward = -2 if Price Crashed (Safety Failure - Higher Penalty)
        """
        
        # Define what constitutes a "Crash" (Regulatory Event usually causes >3% drop)
        is_crash = price_change < -0.03
        is_rally = price_change > 0.02
        
        reward = 0.0
        
        if predicted_risk > 0.5:
            # AI declared RISK
            if is_crash:
                # GOOD: We predicted the crash.
                reward = 1.0 * self.risk_aversion_factor
            elif is_rally:
                # BAD: We feared a rally. False Positive.
                reward = -1.0 * self.false_positive_penalty
            else:
                # Neutral: Market was flat. Slight penalty for fear-mongering.
                reward = -0.1
                
        else:
            # AI declared SAFE
            if is_crash:
                # TERRIBLE: We failed to predict a crash.
                reward = -2.0 * self.risk_aversion_factor # Heavy penalty
            elif is_rally:
                # GOOD: We stayed in and profited.
                reward = 1.0
            else:
                reward = 0.1 # Small reward for stability
                
        # Scikit-Learn MLP partial_fit takes a LABEL (0 or 1), not a scalar reward.
        # We must convert this "Reward" into a training Signal.
        # If Reward > 0: Reinforce the original decision (Train with Prediction rounded)
        # If Reward < 0: Train with OPPOSITE of prediction
        
        return max(-2.0, min(2.0, reward)) # Clip

    def get_training_label(self, predicted_risk: float, reward: float) -> int:
        """
        Converts scalar reward to binary target for Cross-Entropy Loss optimization (via MLP).
        """
        current_prediction_class = 1 if predicted_risk > 0.5 else 0
        
        if reward > 0:
            return current_prediction_class # You were right, reinforce it.
        else:
            return 1 - current_prediction_class # You were wrong, flip it.

_reward_model = None
def get_reward_model():
    global _reward_model
    if _reward_model is None:
        _reward_model = RegulatoryRewardModel()
    return _reward_model
