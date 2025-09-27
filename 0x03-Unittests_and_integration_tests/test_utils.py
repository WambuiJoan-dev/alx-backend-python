#!/usr/bin/env python3
"""Unit tests for the utils module functions.

This module contains the TestAccessNestedMap class for testing the
access_nested_map utility function.
"""
import unittest
from parameterized import parameterized
from typing import Mapping, Sequence, Any

# Assuming utils.py is in the same directory
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """Tests for the access_nested_map function.

    This class contains unit tests designed to verify the correct behavior
    of the utils.access_nested_map function, including successful access
    and proper exception handling for invalid paths.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: Mapping,
                               path: Sequence, expected: Any) -> None:
        """Tests that access_nested_map returns the expected value for a valid path."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map: Mapping,
                                         path: Sequence, expected_key: str) -> None:
        """Tests that access_nested_map raises a KeyError with the expected key.

        Verifies that when an invalid key is accessed, a KeyError is raised,
        and the message of the exception is the missing key.
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)

        # KeyError is raised with the failing key as the only argument
        self.assertEqual(context.exception.args[0], expected_key)
