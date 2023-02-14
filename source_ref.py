import os
import sys
from dataclasses import dataclass
import inspect

ROOT_PATH = os.path.dirname(sys.modules['__main__'].__file__) + "/"

@dataclass
class SourceRef:
    lineno: str
    file: str
    source_snippet: str

    @classmethod
    def back_frame(cls) -> "SourceRef":
        back_stackframe = inspect.currentframe().f_back.f_back
        lineno = back_stackframe.f_lineno
        return cls(
            lineno=lineno,
            file=back_stackframe.f_code.co_filename.replace(ROOT_PATH, ""),
            source_snippet=SourceRef.try_get_source_snippet(back_stackframe, lineno),
        )

    @staticmethod
    def try_get_source_snippet(code, lineno) -> str:
        src = None
        try:
            src = inspect.getsource(code)
        except OSError:
            return ""

        if (
            "__file__" in code.f_locals
        ):  # is a file we can calculate src snippet from lineno
            lines = src.splitlines()
            src_from = lineno - 3 if lineno > 3 else 0
            src_to = lineno + 3 if lineno + 3 < len(lines) else len(lines)
            lines[lineno] = lines[lineno] + " <--- ${CODE_ERROR_MSG}$"
            lines = lines[src_from:src_to]
            code_snippet = "\n".join(lines)
            return code_snippet
        else:
            return ""

    def to_dict(self):
        return {
            "lineno": self.lineno,
            "file": self.file,
            "source_snippet": self.source_snippet,
        }
