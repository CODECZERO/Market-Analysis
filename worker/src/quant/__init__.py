"""
Quantitative Analysis Module
Wall Street-grade algorithms for Indian stock market
"""

from .pairs_trading import (
    find_cointegrated_pairs,
    generate_pairs_signals,
    scan_pairs_opportunities,
    KalmanFilter
)

from .momentum import (
    calculate_momentum_scores,
    generate_momentum_signals,
    momentum_rank_for_stock
)

from .mean_reversion import (
    calculate_zscore,
    generate_mean_reversion_signals,
    backtest_mean_reversion
)

from .hmm_regime import (
    detect_market_regime,
    calculate_regime_persistence
)

from .fama_french import (
    calculate_fama_french_alpha,
    estimate_smb_hml_factors
)

__all__ = [
    # Pairs Trading
    'find_cointegrated_pairs',
    'generate_pairs_signals',
    'scan_pairs_opportunities',
    'KalmanFilter',
    
    # Momentum
    'calculate_momentum_scores',
    'generate_momentum_signals',
    'momentum_rank_for_stock',
    
    # Mean Reversion
    'calculate_zscore',
    'generate_mean_reversion_signals',
    'backtest_mean_reversion',
    
    # Regime Detection
    'detect_market_regime',
    'calculate_regime_persistence',
    
    # Fama-French
    'calculate_fama_french_alpha',
    'estimate_smb_hml_factors',
]
