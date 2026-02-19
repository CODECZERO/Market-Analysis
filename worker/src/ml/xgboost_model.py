"""
XGBoost Binary Classifier for Stock Signals
Predicts whether stock will rise >2% in next 30 days
Uses 40+ features: technical + fundamental + sentiment + correlation
Includes SHAP values for explainability
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

try:
    import xgboost as xgb
    from sklearn.model_selection import TimeSeriesSplit, cross_val_score
    import optuna
    import shap
    HAS_XGBOOST = True
    
    try:
        import torch
        HAS_CUDA = torch.cuda.is_available()
    except ImportError:
        HAS_CUDA = False

except ImportError:
    HAS_XGBOOST = False
    HAS_CUDA = False
    logging.warning("XGBoost/Optuna/SHAP not available")

logger = logging.getLogger(__name__)


class StockXGBoostClassifier:
    """
    XGBoost classifier for stock trading signals
    """
    
    def __init__(self, threshold_pct: float = 2.0):
        """
        Initialize classifier
        
        Args:
            threshold_pct: Percentage threshold for labeling (default 2%)
        """
        self.threshold_pct = threshold_pct
        self.model = None
        self.feature_names = None
        self.explainer = None
        
    def prepare_features(
        self,
        technical_indicators: Dict[str, any],
        fundamentals: Dict[str, any],
        sentiment_scores: Dict[str, any],
        correlation_features: Optional[Dict[str, any]] = None
    ) -> pd.Series:
        """
        Combine all features into a single feature vector
        
        Args:
            technical_indicators: Dict of technical indicators
            fundamentals: Dict of fundamental metrics
            sentiment_scores: Dict of sentiment scores
            correlation_features: Optional correlation features
            
        Returns:
            Series of features
        """
        features = {}
        
        # Technical features (15+)
        features['rsi_14'] = technical_indicators.get('rsi_14', 50)
        features['macd_histogram'] = technical_indicators.get('macd_histogram', 0)
        features['bb_width_pct'] = technical_indicators.get('bb_width_pct', 0)
        features['adx_14'] = technical_indicators.get('adx_14', 20)
        features['obv_change_20d'] = technical_indicators.get('obv_change_20d', 0)
        features['stoch_k'] = technical_indicators.get('stoch_k', 50)
        features['atr_pct'] = technical_indicators.get('atr_pct', 0)
        features['mfi_14'] = technical_indicators.get('mfi_14', 50)
        features['price_vs_sma50'] = technical_indicators.get('price_vs_sma50', 0)
        features['price_vs_sma200'] = technical_indicators.get('price_vs_sma200', 0)
        features['price_vs_vwap'] = technical_indicators.get('price_vs_vwap', 0)
        features['price_position_in_bb'] = technical_indicators.get('price_position_in_bb', 0.5)
        features['macd_bullish'] = int(technical_indicators.get('macd_bullish', False))
        features['rsi_oversold'] = int(technical_indicators.get('rsi_oversold', False))
        features['rsi_overbought'] = int(technical_indicators.get('rsi_overbought', False))
        
        # Fundamental features (10+)
        features['pe_ratio'] = fundamentals.get('pe_ratio', 20)
        features['pb_ratio'] = fundamentals.get('pb_ratio', 3)
        features['roe'] = fundamentals.get('roe', 15)
        features['debt_to_equity'] = fundamentals.get('debt_to_equity', 1)
        features['current_ratio'] = fundamentals.get('current_ratio', 1.5)
        features['revenue_growth_yoy'] = fundamentals.get('revenue_growth_yoy', 0)
        features['profit_growth_yoy'] = fundamentals.get('profit_growth_yoy', 0)
        features['dividend_yield'] = fundamentals.get('dividend_yield', 0)
        features['fcf_margin'] = fundamentals.get('fcf_margin', 0)
        features['ebitda_margin'] = fundamentals.get('ebitda_margin', 0)
        
        # Sentiment features (5+)
        features['social_sentiment'] = sentiment_scores.get('social_sentiment', 0)
        features['news_sentiment'] = sentiment_scores.get('news_sentiment', 0)
        features['sentiment_velocity'] = sentiment_scores.get('sentiment_velocity', 0)
        features['post_volume_7d'] = sentiment_scores.get('post_volume_7d', 0)
        features['engagement_score'] = sentiment_scores.get('engagement_score', 0)
        
        # Correlation features (optional, 10+)
        if correlation_features:
            features['price_to_market_corr'] = correlation_features.get('price_to_market_corr', 0.5)
            features['sentiment_to_price_lag1'] = correlation_features.get('sentiment_to_price_lag1', 0)
            features['sentiment_to_price_lag3'] = correlation_features.get('sentiment_to_price_lag3', 0)
            features['volume_to_price_corr'] = correlation_features.get('volume_to_price_corr', 0)
            features['sector_correlation'] = correlation_features.get('sector_correlation', 0.5)
        
        return pd.Series(features)
    
    def create_labels(
        self,
        prices: pd.Series,
        forward_days: int = 30
    ) -> pd.Series:
        """
        Create binary labels: 1 if price rises >threshold% in forward_days, 0 otherwise
        
        Args:
            prices: Price series
            forward_days: Days to look forward
            
        Returns:
            Binary label series
        """
        future_returns = prices.pct_change(forward_days).shift(-forward_days)
        labels = (future_returns > self.threshold_pct / 100).astype(int)
        return labels
    
    def tune_hyperparameters(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        n_trials: int = 50
    ) -> Dict[str, any]:
        """
        Tune hyperparameters using Optuna
        
        Args:
            X_train: Training features
            y_train: Training labels
            n_trials: Number of optimization trials
            
        Returns:
            Best hyperparameters
        """
        if not HAS_XGBOOST:
            raise ImportError("XGBoost not installed")
        
        def objective(trial):
            params = {
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('lr', 0.01, 0.3),
                'n_estimators': trial.suggest_int('n_est', 100, 1000),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample', 0.6, 1.0),
                'reg_alpha': trial.suggest_float('alpha', 0.0, 10.0),
                'reg_lambda': trial.suggest_float('lambda', 1.0, 10.0),
                'min_child_weight': trial.suggest_int('min_child', 1, 10),
                'use_label_encoder': False,
                'eval_metric': 'logloss',
                'random_state': 42,
                'device': 'cuda' if HAS_CUDA else 'cpu',
                'tree_method': 'hist'
            }
            
            model = xgb.XGBClassifier(**params)
            
            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=5)
            scores = cross_val_score(model, X_train, y_train, cv=tscv, scoring='accuracy')
            
            return scores.mean()
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        
        return study.best_params
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        params: Optional[Dict[str, any]] = None
    ):
        """
        Train XGBoost model
        
        Args:
            X_train: Training features
            y_train: Training labels
            params: Optional hyperparameters (will use default if None)
        """
        if not HAS_XGBOOST:
            raise ImportError("XGBoost not installed")
        
        # Calculate class imbalance adjustment (CS229)
        num_pos = y_train.sum()
        num_neg = len(y_train) - num_pos
        scale_pos_weight = num_neg / num_pos if num_pos > 0 else 1.0
        
        if params is None:
            params = {
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 200,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'reg_alpha': 0.1,
                'reg_lambda': 1.0,
                'scale_pos_weight': scale_pos_weight, # Correct for imbalance
                'use_label_encoder': False,
                'eval_metric': 'logloss',
                'random_state': 42,
                'device': 'cuda' if HAS_CUDA else 'cpu',
                'tree_method': 'hist'
            }
        
        self.model = xgb.XGBClassifier(**params)
        self.model.fit(X_train, y_train)
        self.feature_names = X_train.columns.tolist()
        
        # Create SHAP explainer
        try:
            self.explainer = shap.TreeExplainer(self.model)
        except:
            logger.warning("Could not create SHAP explainer")
    
    def predict(
        self,
        X: pd.DataFrame,
        return_shap: bool = True
    ) -> Dict[str, any]:
        """
        Predict with SHAP explanation
        
        Args:
            X: Feature dataframe
            return_shap: Whether to compute SHAP values
            
        Returns:
            Prediction results with explanation
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        # Prediction
        proba = self.model.predict_proba(X)[:, 1]  # Probability of class 1 (BUY)
        prediction = (proba >= 0.5).astype(int)
        
        result = {
            'signal': 'BUY' if prediction[0] == 1 else 'SELL',
            'probability': float(proba[0]),
            'confidence': 'HIGH' if abs(proba[0] - 0.5) > 0.3 else 'MEDIUM' if abs(proba[0] - 0.5) > 0.15 else 'LOW',
        }
        
        # SHAP values for explainability
        if return_shap and self.explainer:
            try:
                shap_values = self.explainer.shap_values(X)
                
                # Get top features contributing to prediction
                shap_abs = np.abs(shap_values[0])
                top_indices = np.argsort(shap_abs)[-5:][::-1]  # Top 5
                
                result['shap_explanation'] = {
                    'top_features': [
                        {
                            'feature': self.feature_names[i],
                            'value': float(X.iloc[0, i]),
                            'shap_value': float(shap_values[0][i]),
                            'impact': 'POSITIVE' if shap_values[0][i] > 0 else 'NEGATIVE'
                        }
                        for i in top_indices
                    ],
                    'base_value': float(self.explainer.expected_value)
                }
            except Exception as e:
                logger.error(f"SHAP calculation failed: {e}")
        
        # Feature importance
        feature_importance = self.model.feature_importances_
        top_important_indices = np.argsort(feature_importance)[-5:][::-1]
        
        result['feature_importance'] = [
            {
                'feature': self.feature_names[i],
                'importance': float(feature_importance[i])
            }
            for i in top_important_indices
        ]
        
        return result


