from dataclasses import dataclass

@dataclass
class FileInfo:
    language: str
    file_count: int
    line_count: int
    code_line_count: int
    comment_line_count: int
    blank_line_count: int

    def __post_init__(self):
        self.file_count = int(self.file_count)
        self.line_count = int(self.line_count)
        self.code_line_count = int(self.code_line_count)
        self.comment_line_count = int(self.comment_line_count)
        self.blank_line_count = int(self.blank_line_count)

    def __sub__(self, other: 'FileInfo') -> 'FileInfo':
        return FileInfo(self.language,
                        self.file_count - other.file_count,
                        self.line_count - other.line_count,
                        self.code_line_count - other.code_line_count,
                        self.comment_line_count - other.comment_line_count,
                        self.blank_line_count - other.blank_line_count)