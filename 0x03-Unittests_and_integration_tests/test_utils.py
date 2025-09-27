#!/usr/bin/env python3
"""Unit tests for the utils module functions.

This module contains unit tests for utility functions including
access_nested_map and get_json, leveraging unittest.mock for isolation.
"""
import unittest
from parameterized import parameterized
from typing import Mapping, Sequence, Any, Dict
from unittest.mock import patch, Mock

# Assuming utils.py is in the same directory
from utils import access_nested_map, get_json


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


class TestGetJson(unittest.TestCase):
    """Tests for the get_json function.

    This class contains unit tests designed to verify the correct behavior
    of the utils.get_json function by mocking external HTTP calls.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url: str, test_payload: Dict,
                       mock_get: Mock) -> None:
        """Tests that get_json returns the expected payload without making external calls.

        It mocks the requests.get method to control its return value, ensuring
        that the function handles the mock response correctly.
        """
        # Configure the Mock object returned by the patched requests.get
        # to have a .json() method that returns the test_payload.
        mock_get.return_value.json.return_value = test_payload

        # Call the function under test
        result = get_json(test_url)

        # Test 1: Assert the mocked get method was called exactly once with the correct URL
        mock_get.assert_called_once_with(test_url)

        # Test 2: Assert the output of get_json is equal to the expected payload
        self.assertEqual(result, test_payload)
