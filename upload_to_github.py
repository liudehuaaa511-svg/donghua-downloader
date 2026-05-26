#!/usr/bin/env python3
"""
GitHub Upload Script
Upload all files to GitHub repository using API

Usage: python upload_to_github.py YOUR_TOKEN YOUR_USERNAME
"""

import requests
import base64
import os
import sys

def upload_file(token, owner, repo, local_path, repo_path):
    """Upload a file to GitHub"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Read file content
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_path}"
    
    # Check if file exists
    r = requests.get(url, headers=headers)
    sha = None
    if r.status_code == 200:
        sha = r.json().get("sha")
    
    data = {
        "message": f"Add {repo_path}",
        "content": content,
        "branch": "main"
    }
    
    if sha:
        data["sha"] = sha
    
    r = requests.put(url, headers=headers, json=data)
    
    if r.status_code in [200, 201]:
        print(f"OK: {repo_path}")
        return True
    else:
        print(f"FAIL: {repo_path}: {r.status_code}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python upload_to_github.py YOUR_TOKEN YOUR_USERNAME")
        print("\nCreate a token at: https://github.com/settings/tokens/new")
        print("Required scopes: repo, workflow")
        print("\nExample:")
        print("  python upload_to_github.py ghp_xxxx myusername")
        return
    
    token = sys.argv[1]
    owner = sys.argv[2]
    repo = "donghua-downloader"
    
    # Get script directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 50)
    print("Uploading to GitHub")
    print(f"Repository: {owner}/{repo}")
    print("=" * 50)
    
    files = [
        ("donghua_downloader.py", "donghua_downloader.py"),
        ("gui.py", "gui.py"),
        ("README.md", "README.md"),
        ("requirements.txt", "requirements.txt"),
        ("LICENSE", "LICENSE"),
        ("setup.py", "setup.py"),
        (".gitignore", ".gitignore"),
        ("examples/download_single.py", "examples/download_single.py"),
        ("examples/download_series.py", "examples/download_series.py"),
        ("docs/API.md", "docs/API.md"),
    ]
    
    success = 0
    failed = 0
    
    for local_name, repo_name in files:
        local_path = os.path.join(base_dir, local_name)
        if os.path.exists(local_path):
            if upload_file(token, owner, repo, local_path, repo_name):
                success += 1
            else:
                failed += 1
        else:
            print(f"SKIP: {local_name}: File not found")
            failed += 1
    
    print(f"\n{'=' * 50}")
    print(f"Complete: {success} success, {failed} failed")
    print(f"Visit: https://github.com/{owner}/{repo}")

if __name__ == "__main__":
    main()
