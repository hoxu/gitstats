from dataclasses import dataclass, field
from datetime import timedelta
from typing import Set

@dataclass
class Author:
    lines_added: int = 0
    lines_removed: int = 0
    commits: int = 0
    first_commit_stamp: int = 0
    last_commit_stamp: int = 0
    last_active_day: str = ''
    active_days: Set[str] = field(default_factory=set)
    place_by_commits: int = 0
    commits_frac: float = 0.0
    date_first: str = ''
    date_last: str = ''
    timedelta: timedelta = None

