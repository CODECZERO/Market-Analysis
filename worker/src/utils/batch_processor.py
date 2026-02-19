"""
Batch Processing Utility
Efficiently process multiple stocks with memory constraints
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Process stocks in small batches to avoid memory issues
    Designed for RTX 2050 with 4GB VRAM
    """
    
    def __init__(
        self,
        batch_size: int = 2,
        delay_between_batches: float = 5.0,
        max_retries: int = 3
    ):
        """
        Initialize batch processor
        
        Args:
            batch_size: Number of stocks to process simultaneously (keep low!)
            delay_between_batches: Seconds to wait between batches (for memory cleanup)
            max_retries: Number of retries on failure
        """
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches
        self.max_retries = max_retries
        self.current_batch = []
        self.failed_stocks = []
        
    async def process_watchlist(
        self,
        stock_symbols: List[str],
        analysis_function
    ) -> Dict[str, Any]:
        """
        Process entire watchlist in batches
        
        Args:
            stock_symbols: List of stock symbols to analyze
            analysis_function: Async function to analyze each stock
            
        Returns:
            Dictionary with results and statistics
        """
        total = len(stock_symbols)
        processed = 0
        successful = 0
        failed = 0
        results = []
        
        logger.info(f"Starting batch processing for {total} stocks")
        logger.info(f"Batch size: {self.batch_size}, Delay: {self.delay_between_batches}s")
        
        start_time = time.time()
        
        # Process in batches
        for i in range(0, total, self.batch_size):
            batch = stock_symbols[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (total + self.batch_size - 1) // self.batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches}: {batch}")
            
            # Process batch
            batch_results = await self._process_batch(batch, analysis_function)
            
            # Collect results
            for symbol, result in batch_results.items():
                processed += 1
                if result.get('success'):
                    successful += 1
                    results.append({
                        'symbol': symbol,
                        'data': result.get('data'),
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    failed += 1
                    self.failed_stocks.append({
                        'symbol': symbol,
                        'error': result.get('error'),
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Wait between batches (allow memory cleanup)
            if i + self.batch_size < total:
                logger.info(f"Batch {batch_num} complete. Waiting {self.delay_between_batches}s for memory cleanup...")
                await asyncio.sleep(self.delay_between_batches)
        
        elapsed_time = time.time() - start_time
        
        summary = {
            'total': total,
            'processed': processed,
            'successful': successful,
            'failed': failed,
            'elapsed_seconds': round(elapsed_time, 2),
            'avg_time_per_stock': round(elapsed_time / total, 2) if total > 0 else 0,
            'results': results,
            'failed_stocks': self.failed_stocks
        }
        
        logger.info(f"Batch processing complete: {successful}/{total} successful in {elapsed_time:.1f}s")
        
        return summary
    
    async def _process_batch(
        self,
        stock_symbols: List[str],
        analysis_function
    ) -> Dict[str, Dict]:
        """
        Process a single batch of stocks concurrently
        
        Args:
            stock_symbols: Batch of symbols to process
            analysis_function: Function to analyze each stock
            
        Returns:
            Dictionary mapping symbol to result
        """
        tasks = []
        
        for symbol in stock_symbols:
            task = self._process_with_retry(symbol, analysis_function)
            tasks.append(task)
        
        # Run all tasks in batch concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map results to symbols
        batch_results = {}
        for symbol, result in zip(stock_symbols, results):
            if isinstance(result, Exception):
                batch_results[symbol] = {
                    'success': False,
                    'error': str(result)
                }
            else:
                batch_results[symbol] = result
        
        return batch_results
    
    async def _process_with_retry(
        self,
        symbol: str,
        analysis_function
    ) -> Dict[str, Any]:
        """
        Process single stock with retries
        
        Args:
            symbol: Stock symbol
            analysis_function: Analysis function
            
        Returns:
            Result dictionary
        """
        for attempt in range(self.max_retries):
            try:
                result = await analysis_function(symbol)
                return {
                    'success': True,
                    'data': result
                }
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed for {symbol}: {e}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return {
                        'success': False,
                        'error': str(e)
                    }


class MemoryMonitor:
    """Monitor and log memory usage"""
    
    @staticmethod
    def get_gpu_memory_usage() -> Dict[str, float]:
        """Get current GPU memory usage"""
        try:
            import tensorflow as tf
            
            gpus = tf.config.list_physical_devices('GPU')
            if not gpus:
                return {'available': False}
            
            # Get memory info
            memory_info = tf.config.experimental.get_memory_info('GPU:0')
            
            return {
                'available': True,
                'current_mb': memory_info['current'] / 1024 / 1024,
                'peak_mb': memory_info['peak'] / 1024 / 1024,
                'limit_mb': 3072  # Our configured limit
            }
        except Exception as e:
            logger.warning(f"Could not get GPU memory info: {e}")
            return {'available': False, 'error': str(e)}
    
    @staticmethod
    def log_memory_usage():
        """Log current memory usage"""
        gpu_mem = MemoryMonitor.get_gpu_memory_usage()
        
        if gpu_mem.get('available'):
            logger.info(
                f"GPU Memory: {gpu_mem['current_mb']:.1f}MB / {gpu_mem['limit_mb']}MB "
                f"(Peak: {gpu_mem['peak_mb']:.1f}MB)"
            )
        else:
            logger.info("GPU not available or monitoring failed")


# Example usage
async def example_usage():
    """Example of batch processing"""
    
    # Define analysis function
    async def analyze_stock(symbol: str) -> Dict:
        """Dummy analysis function"""
        logger.info(f"Analyzing {symbol}...")
        await asyncio.sleep(2)  # Simulate processing
        return {
            'symbol': symbol,
            'recommendation': 'BUY',
            'confidence': 0.75
        }
    
    # Create batch processor
    processor = BatchProcessor(
        batch_size=2,           # Process 2 stocks at a time
        delay_between_batches=5.0,  # 5 second delay
        max_retries=3
    )
    
    # Watchlist
    watchlist = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
    
    # Process
    results = await processor.process_watchlist(watchlist, analyze_stock)
    
    # Print summary
    print(f"\nProcessed: {results['successful']}/{results['total']}")
    print(f"Time: {results['elapsed_seconds']}s")
    print(f"Avg per stock: {results['avg_time_per_stock']}s")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_usage())
