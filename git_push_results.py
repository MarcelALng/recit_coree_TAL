#!/usr/bin/env python3
"""
Git automation script to commit and push scraping results to GitHub.
Handles repository initialization, commits, and pushes.
"""

import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path


class GitAutomation:
    def __init__(self, config_file="config.json"):
        """Initialize Git automation with configuration."""
        self.config = self.load_config(config_file)
        self.repo_url = self.config["github"]["repository_url"]
        self.branch = self.config["github"]["branch"]
        self.auto_push = self.config["github"]["auto_push"]
    
    def load_config(self, config_file):
        """Load configuration from JSON file."""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file {config_file} not found!")
            sys.exit(1)
    
    def run_command(self, command, check=True):
        """Run a shell command and return the result."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
    
    def is_git_repo(self):
        """Check if current directory is a Git repository."""
        success, _, _ = self.run_command("git rev-parse --git-dir", check=False)
        return success
    
    def init_repo(self):
        """Initialize Git repository if not already initialized."""
        if not self.is_git_repo():
            print("📦 Initializing Git repository...")
            success, stdout, stderr = self.run_command("git init")
            if success:
                print("✅ Git repository initialized")
                
                # Set default branch name
                self.run_command(f"git branch -M {self.branch}")
                
                # Add remote if repository URL is provided
                if self.repo_url:
                    print(f"🔗 Adding remote origin: {self.repo_url}")
                    self.run_command(f"git remote add origin {self.repo_url}")
            else:
                print(f"❌ Failed to initialize repository: {stderr}")
                return False
        else:
            print("✅ Git repository already initialized")
        
        return True
    
    def get_json_files(self):
        """Get list of JSON files to commit."""
        json_files = []
        
        # Find all president JSON files
        for pattern in ["president_links_*.json", "president_texts_*.json"]:
            json_files.extend(Path(".").glob(pattern))
        
        return [str(f) for f in json_files]
    
    def get_file_stats(self, files):
        """Get statistics about the files to be committed."""
        stats = {
            "total_files": len(files),
            "links_files": 0,
            "texts_files": 0,
            "total_size": 0
        }
        
        for file in files:
            if "links" in file:
                stats["links_files"] += 1
            elif "texts" in file:
                stats["texts_files"] += 1
            
            if os.path.exists(file):
                stats["total_size"] += os.path.getsize(file)
        
        return stats
    
    def create_commit_message(self, stats):
        """Create a meaningful commit message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        template = self.config["github"]["commit_message_template"]
        
        message = template.format(timestamp=timestamp)
        message += f"\n\n📊 Statistics:"
        message += f"\n- Total files: {stats['total_files']}"
        message += f"\n- Links files: {stats['links_files']}"
        message += f"\n- Texts files: {stats['texts_files']}"
        message += f"\n- Total size: {stats['total_size'] / 1024:.2f} KB"
        
        return message
    
    def stage_files(self, files):
        """Stage files for commit."""
        if not files:
            print("⚠️  No JSON files found to commit")
            return False
        
        print(f"\n📝 Staging {len(files)} files...")
        for file in files:
            print(f"  + {file}")
            success, _, stderr = self.run_command(f"git add {file}")
            if not success:
                print(f"❌ Failed to stage {file}: {stderr}")
                return False
        
        # Also add .gitignore and config.json if they exist
        for extra_file in [".gitignore", "config.json"]:
            if os.path.exists(extra_file):
                self.run_command(f"git add {extra_file}", check=False)
        
        print("✅ Files staged successfully")
        return True
    
    def commit_changes(self, message):
        """Commit staged changes."""
        print("\n💾 Creating commit...")
        
        # Check if there are changes to commit
        success, stdout, _ = self.run_command("git diff --cached --quiet", check=False)
        if success:  # No changes
            print("ℹ️  No changes to commit")
            return True
        
        # Create commit
        success, stdout, stderr = self.run_command(f'git commit -m "{message}"')
        if success:
            print("✅ Commit created successfully")
            return True
        else:
            print(f"❌ Failed to create commit: {stderr}")
            return False
    
    def push_to_github(self):
        """Push commits to GitHub."""
        if not self.repo_url:
            print("⚠️  No repository URL configured. Skipping push.")
            print("   Add 'repository_url' to config.json to enable pushing.")
            return True
        
        print(f"\n🚀 Pushing to {self.branch}...")
        
        # Try to push
        success, stdout, stderr = self.run_command(f"git push -u origin {self.branch}", check=False)
        
        if success:
            print("✅ Successfully pushed to GitHub")
            return True
        elif "rejected" in stderr or "non-fast-forward" in stderr:
            print("⚠️  Push rejected. Trying to pull first...")
            
            # Pull with rebase
            success, _, _ = self.run_command(f"git pull --rebase origin {self.branch}", check=False)
            if success:
                # Try push again
                success, _, stderr = self.run_command(f"git push origin {self.branch}")
                if success:
                    print("✅ Successfully pushed after rebase")
                    return True
            
            print(f"❌ Failed to push: {stderr}")
            return False
        else:
            print(f"❌ Failed to push: {stderr}")
            print("\n💡 Possible solutions:")
            print("   1. Check your Git credentials")
            print("   2. Verify repository URL in config.json")
            print("   3. Ensure you have push access to the repository")
            return False
    
    def run(self, dry_run=False):
        """Run the complete Git automation workflow."""
        print("=" * 60)
        print("🔧 Git Automation for Presidential Speeches")
        print("=" * 60)
        
        # Initialize repository
        if not self.init_repo():
            return False
        
        # Get files to commit
        files = self.get_json_files()
        stats = self.get_file_stats(files)
        
        print(f"\n📊 Found {stats['total_files']} JSON files:")
        print(f"   - Links files: {stats['links_files']}")
        print(f"   - Texts files: {stats['texts_files']}")
        print(f"   - Total size: {stats['total_size'] / 1024:.2f} KB")
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be made")
            print(f"\nWould commit message:")
            print(self.create_commit_message(stats))
            return True
        
        # Stage files
        if not self.stage_files(files):
            return False
        
        # Create commit
        commit_message = self.create_commit_message(stats)
        if not self.commit_changes(commit_message):
            return False
        
        # Push to GitHub
        if self.auto_push:
            if not self.push_to_github():
                print("\n⚠️  Push failed, but changes are committed locally")
                print("   You can manually push later with: git push origin", self.branch)
                return False
        else:
            print("\n✅ Changes committed locally (auto-push disabled)")
            print(f"   To push manually: git push origin {self.branch}")
        
        print("\n" + "=" * 60)
        print("✅ Git automation completed successfully!")
        print("=" * 60)
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automate Git commits and pushes for scraping results")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    git_auto = GitAutomation(args.config)
    success = git_auto.run(dry_run=args.dry_run)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
