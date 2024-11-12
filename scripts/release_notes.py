# Creates a JSON formatted list of release notes. It follows the same format
# as in the GitHub API.
#
# Changes are split into categories:
# - `breaking_changes`, has the list of breaking changes
# - `bug_fixes`,
# - `new_features`,
# - `other`
#
# USAGE: pass an initial and final reference to generate release notes
# `release_notes.py v0.6.1 v0.7.0` will generate the release notes for versions between v0.6.1 and v0.7.0
#
# Motivation: While GitHub generates the release notes between releases, this tool can generate release notes between any two references.


import json
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class ReleaseNotes:
    breaking_changes: list[str]
    bug_fixes: list[str]
    new_features: list[str]
    other: list[str]

    def to_json(self) -> str:
        json_map = {
            "breaking_changes": self.breaking_changes,
            "bug_fixes": self.bug_fixes,
            "new_features": self.new_features,
            "other": self.other,
        }
        return json.dumps(json_map)


def parse_git_log(initial_tag: str, final_tag: str):
    git_output = subprocess.Popen(
        ["git", "--no-pager", "log", "--oneline", f"{initial_tag}..{final_tag}"],
        bufsize=0,
        stdout=subprocess.PIPE,
    )
    release_notes = ReleaseNotes(
        breaking_changes=[], bug_fixes=[], new_features=[], other=[]
    )
    while True:
        line = git_output.stdout.readline().decode("utf-8")
        if not line:
            break
        # Remove commit SHA
        line = line[(line.index(" ") + 1) :]
        if line.startswith("feat!:"):
            release_notes.breaking_changes.append(line)
        elif line.startswith("fix:"):
            release_notes.bug_fixes.append(line)
        elif line.startswith("feat:"):
            release_notes.new_features.append(line)
        else:
            release_notes.other.append(line)

    git_output.stdout.close()
    git_output.wait()
    print(release_notes.to_json())


if __name__ == "__main__":
    parse_git_log(sys.argv[1], sys.argv[2])
