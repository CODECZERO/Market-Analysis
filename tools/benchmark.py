"""
Performance Benchmarking Tool
Measures system performance under various loads
"""

import time
import asyncio
import statistics
from typing import List, Dict
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.python.market_analysis_client import MarketAnalysisClient


class PerformanceBenchmark:
    """Benchmark system performance"""
    
    def __init__(self, api_url: str = "http://localhost:3000"):
        self.client = MarketAnalysisClient(api_url)
        self.results = []
    
    def benchmark_single_analysis(
        self,
        symbol: str = "RELIANCE",
        exchange: str = "NSE",
        runs: int = 3
    ) -> Dict:
        """Benchmark single stock analysis"""
        print(f"\n=== Benchmarking Single Analysis ({symbol}) ===")
        print(f"Runs: {runs}")
        
        times = []
        
        for i in range(runs):
            print(f"Run {i+1}/{runs}...", end=" ")
            
            start = time.time()
            try:
                self.client.analyze_stock(
                    symbol,
                    exchange,
                    refresh=True,
                    wait_for_completion=True,
                    max_wait=180
                )
                elapsed = time.time() - start
                times.append(elapsed)
                print(f"✓ {elapsed:.1f}s")
            except Exception as e:
                print(f"✗ Failed: {e}")
        
        if not times:
            return {'error': 'All runs failed'}
        
        return {
            'test': 'single_analysis',
            'symbol': symbol,
            'runs': runs,
            'successful': len(times),
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def benchmark_batch_analysis(
        self,
        symbols: List[str] = None,
        exchange: str = "NSE"
    ) -> Dict:
        """Benchmark batch analysis"""
        if symbols is None:
            symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
        
        print(f"\n=== Benchmarking Batch Analysis ===")
        print(f"Stocks: {len(symbols)}")
        
        start = time.time()
        successful = 0
        failed = 0
        
        for i, symbol in enumerate(symbols):
            print(f"[{i+1}/{len(symbols)}] {symbol}...", end=" ")
            
            try:
                self.client.analyze_stock(symbol, exchange, refresh=True)
                successful += 1
                print("✓")
            except Exception as e:
                failed += 1
                print(f"✗ {e}")
            
            # Small delay between requests
            time.sleep(2)
        
        elapsed = time.time() - start
        
        return {
            'test': 'batch_analysis',
            'total_stocks': len(symbols),
            'successful': successful,
            'failed': failed,
            'total_time': elapsed,
            'avg_per_stock': elapsed / len(symbols)
        }
    
    def benchmark_api_latency(self, calls: int = 10) -> Dict:
        """Benchmark API endpoint latency"""
        print(f"\n=== Benchmarking API Latency ===")
        print(f"Calls: {calls}")
        
        endpoints = {
            'get_watchlist': lambda: self.client.get_watchlist(),
            'search': lambda: self.client.search_stocks("RELIANCE"),
            'get_quote': lambda: self.client.get_quote("RELIANCE", "NSE")
        }
        
        results = {}
        
        for name, func in endpoints.items():
            print(f"Testing {name}...", end=" ")
            times = []
            
            for _ in range(calls):
                start = time.time()
                try:
                    func()
                    elapsed = time.time() - start
                    times.append(elapsed * 1000)  # Convert to ms
                except:
                    pass
            
            if times:
                results[name] = {
                    'avg_ms': statistics.mean(times),
                    'min_ms': min(times),
                    'max_ms': max(times),
                    'p95_ms': sorted(times)[int(len(times) * 0.95)]
                }
                print(f"✓ {results[name]['avg_ms']:.1f}ms avg")
            else:
                print("✗ Failed")
        
        return {
            'test': 'api_latency',
            'endpoints': results
        }
    
    def benchmark_memory_usage(self) -> Dict:
        """Benchmark memory usage (requires psutil)"""
        try:
            import psutil
            import subprocess
            
            print(f"\n=== Benchmarking Memory Usage ===")
            
            # Get Docker container stats
            result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format', '{{.MemUsage}}', 'market_analysis_worker'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                mem_usage = result.stdout.strip()
                print(f"Worker Memory: {mem_usage}")
                
                return {
                    'test': 'memory_usage',
                    'worker_memory': mem_usage
                }
            else:
                return {'test': 'memory_usage', 'error': 'Docker not available'}
                
        except ImportError:
            return {'test': 'memory_usage', 'error': 'psutil not installed'}
        except Exception as e:
            return {'test': 'memory_usage', 'error': str(e)}
    
    def run_full_benchmark(self) -> Dict:
        """Run complete benchmark suite"""
        print("="*60)
        print("  Market Analysis System - Performance Benchmark")
        print("="*60)
        
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tests': []
        }
        
        # Test 1: Single analysis
        result1 = self.benchmark_single_analysis(runs=2)
        results['tests'].append(result1)
        
        # Test 2: API latency
        result2 = self.benchmark_api_latency(calls=5)
        results['tests'].append(result2)
        
        # Test 3: Memory
        result3 = self.benchmark_memory_usage()
        results['tests'].append(result3)
        
        # Print summary
        print("\n" + "="*60)
        print("  Summary")
        print("="*60)
        
        if 'avg_time' in result1:
            print(f"Single Analysis: {result1['avg_time']:.1f}s avg")
        
        if 'endpoints' in result2:
            for ep, stats in result2['endpoints'].items():
                print(f"{ep}: {stats['avg_ms']:.1f}ms avg")
        
        if 'worker_memory' in result3:
            print(f"Worker Memory: {result3['worker_memory']}")
        
        print("\n✓ Benchmark complete!")
        
        return results


def main():
    """Run benchmark"""
    benchmark = PerformanceBenchmark()
    results = benchmark.run_full_benchmark()
    
    # Save results
    import json
    with open('benchmark_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to benchmark_results.json")


if __name__ == "__main__":
    main()
