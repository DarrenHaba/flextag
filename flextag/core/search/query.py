from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import re
from flextag.core.interfaces.search import ISearchQuery
from flextag.core.types.metadata import Metadata
from flextag.core.types.parameter import ParameterValue, ParameterType
from flextag.exceptions import SearchError
from flextag.logger import logger


class TokenType(Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    IN = "IN"
    NOT_IN = "NOT IN"
    LPAREN = "("
    RPAREN = ")"
    TERM = "TERM"

    @classmethod
    def value_of(cls, value: str) -> 'TokenType':
        try:
            return cls[value]
        except KeyError:
            raise SearchError(f"Invalid token type: {value}")


class ComparisonOperator(Enum):
    EQ = "="
    NEQ = "!="
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    IN = "IN"
    NOT_IN = "NOT IN"


@dataclass
class Token:
    type: TokenType
    value: str
    operator: Optional[ComparisonOperator] = None
    comparison_value: Any = None


class BooleanNode:
    def __init__(self, type: TokenType, value: Optional[str] = None,
                 operator: Optional[ComparisonOperator] = None,
                 comparison_value: Any = None):
        self.type = type
        self.value = value
        self.operator = operator
        self.comparison_value = comparison_value
        self.left: Optional['BooleanNode'] = None
        self.right: Optional['BooleanNode'] = None


class QueryParser:
    """Parser for search queries"""

    def _parse_parameter_value(self, value: str) -> Tuple[Any, bool]:
        """Parse parameter value and determine its type"""
        value = value.strip()

        # Handle arrays
        if value.startswith('[') and value.endswith(']'):
            try:
                # Parse array items
                items = [i.strip().strip("\"'") for i in value[1:-1].split(',')]
                return items, False
            except Exception:
                raise SearchError(f"Invalid array format: {value}")

        # Handle quoted strings
        if (value.startswith('"') and value.endswith('"')) or \
                (value.startswith("'") and value.endswith("'")):
            return value[1:-1], False

        # Handle boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true', False

        # Handle numbers
        try:
            if '.' in value:
                return float(value), False
            return int(value), False
        except ValueError:
            # Check for wildcards
            has_wildcards = '*' in value or '?' in value
            return value, has_wildcards

    def _parse_parameter(self, term: str) -> Tuple[str, ComparisonOperator, Any]:
        """Parse parameter term into key, operator, and value"""
        # First check for array operations
        array_match = re.match(r'(\w+)\s+(NOT\s+)?IN\s+(\[.+])', term, re.IGNORECASE)
        if array_match:
            key = array_match.group(1)
            is_not = array_match.group(2) is not None
            array_value = array_match.group(3)
            value, _ = self._parse_parameter_value(array_value)
            return key, ComparisonOperator.NOT_IN if is_not else ComparisonOperator.IN, value

        # Then check other operators
        op_match = re.match(r'(\w+)\s*(>=|<=|!=|>|<|=)\s*(.+)', term)  # Added != operator
        if not op_match:
            raise SearchError(f"Invalid parameter format: {term}")

        key, op_str, value = op_match.groups()

        # Map operator strings to enum
        op_map = {
            ">=": ComparisonOperator.GTE,
            "<=": ComparisonOperator.LTE,
            ">": ComparisonOperator.GT,
            "<": ComparisonOperator.LT,
            "=": ComparisonOperator.EQ,
            "!=": ComparisonOperator.NEQ  # Add new operator
        }
        operator = op_map.get(op_str)
        if not operator:
            raise SearchError(f"Invalid operator: {op_str}")

        parsed_value, has_wildcards = self._parse_parameter_value(value)

        # Validate operator and value type combinations
        if has_wildcards and operator != ComparisonOperator.EQ:
            raise SearchError("Wildcards only supported with = operator")

        return key, operator, parsed_value

    def tokenize(self, query: str) -> List[Token]:
        """Convert query string into tokens with proper grouping"""
        parts = []
        current = ''
        in_quotes = False
        quote_char = None
        in_array = False
        array_depth = 0

        # First separate into basic parts while preserving quotes and arrays
        for char in query:
            if char in '"\'':
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif quote_char == char:
                    in_quotes = False
                current += char
            elif char == '[':
                in_array = True
                array_depth += 1
                current += char
            elif char == ']':
                array_depth -= 1
                in_array = array_depth > 0
                current += char
            elif char in '()' and not (in_quotes or in_array):
                if current:
                    parts.append(current)
                    current = ''
                parts.append(char)
            elif char.isspace() and not (in_quotes or in_array):
                if current:
                    parts.append(current)
                    current = ''
            else:
                current += char

        if current:
            parts.append(current)

        tokens = []
        i = 0
        while i < len(parts):
            part = parts[i].strip()

            if part in "()":
                tokens.append(Token(
                    TokenType.LPAREN if part == '(' else TokenType.RPAREN,
                    part
                ))
            elif part.upper() == "IN" and i + 1 < len(parts):
                # Handle IN operator
                key = parts[i-1]  # Previous token should be the key
                value = parts[i+1]  # Next token should be the array
                if tokens and tokens[-1].type == TokenType.TERM:
                    tokens.pop()  # Remove the key token
                    key, operator, comp_value = self._parse_parameter(f"{key} IN {value}")
                    tokens.append(Token(
                        TokenType.TERM,
                        f"{key}={comp_value}",
                        operator=operator,
                        comparison_value=comp_value
                    ))
                    i += 1  # Skip the array value
            elif part.upper() == "NOT" and i + 2 < len(parts) and parts[i+1].upper() == "IN":
                # Handle NOT IN operator
                key = parts[i-1]
                value = parts[i+2]
                if tokens and tokens[-1].type == TokenType.TERM:
                    tokens.pop()
                    key, operator, comp_value = self._parse_parameter(f"{key} NOT IN {value}")
                    tokens.append(Token(
                        TokenType.TERM,
                        f"{key}={comp_value}",
                        operator=operator,
                        comparison_value=comp_value
                    ))
                    i += 2
            elif part.upper() in ("AND", "OR", "NOT"):
                tokens.append(Token(TokenType.value_of(part.upper()), part.upper()))
            elif "=" in part or ">" in part or "<" in part:
                try:
                    key, operator, value = self._parse_parameter(part)
                    tokens.append(Token(
                        TokenType.TERM,
                        f"{key}={value}",
                        operator=operator,
                        comparison_value=value
                    ))
                except SearchError as e:
                    # Skip invalid parameters in complex expressions
                    if not ("(" in part or ")" in part):
                        raise
                    tokens.append(Token(TokenType.TERM, part))
            else:
                tokens.append(Token(TokenType.TERM, part))
            i += 1

        return tokens

    def parse(self, tokens: List[Token]) -> Tuple[BooleanNode, int]:
        """Parse tokens into a boolean expression tree"""
        if not tokens:
            return BooleanNode(TokenType.TERM, ""), 0
        return self._parse_expression(tokens, 0)

    def _parse_expression(self, tokens: List[Token], index: int) -> Tuple[BooleanNode, int]:
        """Parse expression recursively"""
        if index >= len(tokens):
            return BooleanNode(TokenType.TERM, ""), index

        left: Optional[BooleanNode] = None

        # Handle NOT operator
        if tokens[index].type == TokenType.NOT:
            node = BooleanNode(TokenType.NOT)
            right, next_index = self._parse_expression(tokens, index + 1)
            node.right = right
            return node, next_index

        # Handle parentheses
        if tokens[index].type == TokenType.LPAREN:
            left, index = self._parse_expression(tokens, index + 1)
            if index >= len(tokens) or tokens[index].type != TokenType.RPAREN:
                raise SearchError("Mismatched parentheses")
            index += 1
        else:
            # Handle term
            if tokens[index].type == TokenType.TERM:
                left = BooleanNode(
                    TokenType.TERM,
                    tokens[index].value,
                    tokens[index].operator,
                    tokens[index].comparison_value
                )
                index += 1

        while index < len(tokens) and tokens[index].type in (TokenType.AND, TokenType.OR):
            operator = tokens[index].type
            node = BooleanNode(operator)
            node.left = left
            right, next_index = self._parse_expression(tokens, index + 1)
            node.right = right
            left = node
            index = next_index

        return left or BooleanNode(TokenType.TERM, ""), index


@dataclass
class SearchQuery(ISearchQuery):
    """Enhanced search query with boolean logic support"""
    raw_query: str
    expression_tree: Optional[BooleanNode] = None
    parameters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        parser = QueryParser()
        tokens = parser.tokenize(self.raw_query)
        self.expression_tree, _ = parser.parse(tokens)
        self._extract_parameters()
        self._numeric_types = (ParameterType.INTEGER, ParameterType.FLOAT,
                               ParameterType.DOUBLE, ParameterType.DECIMAL)

    def _validate_types(self, param_value: ParameterValue, comp_value: Any, operator: Optional[ComparisonOperator]) -> None:
        """Validate type compatibility with strict checking"""
        operator = operator or ComparisonOperator.EQ

        # Array type validation
        if param_value.type == ParameterType.ARRAY:
            if operator not in (ComparisonOperator.IN, ComparisonOperator.NOT_IN, ComparisonOperator.EQ):
                raise SearchError("Arrays only support IN, NOT IN, and = operators")
            # Ensure comp_value is a list for IN/NOT IN operations
            if operator in (ComparisonOperator.IN, ComparisonOperator.NOT_IN):
                if not isinstance(comp_value, list):
                    raise SearchError("IN/NOT IN operations require array values")
            # For equality, non-array values should raise an error
            elif isinstance(comp_value, (int, float, str, bool)):
                raise SearchError("Cannot compare array with non-array value")

        # Numeric comparisons
        if operator in (ComparisonOperator.GT, ComparisonOperator.LT,
                        ComparisonOperator.GTE, ComparisonOperator.LTE):
            if param_value.type not in self._numeric_types:
                raise SearchError(f"Cannot use comparison operators with {param_value.type}")
            if not isinstance(comp_value, (int, float, Decimal)):
                raise SearchError("Comparison value must be numeric")

        # Handle equality and inequality
        if operator in (ComparisonOperator.EQ, ComparisonOperator.NEQ):
            if param_value.type in self._numeric_types:
                if isinstance(comp_value, bool):
                    raise SearchError("Cannot compare numeric with boolean value")
                try:
                    float(comp_value) if isinstance(comp_value, str) else comp_value
                except (ValueError, TypeError):
                    raise SearchError("Cannot compare numeric with non-numeric value")

            elif param_value.type == ParameterType.BOOLEAN:
                if not isinstance(comp_value, bool) and not (
                        isinstance(comp_value, str) and comp_value.lower() in ('true', 'false')):
                    raise SearchError("Cannot compare boolean with non-boolean value")

    # def _wildcard_match(self, pattern: str, value: str) -> bool:
    #     """Enhanced wildcard matching using regex with case sensitivity"""
    #     try:
    #         # Convert pattern to regex
    #         regex_pattern = []
    #         i = 0
    #         while i < len(pattern):
    #             if pattern[i] == '*':
    #                 regex_pattern.append('.*')
    #             elif pattern[i] == '?':
    #                 regex_pattern.append('.')
    #             elif pattern[i] == '[':
    #                 end = pattern.find(']', i)
    #                 if end == -1:
    #                     raise SearchError("Unmatched bracket")
    # 
    #                 # Get the content between brackets
    #                 class_content = pattern[i+1:end]
    #                 if class_content.startswith('!') or class_content.startswith('^'):
    #                     # Handle negated character class
    #                     class_content = '^' + class_content[1:]
    # 
    #                 # Preserve case sensitivity for ranges
    #                 regex_pattern.append(f'[{class_content}]')
    #                 i = end
    #             else:
    #                 regex_pattern.append(re.escape(pattern[i]))
    #             i += 1
    # 
    #         final_pattern = f'^{"".join(regex_pattern)}$'
    #         print(f"Debug - Regex pattern: {final_pattern}")  # Debug print
    #         print(f"Debug - Matching value: {value}")  # Debug print
    # 
    #         result = bool(re.match(final_pattern, value))
    #         print(f"Debug - Match result: {result}")  # Debug print
    #         return result
    # 
    #     except Exception as e:
    #         logger.error(f"Wildcard match error: {str(e)}")
    #         return False

    def _extract_parameters(self) -> None:
        """Extract parameters from terms in expression tree"""
        def visit(node: Optional[BooleanNode]) -> None:
            if not node:
                return
            if node.type == TokenType.TERM and node.value and "=" in node.value:
                key, value = node.value.split("=", 1)
                self.parameters[key.strip()] = value.strip().strip("\"'")
            visit(node.left)
            visit(node.right)
        visit(self.expression_tree)

    def evaluate(self, metadata: Metadata) -> bool:
        """Evaluate with strict type checking"""
        def eval_node(node: Optional[BooleanNode]) -> bool:
            if not node:
                return True
    
            if node.type == TokenType.AND:
                return eval_node(node.left) and eval_node(node.right)
            elif node.type == TokenType.OR:
                return eval_node(node.left) or eval_node(node.right)
            elif node.type == TokenType.NOT:
                return not eval_node(node.right)
            elif node.type == TokenType.TERM:
                # Handle special prefixes
                if node.value.startswith(':'):
                    return metadata.id == node.value[1:]
                elif node.value.startswith('#'):
                    return node.value[1:] in metadata.tags
                elif node.value.startswith('.'):
                    return node.value[1:] in metadata.paths
    
                # Handle parameters
                key = node.value.split('=')[0].strip()
                if key not in metadata.parameters:
                    return False
    
                param_value = metadata.parameters[key]
                comp_value = node.comparison_value
    
                # Validate types before comparison
                self._validate_types(param_value, comp_value, node.operator)

                # Handle type-specific comparisons
                if param_value.type in self._numeric_types:
                    if node.operator == ComparisonOperator.NEQ:
                        return param_value.value != comp_value
                
                # Type-specific comparisons
                if param_value.type == ParameterType.BOOLEAN:
                    if isinstance(comp_value, str):
                        comp_value = comp_value.lower() == 'true'
                    return param_value.value == comp_value
    
                elif param_value.type == ParameterType.ARRAY:
                    if node.operator == ComparisonOperator.IN:
                        return any(v in param_value.value for v in comp_value)
                    elif node.operator == ComparisonOperator.NOT_IN:
                        return not any(v in param_value.value for v in comp_value)
                    return param_value.value == comp_value
    
                # Handle all numeric types
                elif param_value.type in (ParameterType.INTEGER, ParameterType.FLOAT,
                                          ParameterType.DOUBLE, ParameterType.DECIMAL):
                    if node.operator == ComparisonOperator.GT:
                        return param_value.value > comp_value
                    elif node.operator == ComparisonOperator.LT:
                        return param_value.value < comp_value
                    elif node.operator == ComparisonOperator.GTE:
                        return param_value.value >= comp_value
                    elif node.operator == ComparisonOperator.LTE:
                        return param_value.value <= comp_value
                    return param_value.value == comp_value
    
                elif param_value.type == ParameterType.STRING:
                    if node.operator and node.operator != ComparisonOperator.EQ:
                        raise SearchError(f"String values don't support {node.operator} operator")
                    if isinstance(comp_value, str) and ('*' in comp_value or '?' in comp_value):
                        return self._wildcard_match(comp_value, str(param_value.value))
                    return param_value.value == comp_value

                elif param_value.type == ParameterType.STRING:
                    if node.operator == ComparisonOperator.NEQ:
                        return param_value.value != comp_value
    
                return False
            return False
    
        try:
            return eval_node(self.expression_tree)
        except Exception as e:
            logger.error(f"Evaluation error: {str(e)}")
            raise SearchError(f"Failed to evaluate query: {str(e)}")

    def has_wildcards(self) -> bool:
        """Check if query contains wildcards"""
        def check_node(node: Optional[BooleanNode]) -> bool:
            if not node:
                return False
            if node.type == TokenType.TERM and node.value:
                return "*" in node.value or "?" in node.value
            return check_node(node.left) or check_node(node.right)
        return check_node(self.expression_tree)

    def get_tags(self) -> List[str]:
        tags = []
        def collect_tags(node: Optional[BooleanNode]) -> None:
            if not node:
                return
            if node.type == TokenType.TERM and node.value and node.value.startswith('#'):
                tags.append(node.value[1:])
            collect_tags(node.left)
            collect_tags(node.right)
        collect_tags(self.expression_tree)
        return tags

    def get_paths(self) -> List[str]:
        paths = []
        def collect_paths(node: Optional[BooleanNode]) -> None:
            if not node:
                return
            if node.type == TokenType.TERM and node.value and node.value.startswith('.'):
                paths.append(node.value[1:])
            collect_paths(node.left)
            collect_paths(node.right)
        collect_paths(self.expression_tree)
        return paths

    def get_id(self) -> Optional[str]:
        def find_id(node: Optional[BooleanNode]) -> Optional[str]:
            if not node:
                return None
            if node.type == TokenType.TERM and node.value and node.value.startswith(':'):
                return node.value[1:]
            left_id = find_id(node.left)
            if left_id:
                return left_id
            return find_id(node.right)
        return find_id(self.expression_tree)

    def get_parameters(self) -> Dict[str, Any]:
        return self.parameters

    def get_operators(self) -> List[str]:
        operators = []
        def collect_operators(node: Optional[BooleanNode]) -> None:
            if not node:
                return
            if node.type in (TokenType.AND, TokenType.OR, TokenType.NOT):
                operators.append(node.type.value)
            collect_operators(node.left)
            collect_operators(node.right)
        collect_operators(self.expression_tree)
        return operators
