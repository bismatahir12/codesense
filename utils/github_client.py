import requests


class GitHubClient:
    """Minimal GitHub API client for PR data fetching and comment posting."""

    BASE = "https://api.github.com"

    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get(self, path: str, params: dict = None):
        resp = requests.get(f"{self.BASE}{path}", headers=self.headers, params=params)
        if resp.status_code == 404:
            raise ValueError(f"Not found: {path}. Check repo name and PR number.")
        if resp.status_code == 401:
            raise ValueError("Invalid GitHub token. Check your token and its scopes.")
        resp.raise_for_status()
        return resp.json()

    def get_pr_data(self, owner: str, repo: str, pr_number: int) -> dict:
        """Fetch PR metadata and its full diff."""
        pr = self._get(f"/repos/{owner}/{repo}/pulls/{pr_number}")

        # Fetch the diff
        diff_resp = requests.get(
            f"{self.BASE}/repos/{owner}/{repo}/pulls/{pr_number}",
            headers={**self.headers, "Accept": "application/vnd.github.v3.diff"},
        )
        diff_resp.raise_for_status()
        diff_text = diff_resp.text

        # Fetch changed files list
        files_data = self._get(f"/repos/{owner}/{repo}/pulls/{pr_number}/files")
        files = [
            {
                "filename": f["filename"],
                "status": f["status"],          # added / modified / removed
                "additions": f["additions"],
                "deletions": f["deletions"],
                "patch": f.get("patch", ""),    # the actual diff hunk
            }
            for f in files_data
        ]

        return {
            "title":         pr["title"],
            "body":          pr.get("body") or "",
            "author":        pr["user"]["login"],
            "head_branch":   pr["head"]["ref"],
            "base_branch":   pr["base"]["ref"],
            "changed_files": pr["changed_files"],
            "additions":     pr["additions"],
            "deletions":     pr["deletions"],
            "files":         files,
            "diff":          diff_text[:12000],  # cap to avoid token limits
        }

    def post_pr_comment(self, owner: str, repo: str, pr_number: int, body: str):
        """Post a review comment to the PR."""
        resp = requests.post(
            f"{self.BASE}/repos/{owner}/{repo}/issues/{pr_number}/comments",
            headers=self.headers,
            json={"body": body},
        )
        resp.raise_for_status()
        return resp.json()
