"""
rabbit - GitHub repository backup tool

Usage:
  rabbit [-plh] [-t PAT] [PATTERN ...]

Options:
  -p, --prefix       Prefix to clone all repositories into
  -l, --list         List all expanded patterns without cloning
  -t, --token PAT    Personal access token to use
  -h, --help         Show help and usage information

"""
from docopt import docopt

from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository

from fnmatch import fnmatch
import sys
from typing import List, Optional


def get_entity_repos(client: Github, name: str) -> Optional[PaginatedList]:
    """
    Get all of the repositories belonging to a user or organization.
    """

    try:
        org = client.get_organization(name)
        return org.get_repos("all")
    except:
        pass

    try:
        user = client.get_user(name)
        return user.get_repos("all")
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

        return [r for r in repos if fnmatch(r.name, self.query)]


if __name__ == "__main__":
    # Set help flag if no arguments are provided
    if len(sys.argv) == 1:
        sys.argv.append("-h")
    args = docopt(__doc__)  # pyright: ignore

    if token := args["--token"] is None:
        print("Error: No authentication token provided", file=sys.stderr)
        sys.exit(1)

    client = Github(args["--token"])
    patterns = [Pattern(rp) for rp in args["PATTERN"]]

    repos: List[Repository] = []
    for p in patterns:
        repos += p.expand(client)

    if args["--list"]:
        for r in repos:
            print(r.ssh_url)
