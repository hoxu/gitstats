from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict

#    # Outputs "<stamp> <date> <time> <timezone> <author> '<' <mail> '>'"

@dataclass
class Revision:
    hash: str
    stamp: int
    timezone: int = 0
    author: str = ''
    email: str = ''
    domain: str = ''
    file_count: int = 0

