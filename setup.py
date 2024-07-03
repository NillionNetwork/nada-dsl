import os
from setuptools import setup

VERSION_FILE = "./nada_dsl/version.py"


def get_head_commit() -> str:
    """Returns the git HEAD commit"""
    return os.popen("git rev-parse HEAD").read().rstrip()


def require_version_file_update() -> bool:
    """Update version file when:
    - It doesn't exist, or
    - The version doesn't match the head commit.
    """
    if os.path.isfile(VERSION_FILE):
        with open(VERSION_FILE, "r", encoding="utf-8") as file:
            nada_dsl_commit = file.read().rstrip().split(" ")[1][:-2]
            head_commit = get_head_commit()
            return len(head_commit) > 0 and head_commit != nada_dsl_commit
    return True


if require_version_file_update():
    commit = os.popen("git rev-parse HEAD").read().rstrip()
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(f"print('nada_dsl {commit}')")

setup()
