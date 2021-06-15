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
from log import logged

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
    node_name = node.__name__
    log_name = f"../documentation/logs/{node_name}_log.yaml"
    _test_inputs(node_name)
    should_run = _check_should_run(log_name)

    if not should_run:
        print(f"Skipping node '{node_name}' because it has already run without raising an exception")
    else:
        print(f"Running node '{node_name}' because it hasn't run without raising an exception")
        run = logged(log_name)(node.main)
        run()

def _test_inputs(name_of_node: str) -> None:
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

def _check_should_run(log_of_node: str) -> bool:
    """
    Determines whether a node should run or not.
    """
    log_of_node = Path(log_of_node)

    should_run = True

    if log_of_node.exists():
        data_from_log = read_yaml(log_of_node)
        if data_from_log["Exception"] == None:
            should_run = False

    return should_run

def read_yaml(path: PathLike) -> Dict:
    """
    Decode a yaml file.
    """
    with open(path, "r") as io:
        return yaml.load(io, Loader=yaml.UnsafeLoader)

if __name__ == "__main__":
    main()
