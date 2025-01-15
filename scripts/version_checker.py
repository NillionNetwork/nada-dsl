# Checks python package version
# Based on https://github.com/maybe-hello-world/pyproject-check-version/blob/v4/version_checker.py
import re
import sys
import tomllib
import os
import requests
from packaging import version
from packaging.version import Version
import json


def get_public_version(project_name: str) -> Version:
    response = requests.get(f"https://pypi.org/pypi/{project_name}/json")
    if response.status_code == 200:
        return version.parse(json.loads(response.content)["info"]["version"])
    else:
        return Version("0.0")


if __name__ == "__main__":
    pyproject_toml_path = sys.argv[1]
    with open(pyproject_toml_path, "rb") as f:
        project = tomllib.load(f)

    project_version = version.parse(project["project"]["version"])
    public_project_version = get_public_version(project["project"]["name"])

    with open(os.environ["GITHUB_OUTPUT"], "at") as f:
        f.write(
            f"local_version_is_higher={str(project_version > public_project_version).lower()}\n"
        )
        f.write(f"local_version={str(project_version)}\n")
        f.write(f"public_version={str(public_project_version)}\n")
