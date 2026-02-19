"""
Comprehensive Testing Suite
Tests for all system components
"""

import sys
sys.path.append('/home/codeczero/Desktop/FullStack/Brand-Mention-Reputation-Tracker/market_analysis/worker/src')

def test_data_acquisition():
    """Test all data sources"""
    print("\n" + "="*70)
    print("TESTING DATA ACQUISITION")
    print("="*70)
    
    results = {}
    
    # Test YFinance
    print("\n1. Testing YFinance Provider...")
    try:
        from providers.yfinance_provider import YFinanceProvider
        provider = YFinanceProvider()
        data = provider.get_stock_data("RELIANCE.NS")
        results['yfinance'] = '✅ PASS' if data else '❌ FAIL'
        print(f"   {results['yfinance']}")
    except Exception as e:
        results['yfinance'] = f'❌ FAIL: {e}'
        print(f"   {results['yfinance']}")
    
    # Test NSETools
    print("\n2. Testing NSETools Provider...")
    try:
        from providers.nsetools_provider import NSEToolsProvider
        provider = NSEToolsProvider()
        quote = provider.get_quote("RELIANCE")
        results['nsetools'] = '✅ PASS' if quote else '❌ FAIL'
        print(f"   {results['nsetools']}")
    except Exception as e:
        results['nsetools'] = f'❌ FAIL: {e}'
        print(f"   {results['nsetools']}")
    
    # Test Finnhub
    print("\n3. Testing Finnhub Provider...")
    try:
        from providers.finnhub_provider import FinnhubProvider
        provider = FinnhubProvider()
        quote = provider.get_quote("AAPL")
        results['finnhub'] = '✅ PASS' if quote else '❌ FAIL'
        print(f"   {results['finnhub']}")
    except Exception as e:
        results['finnhub'] = f'❌ FAIL: {e}'
        print(f"   {results['finnhub']}")
    
    # Test Enhanced OHLCV
    print("\n4. Testing Enhanced OHLCV Fetcher...")
    try:
        from providers.enhanced_ohlcv_fetcher import EnhancedOHLCVFetcher
        fetcher = EnhancedOHLCVFetcher()
        data = fetcher.get_52_week_high_low("RELIANCE.NS")
        results['ohlcv'] = '✅ PASS' if data else '❌ FAIL'
        print(f"   {results['ohlcv']}")
    except Exception as e:
        results['ohlcv'] = f'❌ FAIL: {e}'
        print(f"   {results['ohlcv']}")
    
    # Test Options & Futures
    print("\n5. Testing Options & Futures Provider...")
    try:
        from providers.options_futures_provider import OptionsFuturesProvider
        provider = OptionsFuturesProvider()
        options = provider.get_options_chain("RELIANCE.NS")
        results['options'] = '✅ PASS' if options else '❌ FAIL'
        print(f"   {results['options']}")
    except Exception as e:
        results['options'] = f'❌ FAIL: {e}'
        print(f"   {results['options']}")
    
    return results

def test_scrapers():
    """Test all news and social scrapers"""
    print("\n" + "="*70)
    print("TESTING SCRAPERS")
    print("="*70)
    
    results = {}
    
    # Test MoneyControl
    print("\n1. Testing MoneyControl Scraper...")
    try:
        from scrapers.moneycontrol_scraper import MoneyControlScraper
        scraper = MoneyControlScraper()
        news = scraper.scrape_stock_news("RELIANCE", limit=2)
        results['moneycontrol'] = '✅ PASS' if news else '❌ FAIL'
        print(f"   {results['moneycontrol']}")
    except Exception as e:
        results['moneycontrol'] = f'❌ FAIL: {e}'
        print(f"   {results['moneycontrol']}")
    
    # Test Economic Times
    print("\n2. Testing Economic Times Scraper...")
    try:
        from scrapers.economictimes_scraper import EconomicTimesScraper
        scraper = EconomicTimesScraper()
        news = scraper.scrape_stock_news("RELIANCE", limit=2)
        results['et'] = '✅ PASS' if news else '❌ FAIL'
        print(f"   {results['et']}")
    except Exception as e:
        results['et'] = f'❌ FAIL: {e}'
        print(f"   {results['et']}")
    
    # Test Business Standard
    print("\n3. Testing Business Standard Scraper...")
    try:
        from scrapers.business_standard_scraper import BusinessStandardScraper
        scraper = BusinessStandardScraper()
        news = scraper.scrape_stock_news("RELIANCE", limit=2)
        results['bs'] = '✅ PASS' if news else '❌ FAIL'
        print(f"   {results['bs']}")
    except Exception as e:
        results['bs'] = f'❌ FAIL: {e}'
        print(f"   {results['bs']}")
    
    # Test StockTwits
    print("\n4. Testing StockTwits Scraper...")
    try:
        from scrapers.stocktwits_scraper import StockTwitsScraper
        scraper = StockTwitsScraper()
        messages = scraper.scrape_discussions("AAPL", limit=2)
        results['stocktwits'] = '✅ PASS' if messages else '❌ FAIL'
        print(f"   {results['stocktwits']}")
    except Exception as e:
        results['stocktwits'] = f'❌ FAIL: {e}'
        print(f"   {results['stocktwits']}")
    
    return results

