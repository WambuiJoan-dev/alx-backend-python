#!/usr/bin/env python3
"""Unit tests and integration tests for the client module functions.

This module contains unit tests for the GithubOrgClient class, using
mocking to isolate external dependencies like HTTP calls.
"""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
from typing import Dict, List, Tuple

# Import the class under test and fixtures
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Tests for the GithubOrgClient class methods.

    Verifies correct behavior for fetching organization data using mocks.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, mock_get_json: Mock) -> None:
        """Tests that GithubOrgClient.org returns the correct value.

        Ensures get_json is called once with the expected URL and returns
        the mocked payload.
        """
        # Define a test payload that the mock will return
        test_payload: Dict = {"login": org_name,
                              "repos_url": "http://api.github.com/orgs/{}/repos".format(org_name)}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient(org_name)
        result = client.org()
        expected_url = client.ORG_URL.format(org=org_name)

        # Assertions
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self) -> None:
        """Tests that _public_repos_url returns the correct URL.

        Mocks the 'org' memoized property to return a fixed payload and
        verifies that the '_public_repos_url' property extracts the 'repos_url'.
        """
        # Define the payload the mocked .org property will return
        expected_repos_url = "https://api.github.com/users/holberton/repos"
        test_payload = {"repos_url": expected_repos_url}

        # Patch GithubOrgClient.org using PropertyMock as a context manager
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=PropertyMock,
            return_value=test_payload
        ) as mock_org:
            client = GithubOrgClient("holberton")
            result_url = client._public_repos_url

            # Assertions
            mock_org.assert_called_once()
            self.assertEqual(result_url, expected_repos_url)

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """Tests that public_repos returns the expected list of repository names.

        Mocks 'get_json' to return the list of repos and mocks
        '_public_repos_url' to avoid calling the 'org' property unnecessarily.
        """
        # Define the mocked payload for repos_payload (which calls get_json)
        repos_payload: List[Dict] = [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}},
            {"name": "repo3", "license": None},
        ]
        expected_repos: List[str] = ["repo1", "repo2", "repo3"]
        mock_get_json.return_value = repos_payload

        # Mock the _public_repos_url property (used internally)
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value="https://api.github.com/orgs/some_org/repos"
        ) as mock_public_repos_url:
            client = GithubOrgClient("some_org")
            repos = client.public_repos()

            # Assertions
            self.assertEqual(repos, expected_repos)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
        ({"license": {"key": "my_license"}}, "other_license", False),
    ])
    def test_has_license(self, repo: Dict, license_key: str, expected: bool) -> None:
        """Tests the has_license static method with various license scenarios."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos.

    Mocks external requests.get to test the full data flow using fixtures.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up the class-level mock for requests.get."""
        
        def side_effect(url: str) -> Mock:
            """Mocks the response based on the requested URL."""
            mock_resp = Mock()
            if url == "https://api.github.com/orgs/google":
                mock_resp.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/google/repos":
                mock_resp.json.return_value = cls.repos_payload
            else:
                # Should not happen in this test case
                mock_resp.json.return_value = {}
            return mock_resp

        # Start the patcher for requests.get
        cls.get_patcher = patch('requests.get', side_effect=side_effect)
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """Stops the class-level mock for requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Tests public_repos without a license filter (integration test)."""
        client = GithubOrgClient("google")
        repos = client.public_repos()

        self.assertEqual(repos, self.expected_repos)
        self.mock_get.assert_called()

    def test_public_repos_with_license(self) -> None:
        """Tests public_repos with an 'apache-2.0' license filter (integration test)."""
        client = GithubOrgClient("google")
        repos = client.public_repos("apache-2.0")

        self.assertEqual(repos, self.apache2_repos)
        self.mock_get.assert_called()
