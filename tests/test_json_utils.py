"""Unit tests for JSON parsing utilities."""

import pytest
from utils.json_utils import (
    extract_json_object,
    extract_json_array,
    extract_balanced_json,
    extract_balanced_array,
    safe_json_loads,
    validate_json_structure
)


class TestExtractJsonObject:
    """Tests for extracting JSON objects from text."""

    def test_plain_json_object(self):
        """Test extraction of plain JSON object."""
        text = '{"name": "John", "age": 30}'
        result = extract_json_object(text)
        assert result is not None
        assert result['name'] == "John"
        assert result['age'] == 30

    def test_json_with_fenced_code_block(self):
        """Test extraction from fenced code block with json marker."""
        text = """
        Here's the result:
        ```json
        {
            "title": "Software Engineer",
            "company": "Tech Corp"
        }
        ```
        """
        result = extract_json_object(text)
        assert result is not None
        assert result['title'] == "Software Engineer"
        assert result['company'] == "Tech Corp"

    def test_json_with_plain_code_fence(self):
        """Test extraction from plain code fence without language marker."""
        text = """
        ```
        {
            "status": "success",
            "count": 5
        }
        ```
        """
        result = extract_json_object(text)
        assert result is not None
        assert result['status'] == "success"
        assert result['count'] == 5

    def test_json_with_leading_commentary(self):
        """Test extraction with leading commentary text."""
        text = """
        Let me analyze this data for you.
        I found the following information:

        {"result": "positive", "score": 0.95}

        This looks good!
        """
        result = extract_json_object(text)
        assert result is not None
        assert result['result'] == "positive"
        assert result['score'] == 0.95

    def test_json_with_trailing_commentary(self):
        """Test extraction with trailing commentary text."""
        text = """
        {"errors": [], "warnings": ["minor issue"]}

        Hope this helps!
        """
        result = extract_json_object(text)
        assert result is not None
        assert result['errors'] == []
        assert result['warnings'] == ["minor issue"]

    def test_nested_json_object(self):
        """Test extraction of nested JSON object."""
        text = """
        {
            "user": {
                "name": "Alice",
                "address": {
                    "city": "Portland",
                    "state": "OR"
                }
            },
            "active": true
        }
        """
        result = extract_json_object(text)
        assert result is not None
        assert result['user']['name'] == "Alice"
        assert result['user']['address']['city'] == "Portland"
        assert result['active'] is True

    def test_json_with_escaped_quotes(self):
        """Test extraction of JSON with escaped quotes in strings."""
        text = '{"message": "She said \\"Hello\\" to me"}'
        result = extract_json_object(text)
        assert result is not None
        assert result['message'] == 'She said "Hello" to me'

    def test_multiple_json_objects_returns_first(self):
        """Test that first valid JSON object is returned when multiple exist."""
        text = """
        ```json
        {"first": 1}
        ```

        Some text here

        ```json
        {"second": 2}
        ```
        """
        result = extract_json_object(text)
        assert result is not None
        assert 'first' in result
        assert result['first'] == 1

    def test_invalid_json_returns_none(self):
        """Test that invalid JSON returns None."""
        text = '{"name": "John", age: 30}'  # Missing quotes around key
        result = extract_json_object(text)
        assert result is None

    def test_no_json_returns_none(self):
        """Test that text without JSON returns None."""
        text = "This is just plain text with no JSON at all."
        result = extract_json_object(text)
        assert result is None

    def test_empty_string_returns_none(self):
        """Test that empty string returns None."""
        result = extract_json_object("")
        assert result is None

    def test_none_input_returns_none(self):
        """Test that None input returns None."""
        result = extract_json_object(None)
        assert result is None


class TestExtractBalancedJson:
    """Tests for balanced JSON extraction."""

    def test_balanced_simple_object(self):
        """Test extraction of simple balanced object."""
        text = 'prefix {"key": "value"} suffix'
        result = extract_balanced_json(text)
        assert result == '{"key": "value"}'

    def test_balanced_nested_object(self):
        """Test extraction of nested balanced object."""
        text = 'start {"outer": {"inner": "value"}} end'
        result = extract_balanced_json(text)
        assert result == '{"outer": {"inner": "value"}}'

    def test_no_opening_brace_returns_none(self):
        """Test that text without opening brace returns None."""
        text = "No JSON here"
        result = extract_balanced_json(text)
        assert result is None

    def test_unbalanced_braces_returns_none(self):
        """Test that unbalanced braces returns None."""
        text = '{"key": "value"'  # Missing closing brace
        result = extract_balanced_json(text)
        assert result is None


