import aiohttp
from typing import List, Dict, Any
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger()

class Commit(BaseModel):
    sha: str
    message: str = "No message available"
    pr_number: int | None = None  # New: PR number
    pr_title: str | None = None   # New: PR title
    pr_url: str | None = None     # New: PR URL

class GitHubClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.graphql_url = "https://api.github.com/graphql"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_commits_between_tags(self, repo: str, from_tag: str, to_tag: str, session: aiohttp.ClientSession) -> List[Commit]:
        try:
            owner, repo_name = repo.split("/")
            from_sha_url = f"{self.base_url}/repos/{repo}/git/ref/tags/{from_tag}"
            to_sha_url = f"{self.base_url}/repos/{repo}/git/ref/tags/{to_tag}"

            async with session.get(from_sha_url, headers={"Authorization": f"token {self.token}"}) as resp:
                if resp.status != 200:
                    raise ValueError(f"Failed to fetch from_tag: {resp.status}")
                from_data = await resp.json()
                from_sha = from_data["object"]["sha"]

            async with session.get(to_sha_url, headers={"Authorization": f"token {self.token}"}) as resp:
                if resp.status != 200:
                    raise ValueError(f"Failed to fetch to_tag: {resp.status}")
                to_data = await resp.json()
                to_sha = to_data["object"]["sha"]

            commits_url = f"{self.base_url}/repos/{repo}/compare/{from_sha}...{to_sha}"
            async with session.get(commits_url, headers={"Authorization": f"token {self.token}"}) as resp:
                if resp.status != 200:
                    raise ValueError(f"Failed to fetch commits: {resp.status}")
                data = await resp.json()
                commits_data = data.get("commits", [])
                
                commits = []
                for c in commits_data:
                    try:
                        commit_dict = {
                            "sha": c.get("sha", ""),
                            "message": c.get("commit", {}).get("message", "No message available")
                        }
                        commits.append(Commit(**commit_dict))
                    except Exception as parse_err:
                        logger.warning("Skipping invalid commit", sha=c.get("sha", "unknown"), error=str(parse_err))
                        continue
                
                # Fetch PRs for each commit
                for commit in commits:
                    pr_data = await self.get_pr_for_commit(owner, repo_name, commit.sha, session)
                    if pr_data:
                        commit.pr_number = pr_data.get("number")
                        commit.pr_title = pr_data.get("title")
                        commit.pr_url = pr_data.get("url")
                
                logger.info("Fetched commits", count=len(commits), repo=repo, total_raw=len(commits_data))
                return commits
        except Exception as e:
            logger.error("Error fetching commits", error=str(e), repo=repo)
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_pr_for_commit(self, owner: str, repo: str, commit_sha: str, session: aiohttp.ClientSession) -> Dict[str, Any] | None:
        try:
            query = """
            query($repo: String!, $owner: String!, $commit: GitObjectID!) {
              repository(name: $repo, owner: $owner) {
                object(oid: $commit) {
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
            variables = {"repo": repo, "owner": owner, "commit": commit_sha}
            async with session.post(
                self.graphql_url,
                json={"query": query, "variables": variables},
                headers={"Authorization": f"Bearer {self.token}"}
            ) as resp:
                if resp.status != 200:
                    logger.warning("Failed to fetch PR for commit", commit=commit_sha, status=resp.status)
                    return None
                data = await resp.json()
                pr_nodes = data.get("data", {}).get("repository", {}).get("object", {}).get("associatedPullRequests", {}).get("nodes", [])
                if pr_nodes:
                    return pr_nodes[0]  # Return first PR (most relevant)
                logger.debug("No PR found for commit", commit=commit_sha)
                return None
        except Exception as e:
            logger.error("Error fetching PR for commit", commit=commit_sha, error=str(e))
            return None
