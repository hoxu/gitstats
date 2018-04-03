from dataclasses import dataclass

@dataclass
class AuthorRow:
    sha: str
    stamp: int
    author: str
    files_modified: int
    lines_inserted: int
    lines_deleted: int