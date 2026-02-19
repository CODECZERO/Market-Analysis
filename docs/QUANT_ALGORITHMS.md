# Quantitative Algorithms Documentation

## 📐 Overview

Our system implements **6 institutional-grade quantitative strategies** from Wall Street.

---

## 1. 📈 Cross-Sectional Momentum

**File:** `worker/src/quant/momentum.py`

### Theory
Stocks that have performed well recently tend to continue performing well.

### Implementation
```python
def calculate_momentum_score(data):
    # Multi-timeframe momentum
    returns_1m = (data['Close'][-20:].pct_change().sum())
    returns_3m = (data['Close'][-60:].pct_change().sum()) 
    returns_6m = (data['Close'][-120:].pct_change().sum())
    
    # Weighted score
    score = (0.5 * returns_1m + 0.3 * returns_3m + 0.2 * returns_6m)
    
    # Normalize to -1 to +1
    return np.clip(score, -1, 1)
```

### Signals
- **> 0.6:** STRONG_BUY
- **0.3 to 0.6:** BUY  
- **-0.3 to 0.3:** HOLD
- **< -0.3:** SELL

### Best For
- Trending markets
- High liquidity stocks
- Medium-term trades (1-3 months)

---

## 2. 🔄 Mean Reversion with Z-Score

**File:** `worker/src/quant/mean_reversion.py`

### Theory
Prices that deviate significantly from their mean tend to revert back.

### Implementation
```python
def calculate_zscore(data, window=20):
    mean = data['Close'].rolling(window).mean()
    std = data['Close'].rolling(window).std()
    
    current_price = data['Close'].iloc[-1]
    current_mean = mean.iloc[-1]
    current_std = std.iloc[-1]
    
    zscore = (current_price - current_mean) / current_std
    return zscore
```

### Signals
- **Z < -2:** Oversold → BUY
- **-1 < Z < 1:** Fair value → HOLD
- **Z > 2:** Overbought → SELL

### Formula
```
Z-Score = (Price - Mean) / StdDev
```

### Best For
- Range-bound markets
- High volatility stocks
- Short-term trades (days to weeks)

---

## 3. 🔗 Pairs Trading with Kalman Filter

**File:** `worker/src/quant/pairs_trading.py`

### Theory
Find correlated stock pairs and trade the spread when it diverges.

### Implementation
```python
class PairsTrading:
    def __init__(self):
        self.kf = self._init_kalman_filter()
    
    def calculate_hedge_ratio(self, stock1, stock2):
        # Dynamic hedge ratio via Kalman
        for price1, price2 in zip(stock1, stock2):
            self.kf.update([price1, price2])
        
        return self.kf.x[0]  # Hedge ratio
    
    def calculate_spread(self, stock1, stock2, hedge_ratio):
        return stock1 - (hedge_ratio * stock2)
```

### Strategy
1. Find correlated pairs (correlation > 0.8)
2. Calculate dynamic hedge ratio
3. Compute spread
4. Trade when spread > 2 std deviations

### Best For
- Market-neutral strategies
- Low correlation to market
- Professional traders

---

## 4. 🎯 Hidden Markov Model (HMM) Regime Detection

**File:** `worker/src/quant/hmm_regime.py`

### Theory
Markets have hidden states (BULL, BEAR, FLAT) that govern price movements.

### Implementation
```python
class HMMRegimeDetection:
    def __init__(self, n_states=3):
        self.model = hmm.GaussianHMM(
            n_components=n_states,
            covariance_type="full",
            n_iter=100
        )
    
    def detect_regime(self, returns):
        self.model.fit(returns.reshape(-1, 1))
        states = self.model.predict(returns.reshape(-1, 1))
        
        current_regime = states[-1]
        return self._map_regime(current_regime)
```

### Regimes
- **BULL:** Mean return > 0.5%, volatility moderate
- **BEAR:** Mean return < -0.5%, volatility high
- **FLAT:** Mean return ≈ 0%, volatility low

### Trading Rules
- **BULL regime:** Only long positions
- **BEAR regime:** Avoid or short
- **FLAT regime:** Mean reversion strategies

### Best For
- Regime-adaptive strategies
- Risk management
- Position sizing

---

## 5. 📊 Fama-French 3-Factor Model

**File:** `worker/src/quant/fama_french.py`

### Theory
Stock returns explained by 3 factors:
1. **Market Risk (Beta)**
2. **Size (SMB):** Small minus Big
3. **Value (HML):** High minus Low book-to-market

