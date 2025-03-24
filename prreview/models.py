from datetime import datetime
from dataclasses import dataclass
from typing import Literal, List, TypedDict


@dataclass
class Issue:
    number: int
    title: str
    state: str
    created_at: datetime
    updated_at: datetime
    url: str
    body: str


@dataclass
class PullRequest:
    number: int
    title: str
    changed_files_urls: list[str]
    issue: Issue


class Suggestion(TypedDict):
    ref: str
    suggestion: str


class FileSuggestion(TypedDict):
    file: str
    suggestions: List[Suggestion]


class CurrentFile(TypedDict):
    url: str
    contents: str
    pylint_analysis: str


class AgentState(TypedDict):
    pr: PullRequest
    current_step: Literal["get_pr_details", "find_file", "analyze_file", "conclude"]
    current_file_idx: int
    current_file: CurrentFile
    file_suggestions: List[FileSuggestion]
    refactored_file_contents: List[str]
