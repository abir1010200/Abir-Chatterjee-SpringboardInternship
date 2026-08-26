#!/usr/bin/env python3
"""
AI-Powered Smart Irrigation System - GitHub Remote & Push Utility
================================================================
Configures the remote origin and pushes all branches (main, dev, feature/*) to GitHub.
"""

import sys
import os
import argparse
from dulwich.repo import Repo
from dulwich import porcelain

def configure_and_push(remote_url: str, username: str = None, token: str = None):
    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    r = Repo(repo_dir)

    # Format authenticated URL if token provided
    auth_url = remote_url
    if token:
        user = username or "oauth2"
        # https://token@github.com/user/repo.git or https://user:token@github.com/...
        if remote_url.startswith("https://"):
            clean_url = remote_url[len("https://"):]
            auth_url = f"https://{user}:{token}@{clean_url}"

    print(f"Setting remote 'origin' -> {remote_url}")
    
    config = r.get_config()
    config.set((b"remote", b"origin"), b"url", auth_url.encode("utf-8"))
    config.set((b"remote", b"origin"), b"fetch", b"+refs/heads/*:refs/remotes/origin/*")
    config.write_to_path()

    print("Remote 'origin' configured successfully.")
    
    print("\nPushing branches to GitHub...")
    branches = ["main", "dev", "feature/sensor-ingestion", "feature/weather-api", "feature/field-config"]
    for b in branches:
        try:
            print(f"Pushing branch '{b}'...")
            porcelain.push(r, auth_url, refspecs=[f"refs/heads/{b}:refs/heads/{b}".encode("utf-8")])
            print(f"✅ Successfully pushed '{b}' to GitHub!")
        except Exception as e:
            print(f"⚠️ Note on branch '{b}': {e}")

    print("\n🎉 GitHub synchronization complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure and push to GitHub repository")
    parser.add_argument("url", type=str, help="GitHub repository URL (e.g. https://github.com/username/repo.git)")
    parser.add_argument("--username", type=str, default=None, help="GitHub username")
    parser.add_argument("--token", type=str, default=None, help="GitHub Personal Access Token (PAT)")

    args = parser.parse_args()
    configure_and_push(args.url, args.username, args.token)