### Formula
```
R_stock = R_f + β₁(R_m - R_f) + β₂(SMB) + β₃(HML) + α
```

Where:
- `R_stock` = Stock return
- `R_f` = Risk-free rate
- `R_m` = Market return
- `SMB` = Small cap - Large cap returns
- `HML` = Value - Growth returns
- `α` = Excess return (alpha)

### Implementation
```python
def calculate_factor_loadings(stock_returns, market_returns):
    # Regression: R_s = α + β₁R_m + β₂SMB + β₃HML
    X = np.column_stack([market_returns, smb, hml])
    y = stock_returns
    
    beta = np.linalg.lstsq(X, y)[0]
    alpha = y.mean() - (beta @ X.mean(axis=0))
    
    return alpha, beta
```

### Signals
- **α > 0:** Outperforming (BUY)
- **α ≈ 0:** Fair value (HOLD)
- **α < 0:** Underperforming (SELL)

### Best For
- Fundamental quant analysis
- Long-term investing
- Portfolio construction

---

## 6. 🌊 Volume-Weighted Momentum

**Integrated in:** `worker/src/quant/momentum.py`

### Theory
Momentum is stronger when accompanied by high volume.

### Implementation
```python
def volume_weighted_momentum(data):
    price_change = data['Close'].pct_change()
    volume_ratio = data['Volume'] / data['Volume'].rolling(20).mean()
    
    # Weight momentum by volume
    vwm = (price_change * volume_ratio).rolling(20).sum()
    
    return np.clip(vwm, -1, 1)
```

### Interpretation
- High VWM + rising prices = Strong buy signal
- High VWM + falling prices = Strong sell signal
- Low VWM = Weak signal, ignore

### Best For
- Confirming momentum
- Avoiding false breakouts
- High volume stocks

---

## 🔧 Signal Fusion

All quant signals are combined using weighted averaging:

```python
def fuse_signals(signals, weights=None):
    if weights is None:
        weights = {
            'momentum': 0.30,
            'mean_reversion': 0.25,
            'regime': 0.20,
            'fama_french': 0.15,
            'pairs': 0.10
        }
    
    final_score = sum(
        signals[name] * weight 
        for name, weight in weights.items()
    )
    
    return np.clip(final_score, -1, 1)
```

---

## 📊 Performance Metrics

### Sharpe Ratio
```
Sharpe = (Return - Risk_Free_Rate) / Volatility
```

**Good:** > 1.0  
**Excellent:** > 2.0

### Maximum Drawdown
```
MDD = min(Peak - Trough) / Peak
```

**Acceptable:** < 20%  
**Concerning:** > 30%

### Win Rate
```
Win_Rate = Winning_Trades / Total_Trades
```

**Typical:** 50-60%  
**Good:** > 60%

---

## 🎯 Strategy Selection Guide

| Market Condition | Best Strategy |
|------------------|---------------|
| Strong uptrend | Momentum |
| Range-bound | Mean Reversion |
| High volatility | HMM Regime + Pairs |
| Bull market | Fama-French (value) |
| Uncertain | Combine all (fusion) |

---

## 📚 References

1. **Momentum:**
   - Jegadeesh & Titman (1993) - "Returns to Buying Winners"

2. **Mean Reversion:**
   - Poterba & Summers (1988) - "Mean Reversion in Stock Prices"

3. **Pairs Trading:**
   - Gatev et al. (2006) - "Pairs Trading: Performance of a Trading Strategy"

4. **HMM:**
   - Ang & Bekaert (2002) - "Regime Switches in Interest Rates"

5. **Fama-French:**
   - Fama & French (1993) - "Common Risk Factors"

---

## ⚙️ Customization

All strategies have configurable parameters in `worker/src/quant/<strategy>.py`:

```python
# Example: Momentum
MOMENTUM_WINDOW = 20  # days
MOMENTUM_THRESHOLD = 0.6  # for STRONG_BUY

# Example: Mean Reversion  
ZSCORE_WINDOW = 20  # days
ZSCORE_THRESHOLD = 2.0  # std deviations

# Example: HMM
HMM_STATES = 3  # BULL, BEAR, FLAT
HMM_ITERATIONS = 100
```

Adjust these based on:
- Your trading style (day/swing/position)
- Market conditions
- Backtesting results

---

**These are the same strategies used by hedge funds!** 💰📈
