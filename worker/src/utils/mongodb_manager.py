"""
MongoDB Manager
Handles all database operations for stock analysis
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import os

# Use centralized logger
try:
    from system_logger import get_logger, log_event
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
    def log_event(c, t, d): print(f"[{c}] {t}: {d}")

logger = get_logger("MongoDB_Manager")

# Check MongoDB driver
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    logger.warning("pymongo not installed, database operations disabled")


class MongoDBManager:
    """Manage MongoDB operations"""
    
    def __init__(self, connection_uri: Optional[str] = None):
        """
        Initialize MongoDB connection
        
        Args:
            connection_uri: MongoDB connection string
        """
        if not MONGO_AVAILABLE:
            logger.error("MongoDB driver not available")
            self.client = None
            self.db = None
            return
        
        self.connection_uri = connection_uri or os.getenv(
            'MONGODB_URI', 
            'mongodb://localhost:27017/market_analysis'
        )
        
        try:
            self.client = MongoClient(self.connection_uri)
            self.db = self.client.market_analysis
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Connected to MongoDB")
            log_event("Database", "CONNECTION_SUCCESS", "Successfully connected to MongoDB")
            
            # Initialize collections
            self._initialize_collections()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            log_event("Database", "CONNECTION_FAILURE", f"MongoDB connection failed: {e}")
            self.client = None
            self.db = None
    
    def _initialize_collections(self):
        """Initialize required collections"""
        if not self.db:
            return
        
        # Regular collections
        regular_collections = [
            'watchlists',
            'analysis_results',
            'user_portfolios'
        ]
        
        for coll_name in regular_collections:
            if coll_name not in self.db.list_collection_names():
                self.db.create_collection(coll_name)
                logger.info(f"Created collection: {coll_name}")
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes"""
        if not self.db:
            return
        
        try:
            # Watchlist indexes
            self.db.watchlists.create_index([('userId', 1), ('symbol', 1), ('exchange', 1)], unique=True)
            self.db.watchists.create_index([('userId', 1)])
            
            # Analysis results indexes
            self.db.analysis_results.create_index([('symbol', 1), ('timestamp', -1)])
            self.db.analysis_results.create_index([('analysisId', 1)], unique=True)
            
            logger.info("Created database indexes")
        except Exception as e:
            logger.warning(f"Index creation failed: {e}")
    
    # Watchlist operations
    
    def add_to_watchlist(
        self,
        user_id: str,
        symbol: str,
        exchange: str = "NSE"
    ) -> bool:
        """Add stock to user's watchlist"""
        if not self.db:
            return False
        
        try:
            self.db.watchlists.update_one(
                {'userId': user_id, 'symbol': symbol, 'exchange': exchange},
                {
                    '$set': {
                        'userId': user_id,
                        'symbol': symbol,
                        'exchange': exchange,
                        'addedAt': datetime.utcnow()
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add to watchlist: {e}")
            return False
    
    def get_watchlist(self, user_id: str) -> List[Dict]:
        """Get user's watchlist"""
        if not self.db:
            return []
        
        try:
            return list(self.db.watchlists.find(
                {'userId': user_id},
                {'_id': 0}
            ))
        except Exception as e:
            logger.error(f"Failed to get watchlist: {e}")
            return []
    
    def remove_from_watchlist(
        self,
        user_id: str,
        symbol: str,
        exchange: str = "NSE"
    ) -> bool:
        """Remove stock from watchlist"""
        if not self.db:
            return False
        
        try:
            result = self.db.watchlists.delete_one({
                'userId': user_id,
                'symbol': symbol,
                'exchange': exchange
            })
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to remove from watchlist: {e}")
            return False
    
    # Analysis results
    
    def save_analysis_result(
        self,
        analysis_id: str,
        symbol: str,
        exchange: str,
        result: Dict[str, Any]
    ) -> bool:
        """Save analysis result"""
        if not self.db:
            return False
        
        try:
            document = {
                'analysisId': analysis_id,
                'symbol': symbol,
                'exchange': exchange,
                'timestamp': datetime.utcnow(),
                'result': result
            }
            
            self.db.analysis_results.insert_one(document)
            logger.info(f"Saved analysis result for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            return False
    
    def get_analysis_result(self, analysis_id: str) -> Optional[Dict]:
        """Get analysis result by ID"""
        if not self.db:
            return None
        
        try:
            result = self.db.analysis_results.find_one(
                {'analysisId': analysis_id},
                {'_id': 0}
            )
            return result
        except Exception as e:
            logger.error(f"Failed to get analysis result: {e}")
            return None
    
    def get_latest_analysis(self, symbol: str, exchange: str) -> Optional[Dict]:
        """Get latest analysis for a stock"""
        if not self.db:
            return None
        
        try:
            result = self.db.analysis_results.find_one(
                {'symbol': symbol, 'exchange': exchange},
                {'_id': 0},
                sort=[('timestamp', -1)]
            )
            return result
        except Exception as e:
            logger.error(f"Failed to get latest analysis: {e}")
            return None
    
    # Time series data (would be stored in TimeSeries collections in production)
    
    def save_price_data(self, symbol: str, exchange: str, data: Dict):
        """Save historical price data"""
        # In production, this would use TimeSeries collection
        # For now, we skip as it's handled by cache
        pass
    
    def save_technical_indicators(self, symbol: str, indicators: Dict):
        """Save technical indicators"""
        # Would use TimeSeries collection in production
        pass


# Singleton instance
_mongo_manager: Optional[MongoDBManager] = None


def get_db_manager() -> MongoDBManager:
    """Get global database manager instance"""
    global _mongo_manager
    
    if _mongo_manager is None:
        _mongo_manager = MongoDBManager()
    
    return _mongo_manager


if __name__ == "__main__":
    # Test MongoDB connection
    logging.basicConfig(level=logging.INFO)
    
    manager = MongoDBManager()
    
    if manager.db:
        # Test watchlist operations
        manager.add_to_watchlist("test_user", "RELIANCE", "NSE")
        watchlist = manager.get_watchlist("test_user")
        print(f"Watchlist: {watchlist}")
        
        # Test analysis result
        test_result = {
            'recommendation': 'BUY',
            'price': 2450.50,
            'confidence': 0.75
        }
        manager.save_analysis_result("test_123", "RELIANCE", "NSE", test_result)
        
        retrieved = manager.get_analysis_result("test_123")
        print(f"Retrieved analysis: {retrieved}")
        
        print("\n✓ MongoDB operations working!")
    else:
        print("MongoDB not available")
