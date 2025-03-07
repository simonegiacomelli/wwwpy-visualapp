from dataclasses import dataclass

from common.format_bytes import format_bytes


@dataclass
class CsvInfo:
    name: str
    chunk_number: int
    file_size_bytes: int

    def file_size_human(self) -> str:
        return format_bytes(self.file_size_bytes)
