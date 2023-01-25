from inspect import currentframe


def get_back_file_lineno() -> dict:
    back_stackframe = currentframe().f_back.f_back
    return {
        "lineno": back_stackframe.f_lineno,
        "file": back_stackframe.f_code.co_filename
    }
