#!/usr/bin/env python3
"""
Let's build us a pipeline.

Created 6/22/21 by Benjamin Velie.
"""
# Import external libraries and modules.
from os import PathLike
from pathlib import Path
from typing import Dict, List

# Import homemade libraries and modules.
import create_bids_root
import bidsify_subject

DOIT_CONFIG = {
    "verbosity": 2,
    "subject ids": "104 106 107 108 109 110 111 112 113 115 116 117 120 121 122 123 124 125".split()
}

def task_create_bids_root():
    """
    Create the root of our bids dataset.
    """
    bids_dir = Path("../outputs/bids")

    action = create_bids_root.main
    args = [bids_dir]
    kwargs = {}
    file_dep = ["create_bids_root.py"]
    targets = [bids_dir / "dataset_description.json"]

    return {
        "actions": [(action, _serialize_list(args), _serialize_dict(kwargs))],
        "file_dep": _serialize_list(file_dep),
        "targets": _serialize_list(targets),
    }

def task_bidsify_subject():
    """
    Convert a subject to BIDS format.
    """
    action = bidsify_subject.main
    bids_dir = Path("../outputs/bids").resolve()

    for id in DOIT_CONFIG["subject ids"]:
        old_subject_dir = Path(f"../raw/subjects-complete/sub-{id}").resolve()
        sources = {
            "script": "bidsify_subject.py",
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
        sources_json = _serialize_dict(sources)
        targets_json = _serialize_dict(targets)

        yield {
            "basename": f"bidsify {id}",
            "actions": [(action, ([{"sources": sources_json, "targets": targets_json}]), {})],
            "file_dep": tuple(sources_json.values()),
            "targets": tuple(targets_json.values()),
        }

def _serialize_list(list1: List) -> List:
    """
    Make list serializable.
    """
    return [str(item) for item in list1]

def _serialize_dict(dict1: Dict) -> Dict:
    """
    Make dict serializeable.
    """
    return {str(key): str(value) for key, value in dict1.items()}

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
