import os
import requests
from datetime import datetime
from models import Issue, PullRequest

import subprocess
import tempfile
import re


def run_pylint_on_string(code_string):
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        temp_filename = temp_file.name
        temp_file.write(code_string.encode("utf-8"))
    try:
        result = subprocess.run(
            ["pylint", temp_filename], capture_output=True, text=True, check=False
        )
        output = result.stdout + result.stderr
        sanitized_output = re.sub(
            r"{}:".format(re.escape(temp_filename)), "<file>:", output
        )
        base_filename = os.path.basename(temp_filename)
        module_name = os.path.splitext(base_filename)[0]
        sanitized_output = re.sub(
            r"\b{}\b".format(re.escape(module_name)), "<module>", sanitized_output
        )
        return sanitized_output
    except FileNotFoundError:
        return "Error: PyLint is not installed or not in the PATH."
    finally:
        os.unlink(temp_filename)


def get_response_github(url):
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    response = requests.get(url, headers=headers)
    return response.json()


def get_pr_details(owner, repo, pr_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    response = get_response_github(url)
    issue = get_issue_details(response["issue_url"])
    pr_files_response = get_pr_files(owner, repo, pr_number)
    pr = PullRequest(
        number=response["number"],
        title=response["title"],
        changed_files_urls=[file["raw_url"] for file in pr_files_response],
        issue=issue,
    )
    return pr


def get_pr_files(owner, repo, pr_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    response = get_response_github(url)
    return response


def get_issue_details(issue_url):
    response = get_response_github(issue_url)
    issue = Issue(
        number=response["number"],
        title=response["title"],
        state=response["state"],
        created_at=datetime.fromisoformat(response["created_at"]),
        updated_at=datetime.fromisoformat(response["updated_at"]),
        url=response["url"],
        body=response["body"],
    )
    return issue


get_pr_details("shubham0204", "SmolChat-Android", 56)
