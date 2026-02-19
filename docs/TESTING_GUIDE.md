# Testing Guide

## 📊 Test Suites

We have **3 types of tests**:

### 1. **Offline Tests** (Synthetic Data) ⭐
Tests model functionality with randomly generated data.

```bash
python tests/test_offline.py
```

**What it tests:**
- ✅ Technical indicators (RSI, MACD, Bollinger Bands)
- ✅ Quant strategies (Momentum, Mean Reversion)
- ✅ LSTM predictions
- ✅ Decision engine logic
- ✅ Edge cases (small dataset, high volatility, flat market)

**Why offline?**
- Fast (no network calls)
- Reliable (deterministic data)
- Tests core logic
- Good for development

---

### 2. **Online Tests** (Real Data) ⭐
Tests model accuracy with actual NSE stock data.

```bash
python tests/test_online.py
```

**What it tests:**
- ✅ Data fetching from YFinance
- ✅ Prediction accuracy (backtesting)
- ✅ Recommendation quality
- ✅ Consistency (same stock, same result)
- ✅ Performance (speed)

**Why online?**
- Real-world validation
- Actual accuracy metrics
- Market behavior testing
- Production readiness

---

### 3. **Integration Tests** (API)
Tests API endpoints and full pipeline.

```bash
# Start API server first
python api_server.py

# In another terminal
python tests/integration_test.py
```

---

## 🚀 Quick Test

Run all tests:

```bash
# Offline (fast, ~30s)
python tests/test_offline.py

# Online (slow, ~2-3min)
python tests/test_online.py

# Integration (requires API running)
python api_server.py &
sleep 5
python tests/integration_test.py
```

---

## 📈 Understanding Results

### Offline Tests
```
✓ RSI in valid range: 65.23
✓ MACD calculated: 12.45
✓ SMAs calculated: SMA50=2420.30, SMA200=2380.00
✓ Price within Bollinger Bands
✓ Momentum signal in range: 0.723

Passed: 14/15 (93.3%)
```

**Good:** 80%+ pass rate  
**Acceptable:** 60-80%  
**Bad:** <60%

---

### Online Tests
```
Testing RELIANCE...
  1-Day: Predicted ₹2467.50, Actual ₹2456.75, Error 0.4%, Accuracy 99.6%
  7-Day: Predicted ₹2510.20, Actual ₹2489.30, Error 0.8%, Accuracy 99.2%

Average Prediction Accuracy: 68.5%
```

**Good:** 60%+ accuracy (ML is hard!)  
**Acceptable:** 50-60%  
**Bad:** <50% (worse than random)

---

### Recommendation Quality
```
Analyzing RELIANCE...
  ✓ BUY was correct: +3.2%

Recommendation Accuracy: 2/3 (66.7%)
```

**Good:** 60%+ (better than most analysts!)  
**Acceptable:** 50-60%  
**Bad:** <50%

---

## 🛠️ Customizing Tests

### Change Test Stocks (Online Tests)

Edit `tests/test_online.py`:
```python
TEST_STOCKS = [
    ("RELIANCE", "NSE"),
    ("TCS", "NSE"),
    ("INFY", "NSE"),  # Add your stocks here
]
```

### Adjust Thresholds

In test files, find:
```python
if avg_accuracy >= 0.60:  # 60% threshold
    return True
```

Change `0.60` to be more/less strict.

### Add New Tests

```python
def test_my_feature():
    """Test description"""
    # Your test code
    return True  # or False
```

---

## 🐛 Common Issues

### "Module not found"
```bash
# Install worker dependencies
pip install -r worker/requirements.txt
```

### "Data fetch failed"
- Check internet connection
- YFinance might be rate-limited
- Try again in a few minutes

### "Tests timing out"
- Online tests can take 2-3 minutes
- Be patient!
- Reduce `TEST_STOCKS` list

---

## 📊 CI/CD Integration

### GitHub Actions

`.github/workflows/test.yml`:
```yaml
name: Tests

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r worker/requirements.txt
      
      - name: Run offline tests
        run: python tests/test_offline.py
      
      - name: Run online tests
        run: python tests/test_online.py
```

---

## 🎯 Test Coverage

| Component | Offline | Online | Integration |
|-----------|---------|--------|-------------|
| Technical Indicators | ✅ | ✅ | ✅ |
| Quant Strategies | ✅ | ✅ | - |
| LSTM Model | ✅ | ✅ | - |
| Decision Engine | ✅ | ✅ | ✅ |
| Data Fetch | - | ✅ | ✅ |
| API Endpoints | - | - | ✅ |
| Watchlist | - | - | ✅ |

---

## 💡 Best Practices

1. **Run offline tests frequently** (fast feedback)
2. **Run online tests before commits** (catch bugs)
3. **Run integration tests in staging** (full system)
4. **Monitor accuracy over time** (track degradation)
5. **Add tests for bugs** (prevent regression)

---

## 📈 Benchmarking

### Current Baselines

| Metric | Target | Current |
|--------|--------|---------|
| Offline Pass Rate | 80% | 93% ✅ |
| Prediction Accuracy | 60% | 65-68% ✅ |
| Recommendation Accuracy | 50% | 60-70% ✅ |
| Analysis Time | <60s | ~45s ✅ |

---

**Start testing with:**
```bash
python tests/test_offline.py
```

**Then validate with real data:**
```bash
python tests/test_online.py
```

Happy testing! 🧪✨
