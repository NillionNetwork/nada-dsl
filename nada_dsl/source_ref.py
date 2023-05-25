import os
from dataclasses import dataclass
from typing import Tuple
import inspect

USED_SOURCES = {}


@dataclass
class SourceRef:
    file: str
    lineno: int
    offset: int
    length: int

    @classmethod
    def back_frame(cls) -> "SourceRef":
        backend_frame = inspect.currentframe().f_back.f_back
        lineno = backend_frame.f_lineno
        (offset, length, snippet) = SourceRef.try_get_line_info(backend_frame, lineno)
        return cls(
            lineno=lineno,
            offset=offset,
            file=os.path.basename(backend_frame.f_code.co_filename),
            length=length,
        )

    @staticmethod
    def try_get_line_info(backend_frame, lineno) -> Tuple[int, int, str]:
        filename = os.path.basename(backend_frame.f_code.co_filename)

        src = None
        try:
            if filename not in USED_SOURCES:
                with open(f"{backend_frame.f_code.co_filename}") as file:
                    src = file.read()
                USED_SOURCES[filename] = src
            else:
                src = USED_SOURCES[filename]
        except OSError:
            return 0, 0, ""

        lines = src.splitlines()
        if lineno < len(lines):
            offset = 0
            for i in range(lineno - 1):
                offset += len(lines[i]) + 1
            return offset, len(lines[lineno - 1]), lines[lineno - 1]
        else:
            return 0, 0, ""

    def to_dict(self):
        return {
            "lineno": self.lineno,
            "offset": self.offset,
            "file": self.file,
            "length": self.length,
        }

    @staticmethod
    def get_sources():
        return USED_SOURCES
