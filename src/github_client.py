import aiohttp
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()

@dataclass
class Commit:
    sha: str
    message: str
    author_name: str
    author_email: str
    pr_number: str | None
    pr_title: str | None
    pr_url: str | None

class GitHubClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def get_commits_between_tags(self, repo: str, from_tag: str, to_tag: str, session: aiohttp.ClientSession) -> list[Commit]:
        commits = []
        url = f"https://api.github.com/repos/{repo}/compare/{from_tag}...{to_tag}"
        
        logger.info("Fetching commits from GitHub", repo=repo, from_tag=from_tag, to_tag=to_tag, url=url)
        
        async with session.get(url, headers=self.headers) as response:
            # Get error detail for all non-200 responses
            if response.status != 200:
                error_detail = await response.text()
                logger.error(f"GitHub API {response.status} error", 
                            repo=repo, 
                            from_tag=from_tag, 
                            to_tag=to_tag, 
                            detail=error_detail[:300])
            
            if response.status == 404:
                # Provide helpful error message
                error_detail = await response.text()
                
                # Try to determine the specific issue
                if "Repository not found" in error_detail or "Not Found" in error_detail:
                    raise Exception(
                        f"Repository '{repo}' not found or not accessible. "
                        f"Please check:\n"
                        f"  1. Repository name is correct (format: owner/repo)\n"
                        f"  2. Repository exists and is public, or you have access\n"
                        f"  3. Your GITHUB_TOKEN has 'repo' or 'public_repo' scope"
                    )
                else:
                    raise Exception(
                        f"Tags '{from_tag}' or '{to_tag}' not found in repository '{repo}'. "
                        f"Please check:\n"
                        f"  1. Both tags exist in the repository\n"
                        f"  2. Tag names are spelled correctly (case-sensitive)\n"
                        f"  3. Use 'git tag' to list available tags\n"
                        f"  4. Try using commit SHAs instead of tag names"
                    )
            
            elif response.status == 401:
                raise Exception(
                    "GitHub authentication failed. Please check:\n"
                    "  1. GITHUB_TOKEN is set in .env file\n"
                    "  2. Token is valid and not expired\n"
                    "  3. Token has required scopes (repo or public_repo)"
                )
            
            elif response.status == 403:
                error_detail = await response.text()
                if "rate limit" in error_detail.lower():
                    raise Exception(
                        "GitHub API rate limit exceeded. Please:\n"
                        "  1. Wait for rate limit to reset\n"
                        "  2. Use authenticated requests (set GITHUB_TOKEN)\n"
                        "  3. Check rate limit: https://api.github.com/rate_limit"
                    )
                else:
                    raise Exception(
                        f"GitHub API forbidden (403). Possible reasons:\n"
                        f"  1. Repository is private and token doesn't have access\n"
                        f"  2. Token has insufficient permissions\n"
                        f"  3. IP address is blocked\n"
                        f"  Detail: {error_detail[:200]}"
                    )
            
            elif response.status != 200:
                error_detail = await response.text()
                raise Exception(
                    f"GitHub API error: {response.status}\n"
                    f"Detail: {error_detail[:300]}"
                )
            
            data = await response.json()
            
            # Check if there are any commits
            commit_list = data.get("commits", [])
            if not commit_list:
                logger.warning("No commits found between tags", 
                             repo=repo, 
                             from_tag=from_tag, 
                             to_tag=to_tag)
                return []
            
            logger.info("Processing commits", count=len(commit_list))
            
            for commit in commit_list:
                commit_data = commit["commit"]
                message = commit_data["message"]
                
                # Extract author information
                author = commit_data.get("author", {})
                author_name = author.get("name", "Unknown")
                author_email = author.get("email", "")
                
                pr_data = await self._get_pr_for_commit(repo, commit["sha"], session)
                commits.append(Commit(
                    sha=commit["sha"],
                    message=message,
                    author_name=author_name,
                    author_email=author_email,
                    pr_number=pr_data["number"] if pr_data else None,
                    pr_title=pr_data["title"] if pr_data else None,
                    pr_url=pr_data["html_url"] if pr_data else None
                ))
        
        logger.info("Fetched commits successfully", 
                   count=len(commits), 
                   repo=repo, 
                   total_raw=len(commit_list))
        return commits

    async def _get_pr_for_commit(self, repo: str, sha: str, session: aiohttp.ClientSession) -> dict | None:
        """Fetch PR associated with a commit SHA using GraphQL."""
        # FIXED: Use GitObjectID type instead of String! for oid parameter
        query = """
        query($repoOwner: String!, $repoName: String!, $sha: GitObjectID!) {
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
        
        try:
            async with session.post(
                "https://api.github.com/graphql",
                json={"query": query, "variables": variables},
                headers=self.headers
            ) as response:
                if response.status != 200:
                    logger.warning("GraphQL query failed", 
                                 status=response.status, 
                                 sha=sha[:7])
                    return None
                
                data = await response.json()
                
                # Check for GraphQL errors
                if "errors" in data:
                    logger.warning("GraphQL returned errors", 
                                 errors=data["errors"], 
                                 sha=sha[:7])
                    return None
                
                nodes = data.get("data", {}).get("repository", {}).get("object", {}).get("associatedPullRequests", {}).get("nodes", [])
                if nodes:
                    pr = nodes[0]
                    return {
                        "number": str(pr.get("number", "")),
                        "title": pr.get("title", ""),
                        "html_url": pr.get("url", "")
                    }
                return None
        except Exception as e:
            logger.warning("Error fetching PR for commit", 
                         sha=sha[:7], 
                         error=str(e))
            return None
