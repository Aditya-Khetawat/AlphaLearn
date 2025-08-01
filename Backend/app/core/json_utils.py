import json
import math
from typing import Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class SafeJSONResponse(JSONResponse):
    """Custom JSON response that safely handles NaN and infinity values"""
    
    def render(self, content: Any) -> bytes:
        """Override render to safely serialize content with NaN handling"""
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,  # This will prevent NaN serialization
            indent=None,
            separators=(",", ":"),
            default=self.safe_json_default,
        ).encode("utf-8")
    
    @staticmethod
    def safe_json_default(obj):
        """Handle objects that aren't JSON serializable"""
        if isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return 0.0
        return obj


def safe_jsonable_encoder(obj: Any) -> Any:
    """Safe JSON encoder that converts NaN and inf to safe values"""
    def clean_value(value):
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return 0.0
        elif isinstance(value, dict):
            return {k: clean_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [clean_value(item) for item in value]
        return value
    
    return clean_value(jsonable_encoder(obj))
