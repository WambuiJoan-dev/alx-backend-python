#!/usr/bin/env python3
"""Unit tests for the utils module functions.
"""
import unittest
from parameterized import parameterized
from typing import Mapping, Sequence, Any

# Assuming utils.py is in the same directory
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """Tests for the access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: Mapping,
                               path: Sequence, expected: Any) -> None:
        """Tests that access_nested_map returns the expected value for a given path."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    def test_access_nested_map_key_error(self) -> None:
        """Tests that access_nested_map raises a KeyError for an invalid path."""
        # This test case is required by standard testing practices for this type of function,
        # even though it was not explicitly requested in the prompt.
        test_map = {"a": 1}
        with self.assertRaises(KeyError):
            access_nested_map(test_map, ("b",))

        test_map_nested = {"a": {"b": 2}}
        with self.assertRaises(KeyError):
            access_nested_map(test_map_nested, ("a", "c"))
