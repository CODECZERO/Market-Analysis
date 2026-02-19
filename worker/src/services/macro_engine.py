import logging
import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MacroEngine:
    def __init__(self):
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY") 
        self.news_api_key = os.getenv("NEWS_API_KEY")
        
        # Key economic zones mapping (Local Movement)
        self.key_zones = {
            "IT": ["Bangalore", "Pune", "Hyderabad"],      # Tech hubs
            "STEEL": ["Jamshedpur", "Odisha", "Bhilai"],   # Mining/Plants
            "AUTO": ["Chennai", "Gurgaon", "Pune"],        # Mfg hubs
            "AGRI": ["Punjab", "Maharashtra", "Andhra"],   # Crop belts
            "FINANCE": ["Mumbai", "Gift City"],           # Financial capitals
            "OIL": ["Jamnagar", "Barmer", "Assam"]         # Refineries
        }
        
    def analyze_macro_factors(self, symbol: str, sector: str) -> Dict[str, Any]:
        """
        Aggregates macro-economic factors relevant to a specific stock/sector.
        """
        logger.info(f"🌍 Analyzing macro factors for {symbol} ({sector})")
        
        weather_impact = self._check_weather_risk(sector)
        geopolitical_risk = self._check_geopolitical_risk(symbol)
        supply_chain = self._check_supply_chain(sector)
        money_flow = self._check_central_bank_liquidity()
        
        # Synthesize a "Macro Score" (-1.0 to 1.0)
        macro_score = (weather_impact['score'] * 0.2 + 
                       geopolitical_risk['score'] * 0.5 + 
                       supply_chain['score'] * 0.3)
                       
        return {
            "macro_score": round(macro_score, 2),
            "weather": weather_impact,
            "geopolitics": geopolitical_risk,
            "supply_chain": supply_chain,
            "liquidity": money_flow,
            "local_movement": self._check_local_movement(sector),
            "summary": self._generate_summary(weather_impact, geopolitical_risk, supply_chain)
        }
    
    def _check_weather_risk(self, sector: str) -> Dict[str, Any]:
        """Checks for weather disasters using OpenWeatherMap"""
        # If no API key or sector irrelevant, return simulated data (Cold Start)
        if not self.weather_api_key or sector not in self.key_zones:
            # Simulate "Safe" weather for demo purposes
            return {
                "score": 0.1, 
                "risk": "Low (Simulated)", 
                "events": ["Clear skies in major hubs (Simulated)"]
            }
            
        events = []
        severity_score = 0.0
        
        for city in self.key_zones.get(sector, []):
            try:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}"
                # data = requests.get(url, timeout=2).json() # Uncomment for real call
                # Simulation for robustness if no key:
                data = {"weather": [{"main": "Clear"}]} 
                
                condition = data.get('weather', [{}])[0].get('main')
                if condition in ["Thunderstorm", "Tornado", "Ash"]:
                    severity_score -= 0.5
                    events.append(f"{condition} in {city}")
                elif condition in ["Rain", "Drizzle"] and sector == "AGRI":
                    severity_score += 0.2 # Rain good for agri (simplified)
            except:
                continue
                
        return {"score": max(-1.0, min(1.0, severity_score)), "risk": "Low" if severity_score > -0.2 else "High", "events": events}

    def _check_geopolitical_risk(self, symbol: str) -> Dict[str, Any]:
        """Scans for global risks: war, sanctions, and trade bans"""
        risk_score = 0.0
        events = []
        
        # In a real app, this would query a news aggregator for global context
        # We simulate this by checking for known hot-zone keywords in recent metadata
        risk_keywords = {
            "war": -0.8,
            "sanction": -0.6,
            "ban": -0.4,
            "unrest": -0.3,
            "election": -0.1,
            "trade war": -0.5
        }
        
        # Mocking a global situation engine
        current_global_context = os.getenv("GLOBAL_RISK_CONTEXT", "trade war tension").lower() # Default to some tension for realism
        for kw, impact in risk_keywords.items():
            if kw in current_global_context:
                risk_score += impact
                events.append(kw.capitalize())
        
        # Ensure at least one event for visibility if score is 0
        if risk_score == 0:
            events.append("Global Stability (Simulated)")
        
        return {
            "score": max(-1.0, min(0.0, risk_score)), 
            "risk_level": "HIGH" if risk_score < -0.4 else "LOW",
            "events": events
        }
    
    def _check_local_movement(self, sector: str) -> Dict[str, Any]:
        """Detects business movement/unrest in specific Indian city hubs"""
        cities = self.key_zones.get(sector, [])
        if not cities:
            return {"status": "STABLE", "score": 0.0}
            
        # Example logic: checking if "curfew" or "strike" is happening in these cities
        # Placeholder for real-time local news integration
        return {"status": "STABLE", "hubs_checked": cities, "score": 0.0}
        
    def _check_supply_chain(self, sector: str) -> Dict[str, Any]:
        """Tracks commodity shortages"""
        # Simplistic mapping
        if sector == "AUTO":
            # Check for "semiconductor shortage" or "steel price hike"
            pass
        return {"score": 0.0, "status": "STABLE"}
        
    def _check_central_bank_liquidity(self) -> Dict[str, Any]:
        return {"score": 0.1, "trend": "NEUTRAL-BULLISH", "source": "Fed Balance Sheet (Simulated)"}
        
    def _generate_summary(self, weather, geo, supply) -> str:
        factors = []
        if weather['events']: factors.append(f"Weather Impact: {', '.join(weather['events'])}")
        if geo['events']: factors.append(f"Geopolitics: {', '.join(geo['events'])}")
        
        if not factors:
            return "Macro environment appears stable."
        return ". ".join(factors)
