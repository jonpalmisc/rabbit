"""
rabbit - GitHub repository backup tool

Usage:
  rabbit [-hvp] [--token PAT] [PATTERN ...]

Options:
  -h, --help         Show help and usage information
  -v, --version      Show program version
  -p, --print        Print all expanded patterns without cloning
  -T, --token PAT    Personal access token to use

"""
from docopt import docopt

from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository

from fnmatch import fnmatch
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
    args = docopt(__doc__)  # pyright: ignore

    if len(raw_patterns := args["PATTERN"]) == 0:
        print("No targets provided")

    client = Github(args["--token"])
    patterns = [Pattern(rp) for rp in raw_patterns]

    repos: List[Repository] = []
    for p in patterns:
        repos += p.expand(client)

    if args["--print"]:
        for r in repos:
            print(r.ssh_url)