def test_technical_indicators():
    """Test technical indicators"""
    print("\n" + "="*70)
    print("TESTING TECHNICAL INDICATORS")
    print("="*70)
    
    results = {}
    
    print("\n1. Testing Technical Indicators Module...")
    try:
        from analysis.technical_indicators import TechnicalIndicators
        import yfinance as yf
        
        ticker = yf.Ticker("RELIANCE.NS")
        data = ticker.history(period="1y")
        
        indicators = TechnicalIndicators(data)
        rsi = indicators.calculate_rsi()
        macd = indicators.calculate_macd()
        
        results['indicators'] = '✅ PASS' if rsi is not None and macd is not None else '❌ FAIL'
        print(f"   {results['indicators']}")
        print(f"   RSI: {rsi:.2f}") if rsi else None
    except Exception as e:
        results['indicators'] = f'❌ FAIL: {e}'
        print(f"   {results['indicators']}")
    
    return results

def test_ml_models():
    """Test ML models"""
    print("\n" + "="*70)
    print("TESTING ML MODELS")
    print("="*70)
    
    results = {}
    
    # Test XGBoost
    print("\n1. Testing XGBoost Classifier...")
    try:
        from ml.xgboost_classifier import XGBoostSignalClassifier
        model = XGBoostSignalClassifier()
        results['xgboost'] = '✅ PASS - Model created'
        print(f"   {results['xgboost']}")
    except Exception as e:
        results['xgboost'] = f'❌ FAIL: {e}'
        print(f"   {results['xgboost']}")
    
    # Test LSTM
    print("\n2. Testing LSTM Model...")
    try:
        from ml.lstm_predictor import LSTMPredictor
        model = LSTMPredictor()
        results['lstm'] = '✅ PASS - Model created'
        print(f"   {results['lstm']}")
    except Exception as e:
        results['lstm'] = f'❌ FAIL: {e}'
        print(f"   {results['lstm']}")
    
    return results

def test_correlations():
    """Test correlation engines"""
    print("\n" + "="*70)
    print("TESTING CORRELATION ENGINES")
    print("="*70)
    
    results = {}
    
    # Test Sector Correlation
    print("\n1. Testing Sector Analyzer...")
    try:
        from analysis.sector_analyzer import SectorAnalyzer
        analyzer = SectorAnalyzer()
        correlations = analyzer.calculate_sector_correlations()
        results['sector'] = '✅ PASS' if correlations else '❌ FAIL'
        print(f"   {results['sector']}")
    except Exception as e:
        results['sector'] = f'❌ FAIL: {e}'
        print(f"   {results['sector']}")
    
    # Test News-Event Correlation
    print("\n2. Testing News-Event Correlation...")
    try:
        from analysis.news_event_correlation import NewsEventCorrelation
        analyzer = NewsEventCorrelation()
        analyzer.load_price_data("RELIANCE.NS")
        results['news_correlation'] = '✅ PASS'
        print(f"   {results['news_correlation']}")
    except Exception as e:
        results['news_correlation'] = f'❌ FAIL: {e}'
        print(f"   {results['news_correlation']}")
    
    return results

def test_services():
    """Test new services"""
    print("\n" + "="*70)
    print("TESTING SERVICES")
    print("="*70)
    
    results = {}
    
    # Test Portfolio Tracker
    print("\n1. Testing Portfolio Tracker...")
    try:
        from services.portfolio_tracker import Portfolio
        portfolio = Portfolio()
        results['portfolio'] = '✅ PASS'
        print(f"   {results['portfolio']}")
    except Exception as e:
        results['portfolio'] = f'❌ FAIL: {e}'
        print(f"   {results['portfolio']}")
    
    # Test Alerts Manager
    print("\n2. Testing Alerts Manager...")
    try:
        from services.alerts_manager import AlertsManager
        manager = AlertsManager()
        results['alerts'] = '✅ PASS'
        print(f"   {results['alerts']}")
    except Exception as e:
        results['alerts'] = f'❌ FAIL: {e}'
        print(f"   {results['alerts']}")
    
    return results

def generate_test_report(all_results: Dict):
    """Generate test summary report"""
    print("\n\n" + "="*70)
    print("TEST SUMMARY REPORT")
    print("="*70)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        print(f"\n{category.upper()}:")
        for test_name, result in results.items():
            total_tests += 1
            if '✅ PASS' in result:
                passed_tests += 1
            print(f"  {test_name}: {result}")
    
    print("\n" + "="*70)
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"TOTAL: {passed_tests}/{total_tests} tests passed ({pass_rate:.1f}%)")
    print("="*70)

def run_all_tests():
    """Run comprehensive test suite"""
    print("\n\n")
    print("█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  MARKET ANALYSIS SYSTEM - COMPREHENSIVE TEST SUITE  ".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    all_results = {}
    
    # Run all test categories
    all_results['Data Acquisition'] = test_data_acquisition()
    all_results['Scrapers'] = test_scrapers()
    all_results['Technical Indicators'] = test_technical_indicators()
    all_results['ML Models'] = test_ml_models()
    all_results['Correlations'] = test_correlations()
    all_results['Services'] = test_services()
    
    # Generate final report
    generate_test_report(all_results)
    
    print("\n✅ Test suite completed!\n")

if __name__ == "__main__":
    run_all_tests()
