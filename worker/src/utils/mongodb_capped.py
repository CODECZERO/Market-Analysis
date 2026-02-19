"""
MongoDB Capped Collections Manager
Optimized for 250MB total storage limit
Uses capped collections with automatic rotation
"""

import os
from pymongo import MongoClient
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CappedCollectionManager:
    """
    Manage MongoDB capped collections for limited storage (250MB total)
    
    Capped collections automatically delete old documents when size limit reached
    """
    
    # Storage allocation (total: 250MB)
    COLLECTION_SIZES = {
        'stock_analysis': 80 * 1024 * 1024,      # 80 MB - Main analysis results
        'stock_predictions': 40 * 1024 * 1024,    # 40 MB - ML predictions
        'stock_prices': 30 * 1024 * 1024,         # 30 MB - Price history cache
        'stock_news': 30 * 1024 * 1024,           # 30 MB - News data
        'stock_sentiment': 20 * 1024 * 1024,      # 20 MB - Social sentiment
        'llm_cache': 30 * 1024 * 1024,            # 30 MB - LLM response cache
        'system_logs': 10 * 1024 * 1024,          # 10 MB - System logs
        # Total: 240 MB (10 MB buffer)
    }
    
    def __init__(self, mongo_url: str = None, db_name: str = None):
        """Initialize with MongoDB connection"""
        self.mongo_url = mongo_url or os.getenv('MONGO_URL')
        self.db_name = db_name or os.getenv('MONGO_DB_NAME', 'brand_tracker')
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB"""
        if not self.client:
            self.client = MongoClient(self.mongo_url)
            self.db = self.client[self.db_name]
            logger.info(f"Connected to MongoDB: {self.db_name}")
    
    def create_capped_collection(self, name: str, size_bytes: int = None, max_documents: int = None):
        """
        Create a capped collection
        
        Args:
            name: Collection name
            size_bytes: Maximum size in bytes
            max_documents: Maximum number of documents (optional)
        
        Returns:
            Collection object
        """
        self.connect()
        
        # Use predefined size or custom
        size = size_bytes or self.COLLECTION_SIZES.get(name, 10 * 1024 * 1024)
        
        try:
            # Check if collection exists
            if name in self.db.list_collection_names():
                # Check if it's capped
                stats = self.db.command('collStats', name)
                if stats.get('capped'):
                    logger.info(f"Capped collection '{name}' already exists")
                    return self.db[name]
                else:
                    # Drop non-capped collection and recreate
                    logger.warning(f"Converting '{name}' to capped collection")
                    self.db[name].drop()
            
            # Create capped collection
            options = {
                'capped': True,
                'size': size,
            }
            
            if max_documents:
                options['max'] = max_documents
            
            self.db.create_collection(name, **options)
            logger.info(f"Created capped collection '{name}' ({size / 1024 / 1024:.1f} MB)")
            
            return self.db[name]
            
        except Exception as e:
            logger.error(f"Error creating capped collection '{name}': {e}")
            # Return regular collection as fallback
            return self.db[name]
    
    def setup_all_collections(self):
        """Create all predefined capped collections"""
        self.connect()
        
        logger.info("Setting up capped collections...")
        
        for name, size in self.COLLECTION_SIZES.items():
            self.create_capped_collection(name, size)
        
        logger.info("✅ All capped collections created")
        
        # Print storage summary
        self.print_storage_summary()
    
    def print_storage_summary(self):
        """Print storage allocation summary"""
        self.connect()
        
        print("\n" + "="*60)
        print("📊 MONGODB STORAGE ALLOCATION (250 MB Total)")
        print("="*60)
        
        total_allocated = 0
        
        for name, size in self.COLLECTION_SIZES.items():
            size_mb = size / 1024 / 1024
            total_allocated += size
            
            # Get actual usage if collection exists
            try:
                if name in self.db.list_collection_names():
                    stats = self.db.command('collStats', name)
                    used_bytes = stats.get('size', 0)
                    used_mb = used_bytes / 1024 / 1024
                    used_pct = (used_bytes / size * 100) if size > 0 else 0
                    doc_count = stats.get('count', 0)
                    
                    print(f"{name:25} {size_mb:6.1f} MB  |  {used_mb:6.2f} MB used ({used_pct:5.1f}%)  |  {doc_count:6} docs")
                else:
                    print(f"{name:25} {size_mb:6.1f} MB  |  Not created yet")
            except Exception as e:
                print(f"{name:25} {size_mb:6.1f} MB  |  Error: {e}")
        
        print("="*60)
        print(f"Total Allocated: {total_allocated / 1024 / 1024:.1f} MB / 250 MB")
        print(f"Buffer Remaining: {(250 * 1024 * 1024 - total_allocated) / 1024 / 1024:.1f} MB")
        print("="*60 + "\n")
    
    def get_collection_stats(self, name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        self.connect()
        
        try:
            stats = self.db.command('collStats', name)
            return {
                'name': name,
                'count': stats.get('count', 0),
                'size_bytes': stats.get('size', 0),
                'size_mb': stats.get('size', 0) / 1024 / 1024,
                'storage_bytes': stats.get('storageSize', 0),
                'storage_mb': stats.get('storageSize', 0) / 1024 / 1024,
                'max_size_bytes': stats.get('maxSize', 0),
                'max_size_mb': stats.get('maxSize', 0) / 1024 / 1024,
                'capped': stats.get('capped', False),
            }
        except Exception as e:
            logger.error(f"Error getting stats for '{name}': {e}")
            return {}
    
    def cleanup_old_data(self):
        """
        Manual cleanup for non-capped collections
        (Capped collections auto-cleanup, but this is for safety)
        """
        self.connect()
        
        logger.info("Running manual cleanup...")
        
        # This is automatic for capped collections
        # But we can log the status
        for name in self.COLLECTION_SIZES.keys():
            stats = self.get_collection_stats(name)
            if stats:
                usage_pct = (stats['size_bytes'] / stats.get('max_size_bytes', 1)) * 100 if stats.get('max_size_bytes') else 0
                logger.info(f"{name}: {stats['count']} docs, {stats['size_mb']:.2f} MB ({usage_pct:.1f}% full)")
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# CLI usage
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    
    from dotenv import load_dotenv
    load_dotenv()
    
    manager = CappedCollectionManager()
    
    # Setup all collections
    manager.setup_all_collections()
    
    # Print summary
    manager.print_storage_summary()
    
    manager.close()
