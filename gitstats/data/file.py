from dataclasses import dataclass

@dataclass
class File:
    full_path: str
    ext: str
    size: int
    lines: int = 0


