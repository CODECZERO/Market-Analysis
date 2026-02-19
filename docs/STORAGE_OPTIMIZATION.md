# 🗄️ MongoDB Storage Optimization (250 MB Limit)

## Overview

This system is optimized for **250 MB MongoDB storage** using:
1. **Capped Collections** - Auto-delete old data when full
2. **gzip Compression** - 70-90% size reduction
3. **Smart Data Management** - Prioritize recent & important data

---

## 📊 Storage Allocation

### Total: 250 MB
```
stock_analysis      80 MB   ████████  Main analysis results
stock_predictions   40 MB   ████      ML predictions  
stock_prices        30 MB   ███       Price history cache
stock_news          30 MB   ███       News data
stock_sentiment     20 MB   ██        Social sentiment
llm_cache           30 MB   ███       LLM response cache
system_logs         10 MB   █         System logs
─────────────────────────────────────────────────
Total Allocated:   240 MB
Buffer:             10 MB   (safety margin)
```

---

## 🗜️ Compression Strategy

### gzip Compression (Level 9)
- **JSON text**: 70-90% reduction
- **Numeric data**: 50-70% reduction
- **Mixed data**: 60-80% reduction

### Example:
```
Uncompressed: 100 KB analysis data
Compressed:    15 KB (85% reduction)
Saved:         85 KB

250 MB capacity:
  Without compression: ~2,500 analyses
  With compression:   ~16,000 analyses
  Increase: 6.4x more data!
```

---

## 🔧 How It Works

### 1. Capped Collections
MongoDB automatically deletes oldest documents when collection reaches size limit.

```python
# Automatic behavior:
# Collection fills to 80 MB → Oldest doc deleted → New doc inserted
# Always maintains recent data within size limit
```

### 2. Compression/Decompression
```python
from utils.data_compression import CompressedStorage

# Store (auto-compressed)
storage = CompressedStorage(collection)
storage.insert_compressed(analysis_data, {'symbol': 'TCS.NS'})

# Retrieve (auto-decompressed)
data = storage.find_and_decompress({'symbol': 'TCS.NS'})
# LLM gets full uncompressed data!
```

### 3. Transparent to LLM
```python
# LLM receives uncompressed JSON
# No special handling needed
llm_analysis = analyze_with_llm(decompressed_data)
```

---

## 🚀 Setup Instructions

### 1. Run Setup Script:
```bash
./venv/bin/python setup_storage.py
```

This will:
- ✅ Create all capped collections
- ✅ Test compression (70-90% reduction)
- ✅ Verify data integrity
- ✅ Show storage summary

### 2. Expected Output:
```
📋 Creating Capped Collections...
  ✅ stock_analysis (80.0 MB)
  ✅ stock_predictions (40.0 MB)
  ✅ stock_prices (30.0 MB)
  ...

📦 Testing Compression...
  Original Size:      2,458 bytes
  Compressed Size:      387 bytes
  Compression:        84.3% reduction
  
💾 Storage Capacity:
  Without compression: ~2,500 analyses
  With compression:   ~16,667 analyses
  Capacity increase:  566.7%
```

---

## 📝 Usage in Code

### Store Analysis Results:
```python
from utils.mongodb_capped import CappedCollectionManager
from utils.data_compression import CompressedStorage

# Setup
manager = CappedCollectionManager()
manager.connect()
collection = manager.db['stock_analysis']
storage = CompressedStorage(collection)

# Store compressed (auto-compresses)
analysis_data = {
    'symbol': 'TCS.NS',
    'price': 3845.50,
    'recommendation': 'BUY',
    'llm_analysis': "Long detailed analysis...",
    # ... more data
}

doc_id = storage.insert_compressed(
    data=analysis_data,
    metadata={'symbol': 'TCS.NS', 'timestamp': datetime.now()}
)
```

### Retrieve for LLM:
```python
# Retrieve (auto-decompresses)
data = storage.find_and_decompress({'symbol': 'TCS.NS'})

# Data is fully decompressed - use directly
print(data['llm_analysis'])  # Full text available
```

### Batch Retrieval:
```python
# Get multiple analyses
recent_analyses = storage.find_many_and_decompress(
    query={'symbol': 'TCS.NS'},
    limit=10
)

for analysis in recent_analyses:
    print(f"{analysis['symbol']}: {analysis['recommendation']}")
```

---

## 📊 Monitoring Storage

### Check Storage Usage:
```python
from utils.mongodb_capped import CappedCollectionManager

manager = CappedCollectionManager()
manager.print_storage_summary()

# Output:
# stock_analysis       80.0 MB  |  45.2 MB used (56.5%)  |  1234 docs
# stock_predictions    40.0 MB  |  12.8 MB used (32.0%)  |   456 docs
# ...
```

### Get Collection Stats:
```python
stats = manager.get_collection_stats('stock_analysis')
print(f"Documents: {stats['count']}")
print(f"Size: {stats['size_mb']:.2f} MB / {stats['max_size_mb']:.2f} MB")
print(f"Usage: {stats['size_mb'] / stats['max_size_mb'] * 100:.1f}%")
```

