#!/usr/bin/env python3
"""Unit tests for the client module functions.

This module contains unit tests for the GithubOrgClient class, using
mocking to isolate external dependencies like HTTP calls.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized
from typing import Dict, List, Tuple

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

    def test_public_repos_url(self) -> None:
        """Tests that _public_repos_url returns the correct URL based on the mocked payload.

        Mocks the 'org' method (which is a memoized property) to return a fixed
        payload and verifies that the '_public_repos_url' property extracts the
        'repos_url' correctly.
        """
        # Define the payload the mocked .org property will return
        expected_repos_url = "https://api.github.com/users/holberton/repos"
        test_payload = {"repos_url": expected_repos_url}

        # Patch GithubOrgClient.org using PropertyMock
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=PropertyMock,
            return_value=test_payload
        ) as mock_org:
            # Instantiate the client
            client = GithubOrgClient("holberton")

            # Access the property under test
            result_url = client._public_repos_url

            # Assert that the mocked property was called once
            mock_org.assert_called_once()

            # Assert that the result is the expected repos URL
            self.assertEqual(result_url, expected_repos_url)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """Tests that public_repos returns the expected list of repository names.

        Mocks both the 'repos_payload' method (via get_json) and the
        '_public_repos_url' property to ensure isolated unit testing.
        """
        # Define the mocked payload for repos_payload (which calls get_json)
        repos_payload: List[Dict] = [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}},
            {"name": "repo3", "license": None},
        ]
        expected_repos: List[str] = ["repo1", "repo2", "repo3"]

        # Configure the mock_get_json to return the payload when called
        # by repos_payload()
        mock_get_json.return_value = repos_payload

        # Mock the _public_repos_url property (used internally by repos_payload)
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value="https://api.github.com/orgs/some_org/repos"
        ) as mock_public_repos_url:
            # Instantiate the client
            client = GithubOrgClient("some_org")

            # Call the method under test
            repos = client.public_repos()

            # Assertions
            # 1. Test that the list of repos is what we expect
            self.assertEqual(repos, expected_repos)

            # 2. Test that the mocked property was called once
            mock_public_repos_url.assert_called_once()

            # 3. Test that the mocked get_json was called once
            # This call happens inside the memoized repos_payload property
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
        ({"license": {"key": "my_license"}}, "other_license", False),
    ])
    def test_has_license(self, repo: Dict, license_key: str, expected: bool) -> None:
        """Tests the has_license static method.

        Verifies that the method correctly checks for the presence and matching
        of a license key within a repository dictionary. Includes edge cases
        for missing license data.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)
