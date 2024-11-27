import json
from enum import Enum
from typing import Any, Union, List
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass
from ...exceptions import ParameterError
from ...logger import logger


class ParameterType(Enum):
    """Extended parameter value types"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DOUBLE = "double"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    ARRAY = "array"

    @classmethod
    def from_value(cls, value: Any) -> 'ParameterType':
        """Determine parameter type from value"""
        if isinstance(value, bool):
            return cls.BOOLEAN
        elif isinstance(value, int):
            return cls.INTEGER
        elif isinstance(value, float):
            return cls.DOUBLE
        elif isinstance(value, Decimal):
            return cls.DECIMAL
        elif isinstance(value, list):
            return cls.ARRAY
        return cls.STRING


@dataclass
class ParameterValue:
    """Typed parameter value with extended numeric support"""
    value: Any
    type: ParameterType = None

    def __post_init__(self):
        if self.type is None:
            self.type = ParameterType.from_value(self.value)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ParameterValue):
            return self.value == other.value
        return self.value == other

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return f"ParameterValue(value={repr(self.value)}, type={self.type})"

    @classmethod
    def parse(cls, raw_value: Union[str, int, float, Decimal, bool, List]) -> 'ParameterValue':
        """Parse raw value into typed value with numeric type inference"""
        try:
            # Handle non-string values
            if not isinstance(raw_value, str):
                return cls(raw_value, ParameterType.from_value(raw_value))

            # Handle arrays
            if raw_value.startswith('[') and raw_value.endswith(']'):
                try:
                    array_value = json.loads(raw_value)
                    if not isinstance(array_value, list):
                        raise ParameterError(f"Invalid array format: {raw_value}")
                    return cls(array_value, ParameterType.ARRAY)
                except json.JSONDecodeError:
                    raise ParameterError(f"Invalid array format: {raw_value}")

            # Handle quoted strings
            if (raw_value.startswith('"') and raw_value.endswith('"')) or \
                    (raw_value.startswith("'") and raw_value.endswith("'")):
                return cls(raw_value[1:-1], ParameterType.STRING)

            # Handle boolean
            if raw_value.lower() in ('true', 'false'):
                return cls(raw_value.lower() == 'true', ParameterType.BOOLEAN)

            # Handle numbers with type suffixes
            if raw_value.endswith(('d', 'f', 'm')):
                num_val = raw_value[:-1]
                suffix = raw_value[-1].lower()
                try:
                    if suffix == 'd':
                        return cls(float(num_val), ParameterType.DOUBLE)
                    elif suffix == 'f':
                        return cls(float(num_val), ParameterType.FLOAT)
                    elif suffix == 'm':
                        return cls(Decimal(num_val), ParameterType.DECIMAL)
                except (ValueError, InvalidOperation):
                    raise ParameterError(f"Invalid numeric format: {raw_value}")

            # Handle regular numbers
            try:
                if '.' in raw_value:
                    # Default to float for floating point (not double)
                    return cls(float(raw_value), ParameterType.FLOAT)
                return cls(int(raw_value), ParameterType.INTEGER)
            except ValueError:
                return cls(raw_value, ParameterType.STRING)

        except Exception as e:
            if isinstance(e, ParameterError):
                raise
            raise ParameterError(f"Failed to parse parameter value: {str(e)}")

    def to_string(self) -> str:
        """Convert value to string representation"""
        try:
            if self.type == ParameterType.ARRAY:
                return json.dumps(self.value)
            elif self.type == ParameterType.STRING and ' ' in str(self.value):
                return f'"{self.value}"'
            elif self.type == ParameterType.DECIMAL:
                return f"{self.value}m"
            elif self.type == ParameterType.FLOAT:
                return f"{self.value}f"
            elif self.type == ParameterType.DOUBLE:
                return f"{self.value}d"
            return str(self.value)
        except Exception as e:
            logger.error(f"Parameter string conversion error: {str(e)}")
            return str(self.value)

    # def to_string(self) -> str:
    #     """Convert value back to string format"""
    #     try:
    #         if self.type == ParameterType.STRING:
    #             return f'"{self.value}"'
    #         elif self.type == ParameterType.ARRAY:
    #             items = [
    #                 ParameterValue(ParameterType.STRING, v).to_string()
    #                 if isinstance(v, str)
    #                 else str(v)
    #                 for v in self.value
    #             ]
    #             return f"[{','.join(items)}]"
    #         elif self.type == ParameterType.BOOLEAN:
    #             return str(self.value).lower()
    #         elif self.type in (ParameterType.FLOAT, ParameterType.DOUBLE):
    #             return f"{self.value}{'d' if self.type == ParameterType.DOUBLE else 'f'}"
    #         elif self.type == ParameterType.DECIMAL:
    #             return f"{self.value}m"
    #         else:
    #             return str(self.value)
    # 
    #     except Exception as e:
    #         logger.error(f"Parameter serialization error: {str(e)}",
    #                      type=self.type, value=self.value)
    #         raise ParameterError(
    #             f"Failed to convert parameter to string: {str(e)}"
    #         )
    # 
    # def __eq__(self, other: Any) -> bool:
    #     """Compare parameter values"""
    #     if isinstance(other, ParameterValue):
    #         return self.type == other.type and self.value == other.value
    #     return self.value == other
