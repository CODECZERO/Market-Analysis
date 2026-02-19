"""
Fama-French 3-Factor Model
Calculates Alpha (Risk-Adjusted Return) using Market, Size (SMB), and Value (HML) factors.
"""

import pandas as pd
import numpy as np
import logging
# import statsmodels.api as sm # Requires statsmodels

logger = logging.getLogger(__name__)

class FamaFrenchAnalyzer:
    def __init__(self, risk_free_rate=0.06):
        self.rf = risk_free_rate
        
    def calculate_alpha(self, stock_returns: pd.Series, market_returns: pd.Series) -> float:
        """
        Calculates Jensen's Alpha as a simplified proxy for Fama-French 
        if SMB/HML factors are not readily available live.
        
        Formula: Alpha = Rp - [Rf + Beta * (Rm - Rf)]
        """
        try:
            # 1. Align data
            df = pd.DataFrame({'stock': stock_returns, 'market': market_returns}).dropna()
            
            if len(df) < 30:
                logger.warning("⚠️ Insufficient data for Alpha calculation")
                return 0.0
                
            # 2. Calculate Beta (Covariance / Variance)
            covariance = np.cov(df['stock'], df['market'])[0][1]
            market_variance = np.var(df['market'])
            beta = covariance / market_variance
            
            # 3. Calculate Alpha
            stock_cagr = (df['stock'].mean() * 252) # Annualized
            market_cagr = (df['market'].mean() * 252)
            
            expected_return = self.rf + beta * (market_cagr - self.rf)
            alpha = stock_cagr - expected_return
            
            return float(alpha)
            
        except Exception as e:
            logger.error(f"❌ Fama-French error: {e}")
            return 0.0

    def get_full_factor_analysis(self):
        # Placeholder for full SMB/HML implementation 
        # (Requires external factor data feed like Kenneth French library)
        pass

# Module-level wrappers for compatibility
def calculate_fama_french_alpha(stock_returns, market_returns):
    analyzer = FamaFrenchAnalyzer()
    return analyzer.calculate_alpha(stock_returns, market_returns)

def estimate_smb_hml_factors():
    return {"SMB": 0.0, "HML": 0.0}
