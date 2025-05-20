import pytest
import flextag
from typing import Any, Dict


# Helper functions to create a FlexView with a single section containing parameters
def create_view_with_params(params_str: str) -> flextag.FlexView:
    config = f"""
    [[{params_str}]]: ftml
    content = "Test content"
    [[/]]
    """
    return flextag.load(string=config)


# Helper to get parameters from the first section
def get_params(view: flextag.FlexView) -> Dict[str, Any]:
    return view.sections[0].parameters


class TestAutomaticTypeInference:
    """Tests for automatic type inference (existing functionality)"""

    def test_string_parameter(self):
        view = create_view_with_params('param="hello world"')
        params = get_params(view)

        assert "param" in params
        assert params["param"] == "hello world"
        assert isinstance(params["param"], str)

    def test_integer_parameter(self):
        view = create_view_with_params("param=42")
        params = get_params(view)

        assert "param" in params
        assert params["param"] == 42
        assert isinstance(params["param"], int)

    def test_float_parameter(self):
        view = create_view_with_params("param=3.14")
        params = get_params(view)

        assert "param" in params
        assert params["param"] == 3.14
        assert isinstance(params["param"], float)

    def test_boolean_parameter_true(self):
        view = create_view_with_params("param=true")
        params = get_params(view)

        assert "param" in params
        assert params["param"] is True
        assert isinstance(params["param"], bool)

    def test_boolean_parameter_false(self):
        view = create_view_with_params("param=false")
        params = get_params(view)

        assert "param" in params
        assert params["param"] is False
        assert isinstance(params["param"], bool)

    def test_null_parameter(self):
        view = create_view_with_params("param=null")
        params = get_params(view)

        assert "param" in params
        assert params["param"] is None

    def test_multiple_parameters(self):
        view = create_view_with_params(
            'str_param="text" int_param=42 float_param=3.14 bool_param=true null_param=null'
        )
        params = get_params(view)

        assert params["str_param"] == "text"
        assert params["int_param"] == 42
        assert params["float_param"] == 3.14
        assert params["bool_param"] is True
        assert params["null_param"] is None


class TestExplicitTypeAnnotations:
    """Tests for explicit type annotations (new functionality)"""

    def test_string_type_annotation(self):
        view = create_view_with_params('param:str="hello"')
        params = get_params(view)

        assert "param" in params
        assert params["param"] == "hello"
        assert isinstance(params["param"], str)

    def test_string_type_with_numeric_value(self):
        view = create_view_with_params("param:str=123")
        params = get_params(view)

        assert "param" in params
        assert params["param"] == "123"
        assert isinstance(params["param"], str)

    def test_int_type_annotation(self):
        view = create_view_with_params("param:int=42")
        params = get_params(view)

        assert "param" in params
        assert params["param"] == 42
        assert isinstance(params["param"], int)

    def test_int_type_with_numeric_string(self):
        view = create_view_with_params('param:int="42"')
        params = get_params(view)

        assert "param" in params
        assert params["param"] == 42
        assert isinstance(params["param"], int)

    def test_float_type_annotation(self):
        view = create_view_with_params("param:float=3.14")
        params = get_params(view)

        assert "param" in params
        assert params["param"] == 3.14
        assert isinstance(params["param"], float)

    def test_float_type_with_integer_value(self):
        view = create_view_with_params("param:float=42")
        params = get_params(view)

        assert "param" in params
        assert params["param"] == 42.0
        assert isinstance(params["param"], float)

    def test_bool_type_annotation_true(self):
        view = create_view_with_params("param:bool=true")
        params = get_params(view)

        assert "param" in params
        assert params["param"] is True
        assert isinstance(params["param"], bool)

    def test_bool_type_annotation_false(self):
        view = create_view_with_params("param:bool=false")
        params = get_params(view)

        assert "param" in params
        assert params["param"] is False
        assert isinstance(params["param"], bool)

    def test_null_type_annotation(self):
        view = create_view_with_params("param:null=null")
        params = get_params(view)

        assert "param" in params
        assert params["param"] is None


