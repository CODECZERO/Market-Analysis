"""
Performance utilities for JSON serialization and response optimization
"""

import json
from typing import Any, Dict, Union

# Try to use orjson for better performance
try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False


def fast_json_dumps(obj: Any) -> str:
    """
    Fast JSON serialization.
    
    ⚡ PERFORMANCE: Uses orjson if available (2-3x faster than standard json)
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON string
    """
    if HAS_ORJSON:
        # orjson returns bytes, decode to string
        return orjson.dumps(obj).decode('utf-8')
    else:
        return json.dumps(obj)


def fast_json_loads(s: Union[str, bytes]) -> Any:
    """
    Fast JSON deserialization.
    
    ⚡ PERFORMANCE: Uses orjson if available
    
    Args:
        s: JSON string or bytes
        
    Returns:
        Deserialized object
    """
    if HAS_ORJSON:
        if isinstance(s, str):
            s = s.encode('utf-8')
        return orjson.loads(s)
    else:
        if isinstance(s, bytes):
            s = s.decode('utf-8')
        return json.loads(s)


def get_json_library() -> str:
    """Get which JSON library is being used"""
    return "orjson (fast)" if HAS_ORJSON else "json (standard)"
