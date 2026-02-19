"""
Input Validation and Sanitization Utilities
Protects against NoSQL injection and invalid inputs
"""

import re
from typing import Any, Dict, Optional
from fastapi import HTTPException


class InputValidator:
    """Comprehensive input validation for API endpoints"""
    
    @staticmethod
    def sanitize_symbol(symbol: str) -> str:
        """
        Validate and sanitize stock symbol.
        
        Prevents:
        - NoSQL injection ($ne, $regex, etc.)
        - Path traversal
        - Special characters
        
        Args:
            symbol: Raw symbol input
            
        Returns:
            Sanitized uppercase symbol
            
        Raises:
            HTTPException: If symbol invalid
        """
        if not isinstance(symbol, str):
            raise HTTPException(status_code=400, detail="Symbol must be a string")
        
        if not symbol or len(symbol.strip()) == 0:
            raise HTTPException(status_code=400, detail="Symbol cannot be empty")
        
        # Remove all non-alphanumeric except dots and hyphens
        sanitized = re.sub(r'[^\w\.-]', '', symbol)
        
        # Check length
        if len(sanitized) > 20:
            raise HTTPException(status_code=400, detail="Symbol too long (max 20 characters)")
        
        if len(sanitized) < 1:
            raise HTTPException(status_code=400, detail="Symbol invalid after sanitization")
        
        # Must match stock symbol pattern
        if not re.match(r'^[A-Z0-9\.-]{1,20}$', sanitized.upper()):
            raise HTTPException(status_code=400, detail="Invalid symbol format")
        
        return sanitized.upper().strip()
    
    @staticmethod
    def validate_timeframe(timeframe: str) -> str:
        """
        Validate timeframe parameter.
        
        Args:
            timeframe: 'long' or 'short'
            
        Returns:
            Validated timeframe
            
        Raises:
            HTTPException: If invalid
        """
        if not isinstance(timeframe, str):
            raise HTTPException(status_code=400, detail="Timeframe must be a string")
        
        valid_timeframes = ["long", "short"]
        timeframe = timeframe.lower().strip()
        
        if timeframe not in valid_timeframes:
            raise HTTPException(
                status_code=400,
                detail=f"Timeframe must be one of: {', '.join(valid_timeframes)}"
            )
        
        return timeframe
    
    @staticmethod
    def validate_limit(limit: int, min_val: int = 1, max_val: int = 50) -> int:
        """
        Validate pagination limit.
        
        Args:
            limit: Number of items to return
            min_val: Minimum allowed
            max_val: Maximum allowed
            
        Returns:
            Validated limit
            
        Raises:
            HTTPException: If invalid
        """
        if not isinstance(limit, int):
            raise HTTPException(status_code=400, detail="Limit must be an integer")
        
        if limit < min_val:
            raise HTTPException(status_code=400, detail=f"Limit must be at least {min_val}")
        
        if limit > max_val:
            raise HTTPException(status_code=400, detail=f"Limit cannot exceed {max_val}")
        
        return limit
    
    @staticmethod
    def sanitize_mongodb_query(query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize MongoDB query to prevent NoSQL injection.
        
        Removes MongoDB operators like:
        - $ne (not equal)
        - $gt, $gte, $lt, $lte (comparisons)
        - $regex (regex injection)
        - $where (code injection)
        
        Args:
            query: MongoDB query dict
            
        Returns:
            Sanitized query
        """
        dangerous_operators = [
            '$ne', '$gt', '$gte', '$lt', '$lte',
            '$regex', '$where', '$expr', '$jsonSchema',
            '$text', '$mod', '$all', '$elemMatch'
        ]
        
        sanitized = {}
        
        for key, value in query.items():
            # Remove keys starting with $
            if key.startswith('$'):
                continue
            
            # If value is dict, check for operators
            if isinstance(value, dict):
                value_sanitized = {}
                for k, v in value.items():
                    if k not in dangerous_operators:
                        value_sanitized[k] = v
                sanitized[key] = value_sanitized
            else:
                sanitized[key] = value
        
        return sanitized


# Convenience functions
def validate_symbol(symbol: str) -> str:
    """Shorthand for symbol validation"""
    return InputValidator.sanitize_symbol(symbol)


def validate_stock_request(symbol: str, use_llm: bool = True, use_scrapers: bool = True) -> Dict[str, Any]:
    """Validate complete stock analysis request"""
    return {
        "symbol": InputValidator.sanitize_symbol(symbol),
        "use_llm": isinstance(use_llm, bool) and use_llm,
        "use_scrapers": isinstance(use_scrapers, bool) and use_scrapers
    }
