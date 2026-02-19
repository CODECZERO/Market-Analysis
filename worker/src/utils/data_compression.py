"""
Data Compression Utilities
Compress JSON data before storing in MongoDB
Decompress when retrieving for LLM analysis

Uses gzip compression for 70-90% size reduction
"""

import gzip
import json
import base64
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataCompressor:
    """
    Compress/decompress JSON data for storage
    
    Typical compression ratios:
    - JSON text data: 70-90% reduction
    - Numeric data: 50-70% reduction
    - Mixed data: 60-80% reduction
    
    Example:
        100 KB uncompressed -> 15-30 KB compressed
    """
    
    @staticmethod
    def compress(data: Any) -> Dict[str, Any]:
        """
        Compress data and encode as base64
        
        Args:
            data: Any JSON-serializable data (dict, list, etc.)
        
        Returns:
            Dict with compressed data and metadata:
            {
                'compressed': True,
                'data': '<base64-encoded-gzip>',
                'original_size': <bytes>,
                'compressed_size': <bytes>,
                'compression_ratio': <percentage>
            }
        """
        try:
            # Convert to JSON string
            json_str = json.dumps(data, separators=(',', ':'))  # No whitespace
            original_bytes = json_str.encode('utf-8')
            original_size = len(original_bytes)
            
            # Compress with gzip (level 9 = maximum compression)
            compressed_bytes = gzip.compress(original_bytes, compresslevel=9)
            compressed_size = len(compressed_bytes)
            
            # Encode as base64 for MongoDB storage
            base64_data = base64.b64encode(compressed_bytes).decode('utf-8')
            
            # Calculate compression ratio
            ratio = (1 - compressed_size / original_size) * 100
            
            logger.debug(f"Compressed {original_size} -> {compressed_size} bytes ({ratio:.1f}% reduction)")
            
            return {
                'compressed': True,
                'data': base64_data,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': round(ratio, 2),
            }
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            # Fallback: return uncompressed
            return {
                'compressed': False,
                'data': data,
                'error': str(e)
            }
    
    @staticmethod
    def decompress(compressed_doc: Dict[str, Any]) -> Any:
        """
        Decompress data from MongoDB document
        
        Args:
            compressed_doc: Document from MongoDB with compressed data
        
        Returns:
            Original decompressed data
        """
        try:
            # Check if data is compressed
            if not compressed_doc.get('compressed'):
                # Return as-is if not compressed
                return compressed_doc.get('data')
            
            # Decode base64
            base64_data = compressed_doc['data']
            compressed_bytes = base64.b64decode(base64_data)
            
            # Decompress
            original_bytes = gzip.decompress(compressed_bytes)
            json_str = original_bytes.decode('utf-8')
            
            # Parse JSON
            data = json.loads(json_str)
            
            logger.debug(f"Decompressed {compressed_doc.get('compressed_size')} -> {compressed_doc.get('original_size')} bytes")
            
            return data
            
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            # Return as-is if decompression fails
            return compressed_doc.get('data')
    
    @staticmethod
    def compress_for_llm(data: Any) -> str:
        """
        Compress data into a compact string for LLM context
        
        This removes whitespace and uses shorter keys
        
        Args:
            data: Dict or list to compress
        
        Returns:
            Compact JSON string
        """
        # Use compact JSON (no whitespace)
        json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        
        # Additional optimizations for LLM context
        # (Remove None values, empty strings, etc.)
        data_clean = DataCompressor._clean_for_llm(data)
        json_str_clean = json.dumps(data_clean, separators=(',', ':'), ensure_ascii=False)
        
        return json_str_clean
    
    @staticmethod
    def _clean_for_llm(data: Any) -> Any:
        """Remove null/empty values to reduce token count"""
        if isinstance(data, dict):
            return {
                k: DataCompressor._clean_for_llm(v)
                for k, v in data.items()
                if v is not None and v != '' and v != [] and v != {}
            }
        elif isinstance(data, list):
            return [
                DataCompressor._clean_for_llm(item)
                for item in data
                if item is not None and item != '' and item != [] and item != {}
            ]
        else:
            return data


