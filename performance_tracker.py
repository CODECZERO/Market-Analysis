#!/usr/bin/env python3
"""
Performance Tracker - Track recommendations and calculate success rate
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import pandas as pd

HISTORY_FILE = "data/recommendation_history.json"
PERFORMANCE_FILE = "data/performance_stats.json"

def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs("data", exist_ok=True)

def save_recommendation(symbol: str, recommendation: Dict):
    """Save a recommendation for tracking"""
    ensure_data_dir()
    
    # Load existing history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = []
    
    # Add timestamp and save
    rec = {
        **recommendation,
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "status": "active"  # active, success, failed
    }
    
    history.append(rec)
    
    # Save history
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    return rec

def update_recommendation_result(rec_id: int, result: str, actual_return: float):
    """Update recommendation outcome"""
    ensure_data_dir()
    
    if not os.path.exists(HISTORY_FILE):
        return
    
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    
    if rec_id < len(history):
        history[rec_id]['status'] = result  # 'success' or 'failed'
        history[rec_id]['actual_return'] = actual_return
        history[rec_id]['closed_at'] = datetime.now().isoformat()
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def calculate_performance_stats() -> Dict:
    """Calculate overall performance statistics"""
    ensure_data_dir()
    
    if not os.path.exists(HISTORY_FILE):
        return {
            "total_recommendations": 0,
            "success_rate": 0,
            "avg_return": 0,
            "best_pick": None,
            "worst_pick": None
        }
    
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    
    total = len(history)
    closed = [h for h in history if h.get('status') in ['success', 'failed']]
    
    if not closed:
        return {
            "total_recommendations": total,
            "active_recommendations": total,
            "success_rate": 0,
            "avg_return": 0
        }
    
    successes = len([h for h in closed if h['status'] == 'success'])
    returns = [h.get('actual_return', 0) for h in closed]
    
    stats = {
        "total_recommendations": total,
        "active_recommendations": len([h for h in history if h['status'] == 'active']),
        "closed_positions": len(closed),
        "successful_trades": successes,
        "failed_trades": len(closed) - successes,
        "success_rate": (successes / len(closed) * 100) if closed else 0,
        "avg_return": sum(returns) / len(returns) if returns else 0,
        "best_return": max(returns) if returns else 0,
        "worst_return": min(returns) if returns else 0,
        "total_return": sum(returns)
    }
    
    # Save stats
    with open(PERFORMANCE_FILE, 'w') as f:
        json.dump(stats, f, indent=2)
    
    return stats

def get_recent_recommendations(limit: int = 10) -> List[Dict]:
    """Get recent recommendations"""
    ensure_data_dir()
    
    if not os.path.exists(HISTORY_FILE):
        return []
    
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    
    return sorted(history, key=lambda x: x['timestamp'], reverse=True)[:limit]

def export_to_csv(filename: str = "data/analysis_export.csv"):
    """Export recommendations to CSV"""
    ensure_data_dir()
    
    if not os.path.exists(HISTORY_FILE):
        print("No data to export")
        return
    
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    
    df = pd.DataFrame(history)
    df.to_csv(filename, index=False)
    print(f"✅ Exported {len(history)} records to {filename}")
    return filename

if __name__ == "__main__":
    # Test
    stats = calculate_performance_stats()
    print("Performance Stats:", json.dumps(stats, indent=2))
