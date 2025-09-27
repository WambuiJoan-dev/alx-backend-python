#!/usr/bin/env python3
"""A github org client
"""
from typing import (
    List,
    Dict,
)

from utils import (
    get_json,
    access_nested_map,
    memoize,
)


class GithubOrgClient:
    """A Githib org client

    This class provides methods to interact with the GitHub API
    to fetch organization and repository information, leveraging
    memoization and utility functions.
    """
    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org_name: str) -> None:
        """Init method of GithubOrgClient"""
        self._org_name = org_name

    @memoize
    def org(self) -> Dict:
        """Fetches and memoizes the organization's public information (JSON payload)."""
        return get_json(self.ORG_URL.format(org=self._org_name))

    @property
    def _public_repos_url(self) -> str:
        """Returns the public repositories URL from the organization payload."""
        return self.org["repos_url"]

    @memoize
    def repos_payload(self) -> Dict:
        """Fetches and memoizes the public repositories payload (list of repos)."""
        return get_json(self._public_repos_url)

    def public_repos(self, license: str = None) -> List[str]:
        """
        Returns a list of public repository names for the organization,
        optionally filtered by license.
        """
        json_payload = self.repos_payload
        public_repos = [
            repo["name"] for repo in json_payload
            if license is None or self.has_license(repo, license)
        ]

        return public_repos

    @staticmethod
    def has_license(repo: Dict[str, Dict], license_key: str) -> bool:
        """
        Static method to check if a repository has the specified license key.
        Uses access_nested_map safely.
        """
        assert license_key is not None, "license_key cannot be None"
        try:
            has_license = access_nested_map(repo, ("license", "key")) == license_key
        except KeyError:
            return False
        return has_license
