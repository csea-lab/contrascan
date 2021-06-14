#!/usr/bin/env python3
"""
This node doesn't do much. It simply commands you to run fMRIPrep on the data.

Created on 6/14/2021 by Benjamin Velie.
veliebm@gmail.com
"""
def main():
    """
    Command user to run fMRIPrep.
    """
    outputs_path = f"../outputs/{__name__}"
    exception_message = f"You must now manually run fMRIPrep on the data. After you run it, place its outputs in {outputs_path}"
    raise FileNotFoundError(exception_message)
