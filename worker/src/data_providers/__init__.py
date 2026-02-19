"""
Data Providers Module
Centralized data acquisition for Indian stock market
"""

from .yfinance_provider import (
    YFinanceProvider,
    get_stock_data,
    get_nifty_data
)

__all__ = [
    'YFinanceProvider',
    'get_stock_data',
    'get_nifty_data',
]