def quick_xgb_signal(
    technical_indicators: Dict[str, any],
    fundamentals: Dict[str, any],
    sentiment_scores: Dict[str, any]
) -> Dict[str, any]:
    """
    Quick XGBoost signal using a simple heuristic-based approach
    (Use when model is not trained)
    
    Args:
        technical_indicators: Technical indicator dict
        fundamentals: Fundamental metrics dict
        sentiment_scores: Sentiment scores dict
        
    Returns:
        Signal with heuristic-based probability
    """
    def _safe_num(val, default=0.0):
        if val is None: return default
        try:
            fval = float(val)
            return fval if not np.isnan(fval) else default
        except: return default

    score = 50
    reasons = []

    # Technical signals (50 points max)
    if technical_indicators.get('rsi_oversold'):
        score += 15
        reasons.append("RSI oversold (buy signal)")
    elif technical_indicators.get('rsi_overbought'):
        score -= 15
        reasons.append("RSI overbought (sell signal)")
    
    if technical_indicators.get('macd_bullish'):
        score += 10
        reasons.append("MACD bullish crossover")
    
    if _safe_num(technical_indicators.get('price_vs_sma50', 0)) > 0:
        score += 10
        reasons.append("Price above 50-day SMA")
    
    # Fundamental signals (30 points max)
    pe = _safe_num(fundamentals.get('pe_ratio', 25))
    if pe < 15:
        score += 15
        reasons.append("Low P/E ratio (undervalued)")
    elif pe > 40:
        score -= 10
        reasons.append("High P/E ratio (overvalued)")
    
    if _safe_num(fundamentals.get('revenue_growth_yoy', 0)) > 15:
        score += 15
        reasons.append("Strong revenue growth")
    
    # Sentiment signals (20 points max)
    news_sent = _safe_num(sentiment_scores.get('news_sentiment', 0))
    if news_sent > 0.3:
        score += 10
        reasons.append("Positive news sentiment")
    elif news_sent < -0.3:
        score -= 10
        reasons.append("Negative news sentiment")
    
    # Convert score to probability (0-100 score → 0-1 probability)
    probability = max(0, min(1, (score + 50) / 100))
    
    return {
        'signal': 'BUY' if probability > 0.6 else 'SELL' if probability < 0.4 else 'HOLD',
        'probability': float(probability),
        'confidence': 'MEDIUM',
        'model': 'HEURISTIC_FALLBACK',
        'reasons': reasons,
        'score': score
    }
