#!/usr/bin/env python3

"""
rabbit - GitHub repository backup tool

Usage:
  rabbit [-ldh] [-p PREFIX] [-t TOKEN] [PATTERN ...]

Options:
  -p, --prefix PREFIX    Prefix to clone all repositories into
  -d, --date-suffix      Append the date to the prefix
  -l, --list             List all expanded patterns without cloning
  -t, --token TOKEN      Personal access token to use
  -h, --help             Show help and usage information

"""
from docopt import docopt

from github import Github
from github.Repository import Repository

from datetime import datetime
from fnmatch import fnmatch
import subprocess
import sys
from typing import List, Optional


# Cached repositories for the authenticated user
AU_REPO_CACHE: List[Repository] = []
AU_REPO_CACHE_INITIALIZED = False


def get_auth_user_repos(client: Github) -> List[Repository]:
    """
    Get the authenticated user's repos; caches repos for speed.
    """

    global AU_REPO_CACHE, AU_REPO_CACHE_INITIALIZED

    if not AU_REPO_CACHE_INITIALIZED:
        au = client.get_user()
        AU_REPO_CACHE = list(au.get_repos())
        AU_REPO_CACHE_INITIALIZED = True

    return AU_REPO_CACHE


def get_entity_repos(client: Github, name: str) -> Optional[List[Repository]]:
    """
    Get all of the repositories belonging to a user or organization.
    """

    try:
        ent = client.get_user(name)
        return list(ent.get_repos("all"))
    except:
        return None


class Pattern:
    """
    A pattern describing one or more repos belonging to an organization.
    """

    org: str
    query: str

    def __init__(self, raw: str) -> None:
        parts = raw.split("/")
        self.org = parts[0]
        self.query = parts[1]

    def __repr__(self) -> str:
        return f"<Pattern {self.org}/{self.query}>"

    def expand(self, client: Github) -> List[Repository]:
        """
        Get all of the repositories matched by this pattern.
        """

        if (repos := get_entity_repos(client, self.org)) is None:
            return []

        # Add the authenticated user's repos, which may include private repos
        # belonging to the target entity not returned by `get_entity_repos`,
        # then remove any duplicates.
        repos += get_auth_user_repos(client)
        repos = set(repos)

        return [
            r
            for r in repos
            if (fnmatch(r.name, self.query) and r.owner.login == self.org)
        ]


if __name__ == "__main__":
    # Set help flag if no arguments are provided
    if len(sys.argv) == 1:
        sys.argv.append("-h")
    args = docopt(__doc__)  # pyright: ignore

    if (token := args["--token"]) is None:
        print("Error: No authentication token provided", file=sys.stderr)
        sys.exit(1)

    client = Github(token)

    # Expand all patterns and collect a list of repositories
    repos: List[Repository] = []
    patterns = [Pattern(rp) for rp in args["PATTERN"]]
    for p in patterns:
        repos += p.expand(client)

    # List the matched repositories and exit, if requested
    if args["--list"]:
        for r in repos:
            print(r.ssh_url)

        sys.exit(0)

    prefix = args["--prefix"]
    if args["--date-suffix"]:
        prefix += "-" + datetime.now().isoformat()[:10]

    for r in repos:
        dest = prefix + "/" + r.full_name if prefix else r.full_name
        subprocess.run(["git", "clone", r.ssh_url, dest])
