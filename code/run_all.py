6#!/usr/bin/env python3
"""
The master script. Run this to run the entire analysis from beginning to end.

Created on 6/11/2021 by Benjamin Velie.
veliebm@gmail.com
"""
# Import external modules.
from os import PathLike
from pathlib import Path
from typing import Dict
import yaml

# Import local modules.
import bids
import fmriprep

def main():
    """
    Drives our entire analysis.

    A node can be any python module that contains a .main() function.
    """
    run_node(bids)
    run_node(fmriprep)

def run_node(node) -> None:
    """
    Runs a node in our pipeline.
    """
    name = node.__name__
    _check_inputs(name)
    already_run = _check_already_run(name)

    if already_run:
        print(f"Skipping node '{name}' because it has already run")
    else:
        print(f"Running node '{name}'")
        node.main()

def _check_inputs(name_of_node: str) -> None:
    """
    Raises an exception if required files for this node are not present.
    """
    all_requirements = read_yaml("inputs.yaml")
    requirements = all_requirements[name_of_node]
    for path_template in requirements:
        paths = tuple(Path().glob(path_template))

        if paths == ():
            raise FileNotFoundError(f"Can't find any paths matching {path_template} but {name_of_node} requires them")

        for path in paths:
            if not path.exists():
                raise FileNotFoundError(f"Can't find {path} but {name_of_node} requires it")

def _check_already_run(name_of_node: str) -> bool:
    """
    Check if a node has run before.
    """
    directory = Path(f"../outputs/{name_of_node}")

    already_run = False
    if directory.exists():
        already_run = True

    return already_run

def read_yaml(path: PathLike) -> Dict:
    """
    Decode a yaml file.
    """
    with open(path, "r") as io:
        return yaml.load(io, Loader=yaml.UnsafeLoader)

if __name__ == "__main__":
    main()
