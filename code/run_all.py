#!/usr/bin/env python3
"""
The master script. Run this to run the entire analysis from beginning to end.

Created on 6/11/2021 by Benjamin Velie.
veliebm@gmail.com
"""
# Import external modules.
from os import PathLike
import subprocess

def main():
    """
    Drives our entire analysis. Represents months of hard work.
    """
    run_node("check_raw.py")

def run_node(path_to_script: PathLike) -> None:
    """
    Runs a node in our pipeline.
    """
    command = ["python3", path_to_script]
    subprocess.run(command)

if __name__ == "__main__":
    main()
