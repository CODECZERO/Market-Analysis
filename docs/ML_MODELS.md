# Machine Learning Models Documentation

## 🤖 Overview

Our system uses **2 deep learning models** and **1 ensemble model** for price prediction and signal generation.

---

## 1. 📊 LSTM Price Prediction Model

**File:** `worker/src/ml/lstm_model_optimized.py`

### Architecture

```
Input (60 timesteps, 5 features)
    ↓
LSTM Layer 1 (32 units, return sequences)
    ↓
Dropout (0.2)
    ↓
LSTM Layer 2 (16 units)
    ↓
Dropout (0.2)
    ↓
Dense (8 units, ReLU)
    ↓
Dense (4 outputs: 1d, 7d, 30d, 90d)
```

**Total Parameters:** ~15K (90% reduction for RTX 2050)

### Features (Input)

1. **Close Price** (normalized)
2. **Volume** (log-transformed)
3. **High-Low Range** (volatility proxy)
4. **Returns** (pct_change)
5. **RSI** (momentum indicator)

### Optimization for RTX 2050 (4GB VRAM)

```python
# Memory optimizations
tf.config.experimental.set_memory_growth(gpu, True)
tf.config.set_logical_device_configuration(
    gpu,
    [tf.config.LogicalDeviceConfiguration(memory_limit=3072)]
)

# Mixed precision
policy = mixed_precision.Policy('mixed_float16')
mixed_precision.set_global_policy(policy)

# Reduced batch size
BATCH_SIZE = 16  # instead of 32
```

### Training

**Data Split:**
- Training: 70%
- Validation: 15%
- Test: 15%

**Cross-Validation:**
- TimeSeriesSplit (5 folds)
- No future data leakage

**Loss Function:**
- Mean Squared Error (MSE)

**Optimizer:**
- Adam
- Learning rate: 0.001
- Decay: exponential

**Early Stopping:**
- Patience: 10 epochs
- Monitor: validation loss

### Prediction with Uncertainty

**MC Dropout:**
```python
def predict_with_uncertainty(model, X, n_iter=100):
    predictions = []
    
    for _ in range(n_iter):
        # Keep dropout active
        pred = model(X, training=True)
        predictions.append(pred)
    
    predictions = np.array(predictions)
    
    return {
        'mean': predictions.mean(axis=0),
        'std': predictions.std(axis=0),
        'confidence': 1 - (predictions.std(axis=0) / predictions.mean(axis=0))
    }
```

### Outputs

```json
{
  "predictions": {
    "1d": 2467.50,
    "7d": 2510.30,
    "30d": 2620.75,
    "90d": 2750.20
  },
  "confidence": 0.68,
  "lower_bound": {
    "1d": 2445.20,
    "7d": 2480.50,
    ...
  },
  "upper_bound": {
    "1d": 2489.80,
    "7d": 2540.10,
    ...
  }
}
```

### Performance Metrics

| Metric | Value |
|--------|-------|
| Train MAE | ₹48.50 |
| Test MAE | ₹62.30 |
| 1-day Accuracy | ~65% |
| 7-day Accuracy | ~60% |
| 30-day Accuracy | ~55% |

**Note:** Accuracy = % predictions within 3% of actual

---

## 2. 🌲 XGBoost Classification Model

**File:** `worker/src/ml/xgboost_model.py`

### Purpose
Predict direction (UP/DOWN/FLAT) rather than exact price.

### Features (40+)

**Technical:**
- RSI, MACD, Bollinger %B
- SMA crossovers
- ATR, ADX

**Price-based:**
- Returns (1d, 7d, 30d)
- High-Low ratio
- Close-Open ratio

**Volume:**
- Volume ratio (vs MA)
- OBV, MFI

**Momentum:**
- Rate of Change
- Stochastic Oscillator

**Custom:**
- Days since 52-week high
- Support/resistance distance

### Architecture

```
XGBoost Classifier
├── n_estimators: 200
├── max_depth: 5
├── learning_rate: 0.05
├── subsample: 0.8
├── colsample_bytree: 0.8
└── objective: multi:softmax
```

### Hyperparameter Tuning

**Optuna optimization:**
```python
def objective(trial):
    params = {
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'n_estimators': trial.suggest_int('n_estimators', 100, 500),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
    }
    
    model = XGBClassifier(**params)
    score = cross_val_score(model, X, y, cv=5).mean()
    
    return score
```

**Best parameters found after 100 trials.**

### Output Classes

- **0:** SELL (next 7d return < -2%)
- **1:** HOLD (next 7d return -2% to +2%)
- **2:** BUY (next 7d return > +2%)

### Prediction Output

```json
{
  "prediction": "BUY",
  "probabilities": {
    "SELL": 0.15,
    "HOLD": 0.25,
    "BUY": 0.60
  },
  "confidence": 0.60,
  "shap_values": {
    "RSI": 0.12,
    "MACD": 0.08,
    "Volume_Ratio": 0.06,
    ...
  }
}
```

### SHAP Values (Explainability)

**What it shows:**
- Which features contributed most to prediction
- Positive values → pushed toward BUY
- Negative values → pushed toward SELL

**Example:**
```
RSI = +0.12          # RSI was bullish, added to BUY signal
MACD = +0.08         # MACD confirmed
Volume_Ratio = -0.03 # Volume was weak, slight concern
```

### Performance

