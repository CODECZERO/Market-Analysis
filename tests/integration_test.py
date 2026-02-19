"""
Integration Tests for Market Analysis API
"""

import requests
import time
import json

API_BASE = "http://localhost:8000"


def test_health_check():
    """Test health endpoint"""
    print("Testing health check...")
    response = requests.get(f"{API_BASE}/api/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['status'] in ['healthy', 'degraded', 'unhealthy']
    print(f"  ✓ Status: {data['status']}")
    print(f"  ✓ Redis: {data.get('redis')}")
    print(f"  ✓ MongoDB: {data.get('mongodb')}")
    print()


def test_analyze_stock():
    """Test stock analysis"""
    print("Testing stock analysis...")
    
    payload = {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "refresh": False
    }
    
    response = requests.post(f"{API_BASE}/api/stocks/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['success'] == True
    
    if data.get('cached'):
        print("  ✓ Got cached result")
        return data['data']
    else:
        analysis_id = data['data']['analysisId']
        print(f"  ✓ Analysis queued: {analysis_id}")
        return analysis_id


def test_get_progress(analysis_id):
    """Test progress tracking"""
    print(f"Testing progress for {analysis_id}...")
    
    response = requests.get(f"{API_BASE}/api/stocks/analyze/{analysis_id}/progress")
    
    if response.status_code == 200:
        data = response.json()
        progress = data.get('data', {})
        print(f"  ✓ Status: {progress.get('status')}")
        print(f"  ✓ Progress: {progress.get('progress', 0)}%")
        return progress.get('status')
    
    return None


def test_get_result(analysis_id):
    """Test result retrieval"""
    print(f"Testing result for {analysis_id}...")
    
    response = requests.get(f"{API_BASE}/api/stocks/analyze/{analysis_id}")
    
    if response.status_code == 200:
        data = response.json()
        
        if data['success']:
            result = data['data']
            print(f"  ✓ Got result for {result.get('symbol')}")
            print(f"  ✓ Rating: {result.get('recommendation', {}).get('rating')}")
            return True
    
    return False


def test_watchlist():
    """Test watchlist operations"""
    print("Testing watchlist...")
    
    # Add to watchlist
    payload = {"symbol": "TCS", "exchange": "NSE"}
    response = requests.post(f"{API_BASE}/api/stocks/watchlist", json=payload)
    
    assert response.status_code == 200
    print("  ✓ Added TCS to watchlist")
    
    # Get watchlist
    response = requests.get(f"{API_BASE}/api/stocks/watchlist")
    
    assert response.status_code == 200
    data = response.json()
    print(f"  ✓ Watchlist has {data['count']} stocks")
    
    # Remove from watchlist
    response = requests.delete(f"{API_BASE}/api/stocks/watchlist/TCS?exchange=NSE")
    
    assert response.status_code == 200
    print("  ✓ Removed TCS from watchlist")
    print()


def run_integration_tests():
    """Run all integration tests"""
    print("="*60)
    print("  Market Analysis API - Integration Tests")
    print("="*60)
    print()
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: Watchlist
        test_watchlist()
        
        # Test 3: Analysis
        result = test_analyze_stock()
        
        if isinstance(result, str):  # Got analysis ID
            # Wait and check progress
            print("\nWaiting for analysis to complete...")
            for i in range(6):  # Wait up to 60 seconds
                time.sleep(10)
                status = test_get_progress(result)
                
                if status == 'completed':
                    test_get_result(result)
                    break
        
        print()
        print("="*60)
        print("  ✅ All tests passed!")
        print("="*60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API server")
        print("   Make sure it's running: python api_server.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