class TestExtractJsonArray:
    """Tests for extracting JSON arrays from text."""

    def test_simple_array(self):
        """Test extraction of simple array."""
        text = '["apple", "banana", "cherry"]'
        result = extract_json_array(text)
        assert result is not None
        assert len(result) == 3
        assert result[0] == "apple"

    def test_array_of_objects(self):
        """Test extraction of array containing objects."""
        text = """
        [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        """
        result = extract_json_array(text)
        assert result is not None
        assert len(result) == 2
        assert result[0]['name'] == "Alice"
        assert result[1]['age'] == 25

    def test_array_in_code_fence(self):
        """Test extraction of array from code fence."""
        text = """
        ```json
        [1, 2, 3, 4, 5]
        ```
        """
        result = extract_json_array(text)
        assert result is not None
        assert result == [1, 2, 3, 4, 5]

    def test_empty_array(self):
        """Test extraction of empty array."""
        text = '[]'
        result = extract_json_array(text)
        assert result is not None
        assert result == []

    def test_no_array_returns_none(self):
        """Test that text without array returns None."""
        text = "No array here"
        result = extract_json_array(text)
        assert result is None


class TestExtractBalancedArray:
    """Tests for balanced array extraction."""

    def test_balanced_simple_array(self):
        """Test extraction of simple balanced array."""
        text = 'prefix [1, 2, 3] suffix'
        result = extract_balanced_array(text)
        assert result == '[1, 2, 3]'

    def test_balanced_nested_array(self):
        """Test extraction of nested balanced array."""
        text = 'start [[1, 2], [3, 4]] end'
        result = extract_balanced_array(text)
        assert result == '[[1, 2], [3, 4]]'

    def test_no_opening_bracket_returns_none(self):
        """Test that text without opening bracket returns None."""
        text = "No array here"
        result = extract_balanced_array(text)
        assert result is None


class TestSafeJsonLoads:
    """Tests for safe JSON loading with fallback."""

    def test_valid_json_string(self):
        """Test parsing valid JSON string."""
        result = safe_json_loads('{"key": "value"}')
        assert result == {"key": "value"}

    def test_invalid_json_returns_default(self):
        """Test that invalid JSON returns default value."""
        result = safe_json_loads('invalid json', default={})
        assert result == {}

    def test_none_input_returns_default(self):
        """Test that None input returns default value."""
        result = safe_json_loads(None, default=[])
        assert result == []

    def test_custom_default_value(self):
        """Test using custom default value."""
        custom_default = {"error": "parse_failed"}
        result = safe_json_loads('bad json', default=custom_default)
        assert result == custom_default


class TestValidateJsonStructure:
    """Tests for JSON structure validation."""

    def test_valid_structure_with_required_keys(self):
        """Test validation of structure with all required keys."""
        data = {"name": "John", "email": "john@example.com", "age": 30}
        required = ["name", "email"]
        is_valid, error = validate_json_structure(data, required)
        assert is_valid
        assert error == ""

    def test_missing_required_keys(self):
        """Test validation when required keys are missing."""
        data = {"name": "John"}
        required = ["name", "email", "phone"]
        is_valid, error = validate_json_structure(data, required)
        assert not is_valid
        assert "email" in error
        assert "phone" in error

    def test_non_dict_input(self):
        """Test validation when input is not a dictionary."""
        data = ["not", "a", "dict"]
        required = ["key"]
        is_valid, error = validate_json_structure(data, required)
        assert not is_valid
        assert "not a dictionary" in error.lower()

    def test_empty_required_keys(self):
        """Test validation with no required keys."""
        data = {"any": "data"}
        required = []
        is_valid, error = validate_json_structure(data, required)
        assert is_valid
        assert error == ""
