from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, Set


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
    activity_by_day_and_hour: Dict[int, Dict[int, int]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))
    extra_effort: int = 0
    extra_frac: float = 0.0


