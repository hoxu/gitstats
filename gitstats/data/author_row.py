from dataclasses import dataclass

@dataclass
class AuthorRow:
    hash: str
    stamp: int
    author: str
    files_modified: int
    lines_inserted: int
    lines_deleted: int