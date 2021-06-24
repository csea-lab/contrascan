#!/usr/bin/env python3
"""
This node doesn't do much. It simply commands you to run fMRIPrep on the data.

Created on 6/14/2021 by Benjamin Velie.
veliebm@gmail.com
"""
# Import external modules and libraries.
from os import PathLike
from pathlib import Path

def main(fmriprep_dir: PathLike):
    """
    Command user to run fMRIPrep.
    """
    fmriprep_dir = Path(fmriprep_dir)
    if fmriprep_dir.exists():
        print(f"Detected {fmriprep_dir}")
    else:
        exception_message = f"You must now manually run fMRIPrep on the data. After you run it, place its outputs in {fmriprep_dir}"
        raise FileNotFoundError(exception_message)
