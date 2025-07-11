from github import Github
from github.GithubException import GithubException
from flask import current_app
import re
from datetime import datetime


class GitHubService:
    def __init__(self, token=None):
        self.token = token or current_app.config.get('GITHUB_TOKEN')
        self.repo_name = current_app.config.get('GITHUB_REPO')
        self.base_branch = current_app.config.get('GITHUB_BASE_BRANCH', 'main')
        
        if not self.token:
            raise ValueError("GitHub token not configured")
        if not self.repo_name:
            raise ValueError("GitHub repository not configured")
        
        self.github = Github(self.token)
        try:
            self.repo = self.github.get_repo(self.repo_name)
        except GithubException as e:
            raise ValueError(f"Failed to access repository {self.repo_name}: {str(e)}")
    
    def generate_branch_name(self, company, job_title, job_id):
        """Generate a sanitized branch name based on company and job title"""
        # Remove special characters and replace spaces with hyphens
        company_clean = re.sub(r'[^a-zA-Z0-9\s-]', '', company).strip()
        company_clean = re.sub(r'\s+', '-', company_clean).lower()
        
        title_clean = re.sub(r'[^a-zA-Z0-9\s-]', '', job_title).strip()
        title_clean = re.sub(r'\s+', '-', title_clean).lower()
        
        # Limit length to prevent overly long branch names
        company_clean = company_clean[:30]
        title_clean = title_clean[:30]
        
        # Create branch name with date for uniqueness
        date_str = datetime.now().strftime('%Y%m%d')
        branch_name = f"job/{company_clean}/{title_clean}-{date_str}-{job_id}"
        
        return branch_name
    
    def create_branch(self, branch_name):
        """Create a new branch from the base branch"""
        try:
            # Get the SHA of the base branch
            base_ref = self.repo.get_git_ref(f'heads/{self.base_branch}')
            base_sha = base_ref.object.sha
            
            # Create the new branch
            self.repo.create_git_ref(f'refs/heads/{branch_name}', base_sha)
            
            return True, f"Branch '{branch_name}' created successfully"
        except GithubException as e:
            if e.status == 422 and "Reference already exists" in str(e):
                return False, f"Branch '{branch_name}' already exists"
            return False, f"Failed to create branch: {str(e)}"
    
    def branch_exists(self, branch_name):
        """Check if a branch exists"""
        try:
            self.repo.get_branch(branch_name)
            return True
        except GithubException:
            return False
    
    def get_branch_url(self, branch_name):
        """Get the URL for a specific branch"""
        return f"https://github.com/{self.repo_name}/tree/{branch_name}"
    
    def list_job_branches(self):
        """List all branches that start with 'job/'"""
        try:
            branches = []
            for branch in self.repo.get_branches():
                if branch.name.startswith('job/'):
                    branches.append(branch.name)
            return branches
        except GithubException as e:
            raise ValueError(f"Failed to list branches: {str(e)}")