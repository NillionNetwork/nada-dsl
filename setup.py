from setuptools import setup
import os


# VERSION GENERATION
# This script is run multiple times for any wheels in temp folders
# We only want `version.py` to be created once.
if not os.path.isfile("./nada_dsl/version.py"):
    commit = os.popen("git rev-parse HEAD").read().rstrip()
    print(f"COMMIT: {commit}")
    with open("./nada_dsl/version.py", "w", encoding="utf-8") as f:
        f.write(f"print('nada_dsl {commit}')")

setup()
