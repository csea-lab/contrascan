#!/usr/bin/env python3
"""
Let's build us a pipeline.

Created 6/22/21 by Benjamin Velie.
"""
# Import external libraries and modules.
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List
import json
import collections
import six

# Import homemade libraries and modules.
import create_bids_root
import bidsify_subject
import afniproc

DOIT_CONFIG = {
    "verbosity": 2,
    "num_process": 8, 
    "subject ids": "104 106 107 108 109 110 111 112 113 115 116 117 120 121 122 123 124 125".split()
}

def task_create_bids_root():
    """
    Create the root of our bids dataset. We'll finish BIDSifiying the data when we add our individual subjects to the dataset.
    """
    bids_dir = Path("../outputs/bids")

    action = create_bids_root.main
    args = [bids_dir]
    file_dep = ["create_bids_root.py"]
    targets = [bids_dir / "dataset_description.json"]

    return {
        "actions": [(action, make_json_compatible(args), {})],
        "file_dep": make_json_compatible(file_dep),
        "targets": make_json_compatible(targets),
    }

def task_bidsify_subject():
    """
    Convert all subjects to BIDS format.

    We'll need this for fMRIPrep. Also, when we submit our dataset to the NIH, they'll want it in BIDS format.
    """
    action = bidsify_subject.main
    bids_dir = Path("../outputs/bids").resolve()

    for id in DOIT_CONFIG["subject ids"]:
        old_subject_dir = Path(f"../raw/subjects-complete/sub-{id}").resolve()
        sources = {
            "eeg": old_subject_dir / f"contrascan_{id}.eeg",
            "vhdr": old_subject_dir / f"contrascan_{id}.vhdr",
            "vmrk": old_subject_dir / f"contrascan_{id}.vmrk",
            "func": the_path_that_matches(f"Keil_{id}_*EPI_2s_Gain_*_1.nii", old_subject_dir),
            "anat": the_path_that_matches(f"Keil_{id}_*sT1W_3D_FFE_SAG_*_1.nii", old_subject_dir),
            "dat": old_subject_dir / f"SFcontrascan_{id}.dat",
        }
        targets = {
            "anat": bids_dir / f"sub-{id}/anat/sub-{id}_T1w.nii",
            "eeg":  bids_dir / f"sub-{id}/eeg/sub-{id}_task-contrascan_eeg.eeg",
            "vmrk": bids_dir / f"sub-{id}/eeg/sub-{id}_task-contrascan_eeg.vmrk",
            "vhdr": bids_dir / f"sub-{id}/eeg/sub-{id}_task-contrascan_eeg.vhdr",
            "func metadata": bids_dir / f"sub-{id}/func/sub-{id}_task-contrascan_bold.json",
            "func": bids_dir / f"sub-{id}/func/sub-{id}_task-contrascan_bold.nii",
            "events": bids_dir / f"sub-{id}/func/sub-{id}_task-contrascan_events.tsv",
            "dat": bids_dir / f"sourcedata/sub-{id}_task-contrascan.dat",
        }
        sources_json = make_json_compatible(sources)
        targets_json = make_json_compatible(targets)

        yield {
            "basename": f"bidsify {id}",
            "actions": [(action, ([{"sources": sources_json, "targets": targets_json}]), {})],
            "file_dep": tuple(sources_json.values()),
            "targets": tuple(targets_json.values()),
        }