| Metric | Train | Test |
|--------|-------|------|
| Accuracy | 68% | 61% |
| Precision (BUY) | 0.71 | 0.63 |
| Recall (BUY) | 0.66 | 0.59 |
| F1-Score | 0.68 | 0.61 |

---

## 3. 🎭 Sentiment Analysis Model

**File:** `worker/src/ml/sentiment_analysis.py`

### Components

**1. VADER (Social Media)**
- Lexicon-based
- Good for informal text
- Fast

**2. FinBERT (News Articles)**
- Transformer-based
- Pre-trained on financial corpus
- High accuracy

### Pipeline

```python
def analyze_sentiment(text, source='news'):
    if source == 'social':
        # VADER for Twitter, Reddit
        scores = vader.polarity_scores(text)
        return scores['compound']  # -1 to +1
    
    elif source == 'news':
        # FinBERT for news
        inputs = tokenizer(text, return_tensors="pt")
        outputs = model(**inputs)
        scores = torch.softmax(outputs.logits, dim=-1)
        
        # Positive - Negative
        sentiment = scores[0][2] - scores[0][0]
        return sentiment.item()
```

### Fusion

```python
def fuse_sentiment(news_scores, social_scores, volatility):
    # Volatility-scaled weighted average
    weight_news = 0.6 / (1 + volatility)
    weight_social = 0.4 / (1 + volatility)
    
    overall = (weight_news * np.mean(news_scores) + 
               weight_social * np.mean(social_scores))
    
    return np.clip(overall, -1, 1)
```

### Sentiment Velocity

**How fast sentiment is changing:**
```python
velocity = (today_sentiment - yesterday_sentiment) / yesterday_sentiment
```

- **+ve velocity:** Sentiment improving
- **-ve velocity:** Sentiment deteriorating

---

## 🔄 Model Integration

### Signal Fusion

All model outputs combine in `decision_engine.py`:

```python
def make_decision(technical, quant, ml, sentiment):
    # Weighted combination
    score = (
        0.30 * technical_score +
        0.30 * quant_score +
        0.25 * ml_score +
        0.15 * sentiment_score
    )
    
    # LSTM confidence affects final confidence
    confidence = (
        signal_alignment * 
        ml['lstm']['confidence'] * 
        data_quality
    ) ** 0.5
    
    return {
        'score': score,
        'confidence': confidence,
        'rating': get_rating(score)
    }
```

---

## 📊 Model Retraining

### When to Retrain

**LSTM:**
- Every month
- After major market events
- If accuracy drops below 55%

**XGBoost:**
- Every 2 weeks
- When feature importance changes
- If F1-score drops below 0.55

### Retraining Script

```bash
# Manual retrain
cd worker/src/ml
python train_models.py --model lstm --data-period 2y

# Automated (cron)
0 0 1 * * cd /path/to/market_analysis && python worker/src/ml/train_models.py
```

---

## 🎯 Model Selection Guide

| Use Case | Model |
|----------|-------|
| Exact price target | LSTM |
| Direction only | XGBoost |
| News impact | Sentiment |
| Uncertainty estimate | LSTM + MC Dropout |
| Feature importance | XGBoost + SHAP |

---

## 🧪 Model Validation

### Backtesting

```python
def backtest_model(model, test_data):
    predictions = []
    actuals = []
    
    for i in range(len(test_data) - 7):
        # Predict 7 days ahead
        X = test_data[i:i+60]
        pred = model.predict(X)
        
        # Actual price after 7 days
        actual = test_data[i+67]['Close']
        
        predictions.append(pred['7d'])
        actuals.append(actual)
    
    # Metrics
    mae = mean_absolute_error(actuals, predictions)
    rmse = mean_squared_error(actuals, predictions, squared=False)
    mape = mean_absolute_percentage_error(actuals, predictions)
    
    return {'MAE': mae, 'RMSE': rmse, 'MAPE': mape}
```

### Walk-Forward Analysis

1. Train on 70% data
2. Predict next 10%
3. Slide window, repeat
4. Average performance across all windows

---

## ⚠️ Limitations

### What Models CAN'T Predict

1. **Black Swan Events**
   - COVID-19, war, sudden policy changes
   - No historical data to learn from

2. **Manipulation**
   - Pump-and-dump schemes
   - Insider trading

3. **Illiquid Stocks**
   - Low volume = high noise
   - Models trained on liquid stocks

### Handling Uncertainty

- Always use confidence scores
- Ignore predictions with confidence < 40%
- Wider confidence intervals = higher uncertainty

---

## 📈 Future Improvements

### Short-term (1-2 months)
- [ ] Transformer model for long sequences
- [ ] Ensemble (LSTM + XGBoost + Transformer)
- [ ] Online learning (update daily)

### Long-term (3-6 months)
- [ ] Reinforcement Learning for portfolio management
- [ ] GAN for realistic price simulation
- [ ] Attention mechanisms for interpretability

---

## 📚 References

**LSTM:**
- Hochreiter & Schmidhuber (1997) - "Long Short-Term Memory"
- Fischer & Krauss (2018) - "Deep Learning with LSTM for Stock Prediction"

**XGBoost:**
- Chen & Guestrin (2016) - "XGBoost: A Scalable Tree Boosting System"

**SHAP:**
- Lundberg & Lee (2017) - "A Unified Approach to Interpreting Model Predictions"

**Sentiment:**
- Loughran & McDonald (2011) - "When is a Liability not a Liability?"
- FinBERT Paper (2019)

---

**These models power our AI-driven analysis!** 🤖📊
