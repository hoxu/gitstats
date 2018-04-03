from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Tag:
    tag: str
    stamp: int
    hash: str
    commits: int = 0
    authors: Dict[str, int] = field(default_factory=defaultdict(int))


