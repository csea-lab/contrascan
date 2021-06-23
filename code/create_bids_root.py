#!/usr/bin/env python3
"""
Create the root of our BIDS dataset.
"""
# Import external modules and libraries.
import json
from os import PathLike
from pathlib import Path
from typing import Dict

def main(bids_dir: PathLike):
    """
    Create the root of our BIDS dataset.
    """
    bids_dir = Path(bids_dir).resolve()
    bids_dir.mkdir(parents=True, exist_ok=True)

    description_path = bids_dir / "dataset_description.json"
    write_dataset_description(description_path)

    return _serialize_dict({
        "bids root": bids_dir,
        "dataset description": description_path,
    })

def write_dataset_description(out_path: PathLike):
    """
    Writes the dataset description for the dataset.

    Parameters
    ----------
    file_dataframe : DataFrame
        DataFrame created by organize_files() containing metadata about each file
    """
    # Prepare a dict to write to json.
    description_dict = {
        "Name": "Contrascan dataset",
        "BIDSVersion": "1.4.0",
        "Authors": ["Benjamin Velie", "Maeve Boylan", "Kiersten Riels", "Wendel Friedl", "Andreas Keil"]
    }

    # Write the json.
    with open(out_path, "w") as out_file:
        json.dump(description_dict, out_file, indent="\t")

def _serialize_dict(dict1: Dict) -> Dict:
    """
    Make dict serializeable.
    """
    return {str(key): str(value) for key, value in dict1.items()}
