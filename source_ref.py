import os
from dataclasses import dataclass
import inspect


@dataclass
class SourceRef:
    file: str
    lineno: int
    offset: int
    length: int

    @classmethod
    def circuit_frame(cls) -> "SourceRef":
        back_stackframe = inspect.currentframe().f_back.f_back.f_back.f_back
        source_snippet = inspect.getsource(back_stackframe)
        return cls(
            file=os.path.basename(back_stackframe.f_code.co_filename),
            source_snippet=source_snippet,
        )

    @classmethod
    def back_frame(cls) -> "SourceRef":
        lineno = inspect.currentframe().f_back.f_back.f_lineno
        backend_frame = inspect.currentframe()
        while "__file__" not in backend_frame.f_locals:
            backend_frame = backend_frame.f_back
        (offset, length, snippet) = SourceRef.try_get_line_info(backend_frame, lineno)
        return cls(
            lineno=lineno,
            offset=offset,
            file=os.path.basename(backend_frame.f_code.co_filename),
            length=length,
        )

    @staticmethod
    def try_get_line_info(code, lineno) -> (int, int):
        src = None
        try:
            src = inspect.getsource(code)
        except OSError:
            return ""

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
