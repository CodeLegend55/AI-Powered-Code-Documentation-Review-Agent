"""
GitHub Service - Integration with GitHub for diff analysis
"""
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import httpx

from config import settings

@dataclass
class GitHubDiff:
    """Parsed GitHub diff information"""
    repo: str
    branch: str
    files_changed: List[Dict[str, Any]]
    additions: int
    deletions: int
    commits: List[Dict[str, str]]

@dataclass 
class FileChange:
    """Individual file change"""
    filename: str
    status: str  # added, modified, removed
    additions: int
    deletions: int
    patch: str
    language: str

class GitHubService:
    """Service for GitHub API integration"""
    
    def __init__(self):
        self.token = settings.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    def _parse_repo_url(self, url: str) -> tuple:
        """Parse GitHub URL to extract owner and repo"""
        # Handle various URL formats
        patterns = [
            r"github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?$",
            r"^([^/]+)/([^/]+)$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1), match.group(2).rstrip('/')
        
        raise ValueError(f"Invalid GitHub URL: {url}")
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "cpp",
            ".h": "cpp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".swift": "swift",
            ".kt": "kotlin",
        }
        
        for ext, lang in extension_map.items():
            if filename.endswith(ext):
                return lang
        return "unknown"
    
    async def get_pull_request_diff(self, repo_url: str, pr_number: int) -> GitHubDiff:
        """Get diff from a pull request"""
        owner, repo = self._parse_repo_url(repo_url)
        
        async with httpx.AsyncClient() as client:
            # Get PR info
            pr_response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}",
                headers=self.headers
            )
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            # Get PR files
            files_response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files",
                headers=self.headers
            )
            files_response.raise_for_status()
            files_data = files_response.json()
            
            files_changed = []
            total_additions = 0
            total_deletions = 0
            
            for file in files_data:
                file_change = {
                    "filename": file["filename"],
                    "status": file["status"],
                    "additions": file["additions"],
                    "deletions": file["deletions"],
                    "patch": file.get("patch", ""),
                    "language": self._detect_language(file["filename"])
                }
                files_changed.append(file_change)
                total_additions += file["additions"]
                total_deletions += file["deletions"]
            
            return GitHubDiff(
                repo=f"{owner}/{repo}",
                branch=pr_data.get("head", {}).get("ref", "unknown"),
                files_changed=files_changed,
                additions=total_additions,
                deletions=total_deletions,
                commits=[{
                    "sha": pr_data.get("head", {}).get("sha", ""),
                    "message": pr_data.get("title", "")
                }]
            )
    
    async def get_commit_diff(self, repo_url: str, commit_sha: str) -> GitHubDiff:
        """Get diff from a specific commit"""
        owner, repo = self._parse_repo_url(repo_url)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/commits/{commit_sha}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            files_changed = []
            total_additions = 0
            total_deletions = 0
            
            for file in data.get("files", []):
                file_change = {
                    "filename": file["filename"],
                    "status": file["status"],
                    "additions": file["additions"],
                    "deletions": file["deletions"],
                    "patch": file.get("patch", ""),
                    "language": self._detect_language(file["filename"])
                }
                files_changed.append(file_change)
                total_additions += file["additions"]
                total_deletions += file["deletions"]
            
            return GitHubDiff(
                repo=f"{owner}/{repo}",
                branch="commit",
                files_changed=files_changed,
                additions=total_additions,
                deletions=total_deletions,
                commits=[{
                    "sha": commit_sha,
                    "message": data.get("commit", {}).get("message", "")
                }]
            )
    
    async def get_branch_diff(self, repo_url: str, branch: str, 
                              base_branch: str = "main") -> GitHubDiff:
        """Get diff between branches"""
        owner, repo = self._parse_repo_url(repo_url)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/compare/{base_branch}...{branch}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            files_changed = []
            total_additions = 0
            total_deletions = 0
            
            for file in data.get("files", []):
                file_change = {
                    "filename": file["filename"],
                    "status": file["status"],
                    "additions": file["additions"],
                    "deletions": file["deletions"],
                    "patch": file.get("patch", ""),
                    "language": self._detect_language(file["filename"])
                }
                files_changed.append(file_change)
                total_additions += file["additions"]
                total_deletions += file["deletions"]
            
            commits = [
                {"sha": c["sha"], "message": c["commit"]["message"]}
                for c in data.get("commits", [])
            ]
            
            return GitHubDiff(
                repo=f"{owner}/{repo}",
                branch=branch,
                files_changed=files_changed,
                additions=total_additions,
                deletions=total_deletions,
                commits=commits
            )
    
    async def get_file_content(self, repo_url: str, file_path: str, 
                                branch: str = "main") -> str:
        """Get content of a specific file"""
        owner, repo = self._parse_repo_url(repo_url)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}",
                params={"ref": branch},
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content
    
    def parse_diff_to_code(self, patch: str) -> Dict[str, str]:
        """Parse diff patch to extract added and modified code"""
        added_lines = []
        removed_lines = []
        context_lines = []
        
        for line in patch.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                added_lines.append(line[1:])
            elif line.startswith('-') and not line.startswith('---'):
                removed_lines.append(line[1:])
            elif not line.startswith('@@'):
                context_lines.append(line)
        
        return {
            "added": '\n'.join(added_lines),
            "removed": '\n'.join(removed_lines),
            "context": '\n'.join(context_lines)
        }
    
    def is_available(self) -> bool:
        """Check if GitHub service is available"""
        return self.token is not None and len(self.token) > 0


# Global GitHub service instance
github_service = GitHubService()
