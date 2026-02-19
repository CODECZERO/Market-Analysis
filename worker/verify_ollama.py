#!/usr/bin/env python3
"""
Quick verification that worker configuration is correct for Ollama deployment.
Run this before deploying to production.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from worker.config import get_settings

def verify_config():
    """Verify worker configuration for Ollama."""
    print("Verifying Worker Configuration...")
    print("=" * 60)
    
    settings = get_settings()
    
    checks = []
    
    # Check 1: LLM Provider
    if settings.llm_provider == "ollama":
        print("LLM Provider: ollama")
        checks.append(True)
    else:
        print(f"LLM Provider: {settings.llm_provider} (should be 'ollama')")
        checks.append(False)
    
    # Check 2: Ollama URL
    if settings.ollama_base_url:
        print(f"Ollama URL: {settings.ollama_base_url}")
        checks.append(True)
    else:
        print("Ollama URL not set")
        checks.append(False)
    
    # Check 3: Ollama Model
    if settings.ollama_model:
        print(f"Ollama Model: {settings.ollama_model}")
        checks.append(True)
    else:
        print("Ollama Model not set")
        checks.append(False)
    
    # Check 4: Redis URL
    if settings.redis_url:
        print(f"Redis URL: {settings.redis_url}")
        checks.append(True)
    else:
        print("Redis URL not set")
        checks.append(False)
    
    # Check 5: Embeddings Provider
    if settings.embeddings_provider in ["local", "ollama"]:
        print(f"Embeddings: {settings.embeddings_provider} (no API key needed)")
        checks.append(True)
    else:
        print(f"Embeddings: {settings.embeddings_provider} (may need API key)")
        checks.append(True)  # Just a warning
    
    print("=" * 60)
    
    if all(checks):
        print("\nConfiguration is READY for Ollama deployment!")
        print("\nNext steps:")
        print("1. Push code to Git")
        print("2. Update Koyeb environment variables:")
        print("   - LLM_PROVIDER=ollama")
        print(f"   - OLLAMA_BASE_URL={settings.ollama_base_url}")
        print(f"   - OLLAMA_MODEL={settings.ollama_model}")
        print("3. Click 'Deploy' on Koyeb")
        return 0
    else:
        print("\nConfiguration has issues. Fix them before deploying.")
        return 1

if __name__ == "__main__":
    exit(verify_config())
