import re
from typing import Optional, Tuple


def parse_pr_url(url: str) -> Optional[Tuple[str, str, int]]:
    """
    Parse a GitHub PR URL into (owner, repo, pr_number).
    Accepts:
      https://github.com/owner/repo/pull/42
      https://github.com/owner/repo/pull/42/files
    Returns None if the URL is invalid.
    """
    pattern = r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.search(pattern, url.strip())
    if not match:
        return None
    owner, repo, number = match.groups()
    return owner, repo, int(number)
