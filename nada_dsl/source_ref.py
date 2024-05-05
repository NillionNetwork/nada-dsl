"""
Source reference representation data structure.
"""

import os
from dataclasses import dataclass
from typing import Tuple
import inspect

USED_SOURCES = {}


@dataclass
class SourceRef:
    """
    Source reference representation, i.e., a specific location in the source code.
    """

    file: str
    lineno: int
    offset: int
    length: int

    @classmethod
    def back_frame(cls) -> "SourceRef":
        """Get the source reference of the calling frame."""
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
        """Try to get line information from the source code."""
        # We don't include file sources from nada_dsl package.
        # This is to prevent 'nada_fn' wrongly adding nada_dsl source files from this package.
        if "nada_dsl" in backend_frame.f_code.co_filename:
            return 0, 0, ""
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
        """Convert the SourceRef object to a dictionary."""
        return {
            "lineno": self.lineno,
            "offset": self.offset,
            "file": self.file,
            "length": self.length,
        }

    @staticmethod
    def get_sources():
        """Get all sources."""
        return USED_SOURCES
