"""Tests for the LLM client JSON parsing utility."""

import json
import pytest

from app.core.llm_client import parse_llm_json


class TestParseLlmJson:
    def test_plain_json(self) -> None:
        data = parse_llm_json('{"key": "value"}')
        assert data == {"key": "value"}

    def test_json_in_code_fence(self) -> None:
        text = '```json\n{"key": "value"}\n```'
        data = parse_llm_json(text)
        assert data == {"key": "value"}

    def test_json_in_code_fence_no_lang(self) -> None:
        text = '```\n{"key": "value"}\n```'
        data = parse_llm_json(text)
        assert data == {"key": "value"}

    def test_json_with_surrounding_text(self) -> None:
        text = 'Here is the result:\n{"key": "value"}\nThat is all.'
        data = parse_llm_json(text)
        assert data == {"key": "value"}

    def test_nested_json(self) -> None:
        obj = {"a": {"b": [1, 2, 3]}, "c": "d"}
        text = f"```json\n{json.dumps(obj)}\n```"
        data = parse_llm_json(text)
        assert data == obj

    def test_invalid_json_raises(self) -> None:
        with pytest.raises((json.JSONDecodeError, ValueError)):
            parse_llm_json("this is not json at all")
