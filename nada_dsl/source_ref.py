"""
Source reference representation data structure.
"""

import os
from dataclasses import dataclass
from typing import Tuple
import inspect

USED_SOURCES = {}
REFS = []

tuple_index_map = {}
next_index = 0

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

    def to_index(self):
        """Adds the current object into a dict as a key as well as an entry in an array, and returns an index to it"""
        global next_index
        key = self.to_key()
        value = self.to_value()
        if key in tuple_index_map:
            return tuple_index_map[key]
        else:
            tuple_index_map[key] = next_index
            REFS.append(value)
            next_index += 1
            return tuple_index_map[key]

    def to_value(self):
        """Convert the SourceRef object to a dictionary."""
        return {
            "lineno": self.lineno,
            "offset": self.offset,
            "file": self.file,
            "length": self.length,
        }

    def to_key(self):
        return (self.lineno, self.offset, self.file, self.length)

    @staticmethod
    def get_sources():
        """Get all sources."""
        return USED_SOURCES

    @staticmethod
    def get_refs():
        """Get all refs."""
        return REFS
