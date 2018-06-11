from datetime import timedelta
from dataclasses import dataclass
from typing import List

@dataclass
class PullRequest:
    stamp: int
    hash: str
    author: str
    parent_hashes: List[str]
    branch_rev: str = None
    master_rev: str = None
    duration: timedelta = None
    invalid_pr: bool = False

