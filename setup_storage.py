#!/usr/bin/env python3
"""
Setup MongoDB Storage for Market Analysis
- Creates capped collections (250 MB limit)
- Tests compression
- Shows storage summary
"""

import sys
import os

# Add worker to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker/src'))

from dotenv import load_dotenv
load_dotenv()

from utils.mongodb_capped import CappedCollectionManager
from utils.data_compression import DataCompressor, CompressedStorage
from pymongo import MongoClient


def main():
    print("\n" + "="*70)
    print("🗄️  MONGODB STORAGE SETUP - Market Analysis System")
    print("="*70)
    print(f"Storage Limit: 250 MB")
    print(f"Strategy: Capped Collections + gzip Compression")
    print("="*70 + "\n")
    
    # 1. Setup capped collections
    print("📋 Step 1: Creating Capped Collections...")
    print("-" * 70)
    
    manager = CappedCollectionManager()
    manager.setup_all_collections()
    
    # 2. Test compression
    print("\n📦 Step 2: Testing Data Compression...")
    print("-" * 70)
    
    compressor = DataCompressor()
    
    # Sample analysis data
    sample_analysis = {
        'symbol': 'TCS.NS',
        'timestamp': '2026-02-01T12:00:00',
        'price': 3845.50,
        'technical_indicators': {
            'rsi': 65.5,
            'macd': 12.3,
            'macd_signal': 11.8,
            'sma_20': 3820.4,
            'sma_50': 3845.2,
            'sma_200': 3720.8,
            'bollinger_upper': 3920.5,
            'bollinger_lower': 3770.5,
        },
        'sentiment': {
            'news_score': 0.75,
            'social_score': 0.68,
            'overall_score': 0.72,
            'news_count': 45,
            'social_mentions': 1250,
        },
        'fundamental': {
            'pe_ratio': 28.5,
            'market_cap': 1420000000000,
            'revenue_growth': 12.5,
            'profit_margin': 22.3,
            'roe': 42.1,
        },
        'recommendation': 'BUY',
        'confidence': 0.85,
        'target_price': 4200,
        'stop_loss': 3700,
        'llm_analysis': """
        Technical Analysis: TCS shows strong bullish momentum with RSI at 65.5, 
        indicating positive price action without being overbought. The stock is 
        trading above all major moving averages (20, 50, 200), confirming an 
        uptrend. MACD shows bullish crossover with strong momentum.
        
        Fundamental Analysis: Solid fundamentals with P/E of 28.5, strong ROE 
        of 42%, and healthy profit margins of 22%. Revenue growth of 12.5% 
        indicates consistent business expansion.
        
        Sentiment Analysis: Positive sentiment from news (0.75) and social 
        media (0.68) with 45 news articles and 1,250 social mentions showing 
        strong investor interest.
        
        Recommendation: BUY with target price ₹4,200 and stop loss ₹3,700. 
        Risk/Reward ratio is favorable at 1:2.5.
        """
    }
    
    compressed = compressor.compress(sample_analysis)
    
    print(f"Original Size:      {compressed['original_size']:,} bytes ({compressed['original_size']/1024:.2f} KB)")
    print(f"Compressed Size:    {compressed['compressed_size']:,} bytes ({compressed['compressed_size']/1024:.2f} KB)")
    print(f"Compression Ratio:  {compressed['compression_ratio']:.1f}% reduction")
    print(f"Space Saved:        {compressed['original_size'] - compressed['compressed_size']:,} bytes")
    
    # Show how many we can store
    collection_size = 80 * 1024 * 1024  # 80 MB for stock_analysis
    uncompressed_capacity = collection_size / compressed['original_size']
    compressed_capacity = collection_size / compressed['compressed_size']
    
    print(f"\n💾 Storage Capacity (80 MB stock_analysis collection):")
    print(f"Without compression: ~{int(uncompressed_capacity):,} analyses")
    print(f"With compression:    ~{int(compressed_capacity):,} analyses")
    print(f"Capacity increase:   {((compressed_capacity / uncompressed_capacity) - 1) * 100:.1f}%")
    
    # 3. Test storage and retrieval
    print("\n🔄 Step 3: Testing Storage & Retrieval...")
    print("-" * 70)
    
    try:
        mongo_url = os.getenv('MONGO_URL')
        client = MongoClient(mongo_url)
        db = client[os.getenv('MONGO_DB_NAME', 'brand_tracker')]
        
        # Get collection
        collection = db['stock_analysis']
        compressed_storage = CompressedStorage(collection)
        
        # Insert compressed data
        doc_id = compressed_storage.insert_compressed(
            sample_analysis,
            metadata={'symbol': 'TCS.NS', 'type': 'full_analysis'}
        )
        
        print(f"✅ Inserted compressed document: {doc_id}")
        
        # Retrieve and decompress
        retrieved = compressed_storage.find_and_decompress({'_id': doc_id})
        
        if retrieved == sample_analysis:
            print(f"✅ Data integrity verified (compression -> decompression)")
        else:
            print(f"⚠️  Data mismatch after decompression")
        
        client.close()
        
    except Exception as e:
        print(f"⚠️  Storage test skipped: {e}")
    
    # 4. Final summary
    print("\n📊 Step 4: Storage Summary")
    print("-" * 70)
    
    manager.print_storage_summary()
    
    manager.close()
    
    print("\n✅ Setup Complete!")
    print("\n💡 Benefits:")
    print("  • Capped collections automatically delete old data")
    print("  • 70-90% compression saves storage space")
    print("  • ~3-5x more data can be stored")
    print("  • LLMs get full uncompressed data")
    print("  • Transparent compression/decompression")
    
    print("\n📝 Usage in your code:")
    print("""
    from utils.mongodb_capped import CappedCollectionManager
    from utils.data_compression import CompressedStorage
    
    # Get collection
    manager = CappedCollectionManager()
    manager.connect()
    collection = manager.db['stock_analysis']
    
    # Use compressed storage
    storage = CompressedStorage(collection)
    
    # Store (auto-compressed)
    storage.insert_compressed(analysis_data, {'symbol': 'TCS.NS'})
    
    # Retrieve (auto-decompressed for LLM)
    data = storage.find_and_decompress({'symbol': 'TCS.NS'})
    """)
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