class TestNullableTypes:
    """Tests for nullable type annotations"""

    def test_nullable_string_with_value(self):
        view = create_view_with_params('param:str?="hello"')
        params = get_params(view)

        assert "param" in params
        assert params["param"] == "hello"
        assert isinstance(params["param"], str)

    def test_nullable_string_with_null(self):
        view = create_view_with_params("param:str?=null")
        params = get_params(view)

        assert "param" in params
        assert params["param"] is None

    def test_nullable_int_with_value(self):
        view = create_view_with_params("param:int?=42")
        params = get_params(view)

        assert "param" in params
        assert params["param"] == 42
        assert isinstance(params["param"], int)

    def test_nullable_int_with_null(self):
        view = create_view_with_params("param:int?=null")
        params = get_params(view)

        assert "param" in params
        assert params["param"] is None

    def test_multiple_nullable_parameters(self):
        view = create_view_with_params(
            'str_param:str?="text" int_param:int?=null float_param:float?=3.14'
        )
        params = get_params(view)

        assert params["str_param"] == "text"
        assert params["int_param"] is None
        assert params["float_param"] == 3.14


class TestErrorCases:
    """Tests for error cases and invalid conversions"""

    def test_invalid_int_conversion(self):
        with pytest.raises(Exception) as excinfo:
            create_view_with_params('param:int="hello"')
        assert "Cannot convert" in str(excinfo.value) or "ValueError" in str(
            excinfo.value
        )

    def test_invalid_float_conversion(self):
        with pytest.raises(Exception) as excinfo:
            create_view_with_params('param:float="world"')
        assert "Cannot convert" in str(excinfo.value) or "ValueError" in str(
            excinfo.value
        )

    def test_invalid_bool_value(self):
        with pytest.raises(Exception) as excinfo:
            create_view_with_params("param:bool=42")
        assert "Boolean value must be" in str(excinfo.value) or "ValueError" in str(
            excinfo.value
        )

    def test_invalid_null_value(self):
        with pytest.raises(Exception) as excinfo:
            create_view_with_params('param:null="not null"')
        assert "Null value must be" in str(excinfo.value) or "ValueError" in str(
            excinfo.value
        )

    def test_non_nullable_with_null(self):
        with pytest.raises(Exception) as excinfo:
            create_view_with_params("param:int=null")
        assert "Cannot convert" in str(excinfo.value) or "ValueError" in str(
            excinfo.value
        )


class TestAliasedTypes:
    """Tests for type name aliases"""

    def test_string_alias(self):
        view = create_view_with_params('param:string="hello"')
        params = get_params(view)

        assert "param" in params
        assert params["param"] == "hello"
        assert isinstance(params["param"], str)

    def test_integer_alias(self):
        view = create_view_with_params("param:integer=42")
        params = get_params(view)

        assert "param" in params
        assert params["param"] == 42
        assert isinstance(params["param"], int)


class TestEdgeCases:
    """Tests for edge cases"""

    def test_empty_string(self):
        view = create_view_with_params('param:str=""')
        params = get_params(view)

        assert "param" in params
        assert params["param"] == ""
        assert isinstance(params["param"], str)

    def test_zero_value(self):
        view = create_view_with_params("param:int=0")
        params = get_params(view)

        assert "param" in params
        assert params["param"] == 0
        assert isinstance(params["param"], int)

    def test_case_insensitive_type(self):
        view = create_view_with_params("param:INT=42")
        params = get_params(view)

        assert "param" in params
        assert params["param"] == 42
        assert isinstance(params["param"], int)

    def test_case_insensitive_bool_values(self):
        view = create_view_with_params("param1:bool=TRUE param2:bool=False")
        params = get_params(view)

        assert params["param1"] is True
        assert params["param2"] is False


if __name__ == "__main__":
    # This allows running the tests directly with python
    pytest.main(["-v", __file__])
