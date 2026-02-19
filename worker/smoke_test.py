
import sys
import os
import asyncio
from unittest.mock import MagicMock

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from worker.analyzer import Analyzer, AnalysisInput, GatekeeperCategory, LaunchPrediction
    from worker.llm_adapter import InstrumentedLLMAdapter
    print("Imports successful!")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

async def test_analyzer():
    # Mock LLM Adapter
    mock_llm = MagicMock(spec=InstrumentedLLMAdapter)
    
    async def mock_launch(prompt):
        return {
            "is_launch": True, 
            "product_name": "TestProduct", 
            "success_score": 88,
            "reason": "It rocks", 
            "reception": "positive",
            "hype_signals": ["Love it"],
            "skepticism_signals": []
        }
    mock_llm.detect_launch = mock_launch

    analyzer = Analyzer(mock_llm)
    
    # Test Gatekeeper
    cat = analyzer.regex_gatekeeper("Check out our new launch!", [])
    print(f"Gatekeeper (launch): {cat}")
    assert cat == GatekeeperCategory.LAUNCH
    
    cat = analyzer.regex_gatekeeper("I hate this bug.", [])
    print(f"Gatekeeper (pain): {cat}")
    assert cat == GatekeeperCategory.PAIN

    # Test Oracle
    input_data = AnalysisInput(text="Announcing new features!", target_brand="TestBrand")
    prediction = await analyzer.detect_launch(input_data)
    print(f"Oracle Prediction: {prediction}")
    assert prediction.is_launch == True
    assert prediction.success_score == 88

    print("All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_analyzer())
