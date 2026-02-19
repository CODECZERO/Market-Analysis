"""
Hidden Markov Model for Market Regime Detection
Identifies BULL, BEAR, SIDEWAYS market states
Uses returns, volatility, and volume as observable features
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple
from hmmlearn import hmm
import logging

logger = logging.getLogger(__name__)


def detect_market_regime(
    returns: pd.Series,
    volatilities: pd.Series,
    volumes: pd.Series,
    n_states: int = 3
) -> Dict[str, any]:
    """
    Detect current market regime using Hidden Markov Model
    
    Args:
        returns: Daily returns series
        volatilities: Daily volatility series (e.g., rolling std)
        volumes: Daily volume series
        n_states: Number of hidden states (default 3: BULL, BEAR, SIDEWAYS)
        
    Returns:
        Dictionary with current regime and probabilities
    """
    # Prepare feature matrix
    df = pd.DataFrame({
        'returns': returns,
        'volatility': volatilities,
        'volume': volumes
    }).dropna()
    
    if len(df) < 60:
        return {
            'regime': 'UNKNOWN',
            'probability': 0,
            'error': f'Insufficient data: {len(df)} < 60'
        }
    
    # Standardize features
    X = df.values
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    
    try:
        # Fit Gaussian HMM
        model = hmm.GaussianHMM(
            n_components=n_states,
            covariance_type="full",
            n_iter=100,
            random_state=42
        )
        model.fit(X)
        
        # Predict states
        states = model.predict(X)
        state_probabilities = model.predict_proba(X)
        
        # Current state
        current_state = states[-1]
        current_probs = state_probabilities[-1]
        
        # Characterize states by mean returns
        state_characteristics = {}
        for state_id in range(n_states):
            state_mask = states == state_id
            state_mean_return = df['returns'][state_mask].mean()
            state_mean_vol = df['volatility'][state_mask].mean()
            state_characteristics[state_id] = {
                'mean_return': state_mean_return,
                'mean_volatility': state_mean_vol
            }
        
        # Sort states by mean return: 0=BEAR, 1=SIDEWAYS, 2=BULL
        sorted_states = sorted(
            state_characteristics.items(),
            key=lambda x: x[1]['mean_return']
        )
        
        state_labels = {
            sorted_states[0][0]: 'BEAR',
            sorted_states[1][0]: 'SIDEWAYS',
            sorted_states[2][0]: 'BULL'
        }
        
        # Get current regime
        current_regime = state_labels[current_state]
        current_regime_prob = current_probs[current_state]
        
        # Transition matrix
        transition_matrix = model.transmat_
        
        # Expected next state probabilities
        next_state_probs = transition_matrix[current_state]
        next_regime_probs = {
            state_labels[i]: float(next_state_probs[i])
            for i in range(n_states)
        }
        
        return {
            'regime': current_regime,
            'probability': float(current_regime_prob),
            'state_probabilities': {
                'BULL': float(current_probs[sorted_states[2][0]]),
                'SIDEWAYS': float(current_probs[sorted_states[1][0]]),
                'BEAR': float(current_probs[sorted_states[0][0]]),
            },
            'next_regime_probabilities': next_regime_probs,
            'state_characteristics': {
                'BULL': {
                    'mean_return_pct': float(sorted_states[2][1]['mean_return'] * 100),
                    'mean_volatility': float(sorted_states[2][1]['mean_volatility']),
                },
                'SIDEWAYS': {
                    'mean_return_pct': float(sorted_states[1][1]['mean_return'] * 100),
                    'mean_volatility': float(sorted_states[1][1]['mean_volatility']),
                },
                'BEAR': {
                    'mean_return_pct': float(sorted_states[0][1]['mean_return'] * 100),
                    'mean_volatility': float(sorted_states[0][1]['mean_volatility']),
                },
            },
            'confidence': 'HIGH' if current_regime_prob > 0.7 else 'MEDIUM' if current_regime_prob > 0.5 else 'LOW',
        }
        
    except Exception as e:
        logger.error(f"HMM regime detection failed: {e}")
        return {
            'regime': 'UNKNOWN',
            'probability': 0,
            'error': str(e)
        }


def calculate_regime_persistence(states: np.ndarray) -> Dict[str, float]:
    """
    Calculate how long each regime typically persists
    
    Args:
        states: Array of regime states over time
        
    Returns:
        Dictionary with average persistence in days for each regime
    """
    persistence = {}
    current_state = states[0]
    count = 1
    state_durations = {state: [] for state in np.unique(states)}
    
    for i in range(1, len(states)):
        if states[i] == current_state:
            count += 1
        else:
            state_durations[current_state].append(count)
            current_state = states[i]
            count = 1
    
    # Add last run
    state_durations[current_state].append(count)
    
    # Calculate average
    for state, durations in state_durations.items():
        persistence[int(state)] = float(np.mean(durations))
    
    return persistence
