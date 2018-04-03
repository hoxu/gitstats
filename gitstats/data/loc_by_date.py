from dataclasses import dataclass


@dataclass
class LocByDate:
    hash: str = ''
    stamp: int = 0
    file_count: int = 0
    lines_inserted: int = 0
    lines_deleted: int = 0
    total_lines: int = 0