def task_afniproc():
    """
    Run afni_proc.py to preprocess and deconvolve our subjects.

    This is the base of our pipeline. We'll use the outputs of afni_proc.py for our more advanced analyses.
    """
    action = afniproc.main

    for id in DOIT_CONFIG["subject ids"]:
        in_dir = Path(f"../outputs/bids/sub-{id}").resolve()
        out_dir = Path(f"../outputs/afniproc/sub-{id}").resolve()
        kwargs = {
            "vmrk_path": in_dir / f"eeg/sub-{id}_task-contrascan_eeg.vmrk",
            "func_path": in_dir / f"func/sub-{id}_task-contrascan_bold.nii",
            "anat_path": in_dir / f"anat/sub-{id}_T1w.nii",
            "out_dir": out_dir,
            "subject_id": id,
            "remove_first_trs": 1,
        }
        
        file_dep = [kwargs["vmrk_path"], kwargs["func_path"], kwargs["anat_path"]]
        targets = {
            "log": out_dir / f"output.proc.{id}",
            "command": out_dir / f"proc.{id}",
            "stats head": out_dir / f"{id}.results/stats.{id}+tlrc.HEAD",
            "stats brik": out_dir / f"{id}.results/stats.{id}+tlrc.BRIK",
            "IRF head": out_dir / f"{id}.results/iresp_stim.{id}+tlrc.HEAD",
            "IRF brik": out_dir / f"{id}.results/iresp_stim.{id}+tlrc.BRIK",
            "anat head": out_dir / f"{id}.results/anat_final.{id}+tlrc.HEAD",
            "anat brik": out_dir / f"{id}.results/anat_final.{id}+tlrc.BRIK",
        }

        yield {
            "basename": f"afniproc {id}",
            "actions": [(action, (), make_json_compatible(kwargs))],
            "file_dep": make_json_compatible(file_dep),
            "targets": make_json_compatible(list(targets.values())),
        }

def make_json_compatible(data: Any) -> Any:
    """
    Makes your data json compatible. How? It converts any non-serializable object into a string.

    Also, it converts non-dict/non-string iterables to lists.
    If you're fixing nested structures, this will probably only work for shallow ones.
    """
    def is_iterable(data: Any) -> bool:
        """
        Returns true if an object is an iterable but not a string.
        """
        return isinstance(data, collections.Iterable) and not isinstance(data, six.string_types)
    def is_jsonable(item: Any) -> bool:
        """
        Returns true if an object is json serializable.
        """
        try:
            json.dumps(item)
            return True
        except (TypeError, OverflowError):
            return False
    def fix_dict(dictionary: Dict) -> Dict:
        """
        Make a dict json_serializable.

        Converts all non-serializable items into strings.
        """
        new_dict = {}
        for key, value in dictionary.items():
            if not is_jsonable(key):
                key = str(key)
            if not is_jsonable(value):
                value = str(value)

            new_dict[key] = value            
        
        return new_dict
    def fix_iterable(list1: List) -> List:
        """
        Make an iterable into a json serializable list.

        Converts all non-serializable items into strings.
        """
        fixed_list = []

        for item in list1:
            if is_jsonable(item):
                fixed_list.append(item)
            else:
                fixed_list.append(str(item))

        return fixed_list

    fixed_data = None

    if is_jsonable(data):
        fixed_data = data
    elif type(data) == dict:
        fixed_data = fix_dict(data)
    elif is_iterable(data):
        fixed_data = fix_iterable(data)
    
    return fixed_data

def the_path_that_matches(pattern: str, in_directory: PathLike) -> Path:
    """
    Finds one and only one path matching the specified pattern. Raises an error if it finds 2+ paths or no paths.

    To learn how to use advanced patterns, read http://www.robelle.com/smugbook/wildcard.html

    Parameters
    ----------
    pattern : str
        Pattern to search for.
    in_directory : str or Path
        Directory in which to search for the pattern.

    Returns
    -------
    Path
        Path found by search.

    Raises
    ------
    IOError
        If it finds 2+ paths.
    FileNotFoundError
        If it finds no paths.
    NotADirectoryError
        If in_directory isn't a directory.
    """

    matches = list(Path(in_directory).glob(pattern))

    if not Path(in_directory).is_dir():
        raise NotADirectoryError(f"{in_directory} either doesn't exist or isn't a directory at all!")

    elif(len(matches)) > 1:
        raise IOError(f"The directory {in_directory} exists but contains more than one path that matches '{pattern}': {matches}")

    elif(len(matches)) == 0:
        raise FileNotFoundError(f"The directory {in_directory} exists but contains no paths that match pattern '{pattern}'")
    
    else:
        return matches[0]
