#!/usr/bin/env python3
"""
Use afni_proc.py to preprocess and deconvolve our data. Later, we'll compare our afni_proc.py outputs with our fMRIPrep outputs.

Created on 6/14/2021 by Benjamin Velie.
veliebm@gmail.com
"""
# Import external libraries and modules.
from os import PathLike
from pathlib import Path
from typing import Dict, List
import yaml
import subprocess

# Import CSEA libraries and modules.
from vmrk import Vmrk

def main(subjects: List[str]):
    """
    Preprocesses specified subjects using afni_proc.py.
    """
    bids_directory = Path("../outputs/bids").resolve()

    for subject in subjects:
        path_to_vmrk = bids_directory / f"sub-{subject}/eeg/sub-{subject}_task-contrascan_eeg.vmrk"
        path_to_func = bids_directory / f"sub-{subject}/func/sub-{subject}_task-contrascan_bold.nii"
        path_to_anat = bids_directory / f"sub-{subject}/anat/sub-{subject}_T1w.nii"
        out_directory = Path(f"../outputs/{__name__}/sub-{subject}").resolve()
        preprocess(out_directory, path_to_func, path_to_anat, path_to_vmrk, subject, remove_first_trs=1)

def preprocess(out_directory: PathLike, path_to_func: PathLike, path_to_anat: PathLike, path_to_vmrk: PathLike, subject_id: str, remove_first_trs: int):
    """
    Preprocess a bopscanner subject using afni_proc.py.
    """
    # Get Path objects we'll need.
    out_directory = Path(out_directory).resolve()
    if not out_directory.exists():
        out_directory.mkdir(parents=True)
    path_to_vmrk = Path(path_to_vmrk).resolve()
    path_to_func = Path(path_to_func).resolve()
    path_to_anat = Path(path_to_anat).resolve()

    # Get onset times and write them to their own text file. For each TR we remove, we should subtract 2s from all onsets.
    path_to_onsets = out_directory / "onsets.tsv"
    vmrk_file = Vmrk(path_to_vmrk)
    onset_adjustment = -remove_first_trs*2
    vmrk_file.write_onsets_to(path_to_onsets, add_to_onsets=onset_adjustment)

    # Run afni_proc.py. Need path to func dataset, subject ID, path to anat dataset, path to onsets in text file, and number of TRs to remove from beginning of scan.
    run_afni_proc(subject_id, path_to_anat, path_to_func, path_to_onsets, out_directory, remove_first_trs)

def run_afni_proc(subject_id: str, path_to_anat: PathLike, path_to_func: PathLike, path_to_onsets: PathLike, out_directory: PathLike, remove_first_trs: int) -> None:
    """
    Runs afni_proc.py for the specified subject. It'll preprocess and deconvolve everything for you.

    afni_proc.py help: https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/programs/afni_proc.py_sphx.html#ahelp-afni-proc-py
    """
    arguments = f"""
        afni_proc.py
        -regress_stim_times {path_to_onsets}
        -dsets {path_to_func}
        -subj_id {subject_id}
        -copy_anat {path_to_anat}
        -blocks tshift align tlrc volreg blur mask scale regress
        -tcat_remove_first_trs {remove_first_trs}
        -align_opts_aea
        -cost lpc+ZZ
        -giant_move
        -check_flip
        -tlrc_base TT_N27+tlrc
        -tlrc_NL_warp
        -volreg_align_to MIN_OUTLIER
        -volreg_align_e2a
        -volreg_tlrc_warp
        -blur_size 4.0
        -regress_stim_labels stim
        -regress_basis CSPLINzero(0,18,10)
        -regress_opts_3dD
        -jobs 4
        -regress_motion_per_run
        -regress_censor_motion 0.3
        -regress_censor_outliers 0.05
        -regress_reml_exec
        -regress_compute_fitts
        -regress_make_ideal_sum sum_ideal.1D
        -regress_est_blur_epits
        -regress_est_blur_errts
        -regress_run_clustsim no
        -execute
    """.split()

    subprocess.run(arguments, cwd=out_directory)

def read_yaml(path: PathLike) -> Dict:
    """
    Decode a yaml file.
    """
    with open(path, "r") as io:
        return yaml.load(io, Loader=yaml.UnsafeLoader)
