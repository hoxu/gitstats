from dataclasses import dataclass

@dataclass
class AuthorTotals:
    author: str
    total_commits: int