class CompressedStorage:
    """
    Wrapper for MongoDB operations with automatic compression
    """
    
    def __init__(self, collection):
        """
        Args:
            collection: PyMongo collection object
        """
        self.collection = collection
        self.compressor = DataCompressor()
    
    def insert_compressed(self, data: Any, metadata: Dict = None) -> str:
        """
        Compress and insert data into MongoDB
        
        Args:
            data: Data to store (will be compressed)
            metadata: Additional metadata (not compressed)
        
        Returns:
            Inserted document ID
        """
        compressed_doc = self.compressor.compress(data)
        
        # Add metadata
        if metadata:
            compressed_doc.update(metadata)
        
        # Insert
        result = self.collection.insert_one(compressed_doc)
        
        logger.info(f"Stored compressed doc: {compressed_doc['original_size']} -> {compressed_doc['compressed_size']} bytes ({compressed_doc['compression_ratio']:.1f}% saved)")
        
        return str(result.inserted_id)
    
    def find_and_decompress(self, query: Dict) -> Optional[Any]:
        """
        Find document and decompress data
        
        Args:
            query: MongoDB query
        
        Returns:
            Decompressed data or None
        """
        doc = self.collection.find_one(query)
        
        if not doc:
            return None
        
        return self.compressor.decompress(doc)
    
    def find_many_and_decompress(self, query: Dict, limit: int = 100) -> list:
        """
        Find multiple documents and decompress
        
        Args:
            query: MongoDB query
            limit: Maximum results
        
        Returns:
            List of decompressed data
        """
        docs = self.collection.find(query).limit(limit)
        
        results = []
        for doc in docs:
            try:
                decompressed = self.compressor.decompress(doc)
                results.append(decompressed)
            except Exception as e:
                logger.error(f"Failed to decompress doc: {e}")
                continue
        
        return results


# Test/Demo
if __name__ == "__main__":
    # Example data
    sample_data = {
        'symbol': 'TCS.NS',
        'analysis': {
            'technical': {
                'rsi': 65.5,
                'macd': 12.3,
                'sma_50': 3845.2,
                'sma_200': 3720.8,
            },
            'sentiment': {
                'news': 0.75,
                'social': 0.68,
                'overall': 0.72,
            },
            'recommendation': 'Buy',
            'confidence': 0.85,
            'target': 4200,
            'stop_loss': 3700,
        },
        'llm_analysis': "TCS shows strong technical indicators with RSI at 65.5 indicating bullish momentum. The stock is trading above both 50-day and 200-day moving averages, suggesting a positive long-term trend. Sentiment analysis from news and social media shows positive outlook. Based on fundamental and technical analysis, recommending BUY with target price of ₹4,200.",
    }
    
    compressor = DataCompressor()
    
    print("="*60)
    print("DATA COMPRESSION DEMO")
    print("="*60)
    
    # Compress
    compressed = compressor.compress(sample_data)
    
    print(f"\nOriginal Size:    {compressed['original_size']:,} bytes")
    print(f"Compressed Size:  {compressed['compressed_size']:,} bytes")
    print(f"Compression:      {compressed['compression_ratio']:.1f}% reduction")
    print(f"Space Saved:      {compressed['original_size'] - compressed['compressed_size']:,} bytes")
    
    # Decompress
    decompressed = compressor.decompress(compressed)
    
    print(f"\n✅ Decompression successful: {decompressed == sample_data}")
    
    # LLM-optimized format
    llm_format = compressor.compress_for_llm(sample_data)
    print(f"\nLLM-optimized string length: {len(llm_format)} chars")
    print(f"Original JSON length: {len(json.dumps(sample_data))} chars")
    print(f"Savings for LLM: {(1 - len(llm_format) / len(json.dumps(sample_data))) * 100:.1f}%")
    
    print("="*60)
