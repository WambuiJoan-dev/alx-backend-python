#!/usr/bin/env python3
"""Unit tests for the client module functions.

This module contains unit tests for the GithubOrgClient class, using
mocking to isolate external dependencies like HTTP calls.
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from typing import Dict

# Import the class under test
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for the GithubOrgClient class.

    Verifies correct behavior for fetching organization data using mocks.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """Tests that GithubOrgClient.org returns the correct value.

        The test ensures that get_json is called exactly once with the expected
        URL for a given organization and that the org method returns the
        mocked payload.
        """
        # Define a test payload that the mock will return
        test_payload: Dict = {"login": org_name, "repos_url": "http://api.github.com/orgs/{}/repos".format(org_name)}
        mock_get_json.return_value = test_payload

        # 1. Instantiate GithubOrgClient with the parameterized org_name
        client = GithubOrgClient(org_name)

        # 2. Call the method under test
        result = client.org()

        # 3. Construct the expected URL
        expected_url = client.ORG_URL.format(org=org_name)

        # 4. Assert that get_json was called once with the expected URL
        mock_get_json.assert_called_once_with(expected_url)

        # 5. Assert that the result is the expected payload
        self.assertEqual(result, test_payload)
