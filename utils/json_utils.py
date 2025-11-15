"""Utilities for parsing JSON from LLM responses."""

import json
import re
from typing import Optional


def extract_json_object(text: str) -> Optional[dict]:
    """
    Extract a JSON object from an LLM response.

    Handles various formats:
    - Fenced code blocks (```json ... ```)
    - Plain JSON objects
    - JSON with leading/trailing commentary

    Args:
        text: Raw text from LLM response

    Returns:
        Parsed JSON dict, or None if parsing fails
    """
    if not text or not isinstance(text, str):
        return None

    json_text = None

    # Strategy 1: Try to extract from code fence (```json ... ```)
    if "```" in text:
        # Find all fenced blocks
        fence_pattern = r'```(?:json)?\s*\n(.*?)\n```'
        matches = re.findall(fence_pattern, text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            # Try to parse this block
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

    # Strategy 2: Find first complete JSON object (balanced braces)
    json_text = extract_balanced_json(text)

    if json_text:
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            pass

    # Strategy 3: Simple start/end extraction (fallback)
    start_idx = text.find('{')
    end_idx = text.rfind('}') + 1

    if start_idx != -1 and end_idx > start_idx:
        json_text = text[start_idx:end_idx]
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            pass

    return None


def extract_balanced_json(text: str) -> Optional[str]:
    """
    Extract a balanced JSON object using brace counting.

    This handles nested objects properly.

    Args:
        text: Text containing JSON

    Returns:
        Extracted JSON string, or None if not found
    """
    start_idx = text.find('{')
    if start_idx == -1:
        return None

    brace_count = 0
    in_string = False
    escape_next = False

    for i in range(start_idx, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Found complete JSON object
                    return text[start_idx:i+1]

    return None


def extract_json_array(text: str) -> Optional[list]:
    """
    Extract a JSON array from text.

    Similar to extract_json_object but for arrays.

    Args:
        text: Raw text from LLM response

    Returns:
        Parsed JSON list, or None if parsing fails
    """
    if not text or not isinstance(text, str):
        return None

    # Try fenced code blocks first
    if "```" in text:
        fence_pattern = r'```(?:json)?\s*\n(.*?)\n```'
        matches = re.findall(fence_pattern, text, re.DOTALL | re.IGNORECASE)

        for match in matches:
            try:
                result = json.loads(match.strip())
                if isinstance(result, list):
                    return result
            except json.JSONDecodeError:
                continue

    # Try balanced bracket extraction
    array_text = extract_balanced_array(text)
    if array_text:
        try:
            return json.loads(array_text)
        except json.JSONDecodeError:
            pass

    # Simple start/end extraction
    start_idx = text.find('[')
    end_idx = text.rfind(']') + 1

    if start_idx != -1 and end_idx > start_idx:
        array_text = text[start_idx:end_idx]
        try:
            return json.loads(array_text)
        except json.JSONDecodeError:
            pass

    return None


def extract_balanced_array(text: str) -> Optional[str]:
    """
    Extract a balanced JSON array using bracket counting.

    Args:
        text: Text containing JSON array

    Returns:
        Extracted JSON string, or None if not found
    """
    start_idx = text.find('[')
    if start_idx == -1:
        return None

    bracket_count = 0
    in_string = False
    escape_next = False

    for i in range(start_idx, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if not in_string:
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    return text[start_idx:i+1]

    return None


def safe_json_loads(text: str, default=None) -> any:
    """
    Safely parse JSON with a default fallback.

    Args:
        text: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError):
        return default


def validate_json_structure(data: dict, required_keys: list) -> tuple[bool, str]:
    """
    Validate that a JSON object has required keys.

    Args:
        data: Parsed JSON dict
        required_keys: List of required key names

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Data is not a dictionary"

    missing_keys = [key for key in required_keys if key not in data]

    if missing_keys:
        return False, f"Missing required keys: {', '.join(missing_keys)}"

    return True, ""
