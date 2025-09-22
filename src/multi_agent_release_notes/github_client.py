import aiohttp
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()

@dataclass
class Commit:
    sha: str
    message: str
    pr_number: str | None
    pr_title: str | None
    pr_url: str | None

class GitHubClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

    async def get_commits_between_tags(self, repo: str, from_tag: str, to_tag: str, session: aiohttp.ClientSession) -> list[Commit]:
        commits = []
        url = f"https://api.github.com/repos/{repo}/compare/{from_tag}...{to_tag}"
        async with session.get(url, headers=self.headers) as response:
            if response.status != 200:
                raise Exception(f"GitHub API error: {response.status}")
            data = await response.json()
            for commit in data.get("commits", []):
                message = commit["commit"]["message"]
                pr_data = await self._get_pr_for_commit(repo, commit["sha"], session)
                commits.append(Commit(
                    sha=commit["sha"],
                    message=message,
                    pr_number=pr_data["number"] if pr_data else None,
                    pr_title=pr_data["title"] if pr_data else None,
                    pr_url=pr_data["html_url"] if pr_data else None
                ))
        logger.info("Fetched commits", count=len(commits), repo=repo, total_raw=len(data.get("commits", [])))
        return commits

    async def _get_pr_for_commit(self, repo: str, sha: str, session: aiohttp.ClientSession) -> dict | None:
        """Fetch PR associated with a commit SHA using GraphQL."""
        query = """
        query($repoOwner: String!, $repoName: String!, $sha: String!) {
          repository(owner: $repoOwner, name: $repoName) {
            object(oid: $sha) {
              ... on Commit {
                associatedPullRequests(first: 1) {
                  nodes {
                    number
                    title
                    url
                  }
                }
              }
            }
          }
        }
        """
        owner, repo_name = repo.split("/")
        variables = {"repoOwner": owner, "repoName": repo_name, "sha": sha}
        async with session.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=self.headers
        ) as response:
            if response.status != 200:
                logger.warning("GraphQL query failed", status=response.status, sha=sha)
                return None
            data = await response.json()
            nodes = data.get("data", {}).get("repository", {}).get("object", {}).get("associatedPullRequests", {}).get("nodes", [])
            return nodes[0] if nodes else None