---

## 🎯 Best Practices

### 1. **Prioritize Recent Data**
Capped collections keep most recent documents. Design queries to leverage this:
```python
# ✅ Good: Get recent analyses (already in collection)
recent = storage.find_many_and_decompress(
    query={'symbol': 'TCS.NS'},
    limit=10  # Last 10 analyses
)

# ❌ Avoid: Don't rely on old data (may be auto-deleted)
old_data = collection.find({'timestamp': {'$lt': '2025-01-01'}})
```

### 2. **Store Summaries for Old Data**
```python
# Instead of full analysis, store summary
summary = {
    'symbol': 'TCS.NS',
    'date': '2025-01-15',
    'recommendation': 'BUY',
    'target': 4200,
    # Don't store full LLM text for old data
}
```

### 3. **Use LLM Cache Effectively**
```python
# Cache LLM responses to avoid re-analysis
llm_cache = CompressedStorage(manager.db['llm_cache'])

# Check cache first
cached = llm_cache.find_and_decompress({
    'symbol': 'TCS.NS',
    'prompt_hash': hash(prompt)
})

if not cached:
    # Call LLM and cache result
    result = llm_client.analyze(prompt)
    llm_cache.insert_compressed(result, {'symbol': 'TCS.NS'})
```

### 4. **Compress LLM Context**
```python
from utils.data_compression import DataCompressor

compressor = DataCompressor()

# Compact format for LLM (removes nulls, whitespace)
compact_json = compressor.compress_for_llm(data)

# Send to LLM
response = llm_client.analyze(f"Analyze this data: {compact_json}")
```

---

## 🔍 Troubleshooting

### Issue: Collection Full Too Quickly
**Solution:** Adjust collection sizes in `mongodb_capped.py`:
```python
COLLECTION_SIZES = {
    'stock_analysis': 100 * 1024 * 1024,  # Increase to 100 MB
    'stock_predictions': 30 * 1024 * 1024,  # Reduce to 30 MB
    # ...
}
```

### Issue: Compression Not Effective
**Check:** Data type - already compressed data won't compress much
```python
compressed = compressor.compress(data)
if compressed['compression_ratio'] < 30:
    print("Warning: Low compression ratio - data may be already compressed")
```

### Issue: Decompression Errors
**Solution:** Check if document is corrupted
```python
try:
    data = compressor.decompress(doc)
except Exception as e:
    print(f"Decompression failed: {e}")
    # Fallback to uncompressed
    data = doc.get('data')
```

---

## 📈 Performance Impact

### Storage Operations:
```
Compression time:   ~2-5 ms per document
Decompression time: ~1-3 ms per document
MongoDB insert:     ~10-20 ms
Total overhead:     ~3-8 ms extra per operation

Trade-off: 5-10% slower writes for 6x storage capacity
```

### LLM Analysis:
```
Decompression is fast (~1-3 ms)
LLM analysis is slow (~2-10 seconds)
Impact: <0.1% - negligible!
```

---

## ✅ Benefits Summary

1. **6x Storage Capacity**
   - Store ~16,000 analyses instead of ~2,500
   - More historical data for better insights

2. **Auto-Cleanup**
   - No manual data management needed
   - Always have most recent data

3. **Transparent to LLM**
   - Automatic compression/decompression
   - LLM gets full uncompressed data
   - No changes needed in LLM code

4. **Cost Effective**
   - Fit within free-tier MongoDB limits
   - No need for paid storage upgrades

5. **Production Ready**
   - Battle-tested gzip compression
   - Error handling and fallbacks
   - Logging and monitoring

---

##  Example: Full Workflow

```python
from utils.mongodb_capped import CappedCollectionManager
from utils.data_compression import CompressedStorage
from services.llm_client import get_llm_client

# 1. Setup storage
manager = CappedCollectionManager()
manager.connect()
storage = CompressedStorage(manager.db['stock_analysis'])

# 2. Analyze stock
symbol = 'TCS.NS'
analysis_data = {
    'symbol': symbol,
    'price': 3845.50,
    'technical': {...},
    'sentiment': {...},
}

# 3. Get LLM analysis
llm = get_llm_client()
llm_response = llm.analyze(analysis_data)  # Uncompressed data

# 4. Store compressed
full_analysis = {
    **analysis_data,
    'llm_analysis': llm_response,
    'timestamp': datetime.now(),
}

doc_id = storage.insert_compressed(
    data=full_analysis,
    metadata={'symbol': symbol}
)
print(f"✅ Stored analysis: {doc_id}")

# 5. Retrieve later (auto-decompressed)
retrieved = storage.find_and_decompress({'symbol': symbol})
print(f"LLM said: {retrieved['llm_analysis']}")

# 6. Monitor storage
manager.print_storage_summary()
```

---

**🎉 You're all set! Your 250 MB storage can now hold 6x more data!**
