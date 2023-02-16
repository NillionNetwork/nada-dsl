import os
from dataclasses import dataclass
import inspect


@dataclass
class SourceRef:
    lineno: int
    offset: int
    file: str
    source_snippet: str

    @classmethod
    def circuit_frame(cls) -> "SourceRef":
        back_stackframe = inspect.currentframe().f_back.f_back.f_back.f_back
        source_snippet = inspect.getsource(back_stackframe)
        offset = len(source_snippet)
        return cls(
            lineno=0,
            offset=offset,
            file=os.path.basename(back_stackframe.f_code.co_filename),
            source_snippet=source_snippet,
        )

    @classmethod
    def back_frame(cls) -> "SourceRef":
        back_stackframe = inspect.currentframe().f_back.f_back
        lineno = back_stackframe.f_lineno
        (offset, code_snippet) = SourceRef.try_get_source_snippet(back_stackframe, lineno)
        return cls(
            lineno=lineno,
            offset=offset,
            file=os.path.basename(back_stackframe.f_code.co_filename),
            source_snippet=code_snippet,
        )

    @staticmethod
    def try_get_source_snippet(code, lineno) -> (str, str):
        src = None
        try:
            src = inspect.getsource(code)
        except OSError:
            return ""

        if (
            "__file__" in code.f_locals
        ):  # is a file we can calculate src snippet from lineno
            lines = src.splitlines()
            offset = 0
            for i in range(lineno - 1):
                offset += len(lines[i]) + 1
            code_snippet = lines[lineno - 1]
            return offset, code_snippet
        else:
            return 0, ""

    def to_dict(self):
        return {
            "lineno": self.lineno,
            "offset": self.offset,
            "file": self.file,
            "source_snippet": self.source_snippet,
        }
