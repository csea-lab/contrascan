#!/usr/bin/env python3
"""
After running fMRIPrep, run this node to clean its results further then deconvolve them.

Created 11/16/2020 by Benjamin Velie.
Last updated 6/17/2021 by Benjamin Velie.
veliebm@gmail.com
"""
# Import external modules and libraries.
from os import PathLike
from pathlib import Path
import shutil
from typing import List
import pandas
import subprocess

def main(subject_ids: List[str]) -> None:
    """
    After running fMRIPrep, run this node to clean its results further then deconvolve them.
    """
    regressors = "csf csf_derivative1 csf_power2 csf_derivative1_power2 white_matter white_matter_derivative1 white_matter_derivative1_power2 white_matter_power2 csf_wm trans_x trans_x_derivative1 trans_x_power2 trans_x_derivative1_power2 trans_y trans_y_derivative1 trans_y_derivative1_power2 trans_y_power2 trans_z trans_z_derivative1 trans_z_derivative1_power2 trans_z_power2 rot_x rot_x_derivative1 rot_x_power2 rot_x_derivative1_power2 rot_y rot_y_derivative1 rot_y_power2 rot_y_derivative1_power2 rot_z rot_z_derivative1 rot_z_power2 rot_z_derivative1_power2".split()
    bids_dir = Path("../outputs/bids").resolve()

    for subject_id in subject_ids:
        output_dir = Path(f"../outputs/{__name__}/sub-{subject_id}").resolve()
        fmriprep_dir = Path(f"../outputs/fmriprep/sub-{subject_id}/fmriprep/sub-{subject_id}").resolve()

        inputs = {
            "anat_image": fmriprep_dir / f"anat/sub-{subject_id}_space-MNI152NLin2009cAsym_desc-preproc_T1w.nii.gz",
            "events_tsv": bids_dir / f"sub-{subject_id}/func/sub-{subject_id}_task-contrascan_events.tsv",
            "func_mask": fmriprep_dir / f"func/sub-{subject_id}_task-gabor_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz",
            "regressors_tsv": fmriprep_dir / f"func/sub-{subject_id}_task-gabor_desc-confounds_timeseries.tsv",
            "func_image": fmriprep_dir / f"func/sub-{subject_id}_task-gabor_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz",
        }
        for input in inputs.values():
            _test_path_exists(input)

        # Run steps of analysis.
        func_smoothed = merge(output_dir, inputs["func_image"], subject_id)
        func_means = tstat(output_dir, func_smoothed, subject_id)
        func_scaled = calc(output_dir, func_smoothed, func_means, subject_id)
        deconvolve(output_dir, inputs["anat_image"], func_scaled, inputs["events_tsv"], inputs["regressors_tsv"], regressors, subject_id)
        #remlfit()

def _test_path_exists(path: PathLike) -> None:
    """
    Raises FileNotFoundError if path doesn't exist.
    """
    path = Path(path)
    try:
        assert path.exists()
    except AssertionError:
        raise FileNotFoundError(f"{path} doesn't exist")

def merge(output_dir: Path, path_to_func: Path, subject_id: str) -> Path:
    """
    Smooths a functional image.

    3dmerge info: https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/programs/3dmerge_sphx.html#ahelp-3dmerge
    """
    working_dir = output_dir / "3dmerge"
    working_dir.mkdir(parents=True, exist_ok=True)

    prefix = f"sub-{subject_id}_bold_smoothed"
    outfile = working_dir / f"{prefix}+tlrc.HEAD"

    command = f"""
        3dmerge
        -1blur_fwhm 4.0
        -doall
        -prefix {prefix}
        {path_to_func}
    """.split()
    subprocess.run(command, cwd=working_dir)

    _test_path_exists(outfile)
    return outfile

def tstat(output_dir: Path, smoothed_func: Path, subject_id: str) -> Path:
    """
    Get the mean of each voxel in a functional dataset.

    3dTstat info: https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/programs/3dTstat_sphx.html#ahelp-3dtstat
    """
    working_dir = output_dir / "3dTstat"
    working_dir.mkdir(parents=True, exist_ok=True)

    prefix = f"sub-{subject_id}_bold_mean"
    outfile = working_dir / f"{prefix}+tlrc.HEAD"

    command = f"""
        3dTstat
        -prefix {prefix}
        {smoothed_func}
    """.split()
    subprocess.run(command, cwd=working_dir)

    _test_path_exists(outfile)
    return outfile

def calc(output_dir: Path, smoothed_func: Path, func_means: Path, subject_id: str) -> Path:
    """
    For each voxel in a smoothed func image, calculate the voxel as percent of the mean.

    3dcalc info: https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/programs/3dcalc_sphx.html#ahelp-3dcalc
    """
    program = "3dcalc"
    working_dir = output_dir / program
    working_dir.mkdir(parents=True, exist_ok=True)
    
    prefix = f"sub-{subject_id}_bold_scaled"
    outfile = working_dir / f"{prefix}+tlrc.HEAD"

    command = f"""
        {program}
        -float
        -a {smoothed_func}
        -b {func_means}
        -expr ((a-b)/b)*100
        -prefix {prefix}
    """.split()
    subprocess.run(command, cwd=working_dir)

    _test_path_exists(outfile)
    return outfile

def deconvolve(output_dir: Path, anat_path: Path, func_scaled: Path, events_tsv: Path, regressors_tsv: Path, regressors: List[str], subject_id: str) -> List[Path]:
    """
    Runs a within-subject analysis on a smoothed functional image.

    Returns a tuple of paths to outfiles: (bucket, IRF)

    3dDeconvolve info: https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/programs/3dDeconvolve_sphx.html#ahelp-3ddeconvolve
    """
    # Prepare our directories.
    program = "3dDeconvolve"
    working_dir = output_dir / program
    events_dir = output_dir / "temp" / "events"
    regressors_dir = output_dir / "temp" / "regressors-all"
    for dir in (working_dir, regressors_dir, events_dir):
        dir.mkdir(parents=True, exist_ok=True)

    # Name our outfiles.
    bucket_prefix = f"sub-{subject_id}_bold_deconvolved"
    IRF_prefix = f"sub-{subject_id}_bold_IRF"
    out_files = (
        working_dir / f"{bucket_prefix}+tlrc.HEAD",
        working_dir / f"{IRF_prefix}+tlrc.HEAD",
    )

    # Prepare text files to use with 3dDeconvolve.
    _split_columns_into_text_files(events_tsv, events_dir)
    _split_columns_into_text_files(regressors_tsv, regressors_dir)
    onsets_path = events_dir / "onset.txt"

    # Total amount of regressors to include in the analysis.
    amount_of_regressors = 1 + len(regressors)

    # Create list of arguments to pass to 3dDeconvolve.
    command = f"""
        {program}
        -input {func_scaled}
        -GOFORIT 4
        -polort A
        -fout
        -bucket {bucket_prefix}
        -num_stimts {amount_of_regressors}
        -stim_times 1 {onsets_path} CSPLINzero(0,18,10)
        -stim_label 1 all
        -iresp 1 {IRF_prefix}
    """.split()

    # Add individual stim files to the string.
    for i, regressor in enumerate(regressors):
            stim_number = i + 2
            stim_file_info = f"-stim_file {stim_number} {regressors_dir/regressor}.txt -stim_base {stim_number}"
            stim_label_info = f"-stim_label {stim_number} {regressor}"
            command += stim_file_info.split() + stim_label_info.split()
    
    subprocess.run(command, cwd=working_dir)

    # Copy anatomy file into working directory to use with AFNI viewer.
    shutil.copyfile(src=anat_path, dst=working_dir / anat_path.name)

    for path in out_files:
        _test_path_exists(path)
    return out_files

def remlfit():
        """
        Runs a 3dREMLfit within-subject analysis on a smoothed functional image using a matrix created by 3dDeconvolve.

        3dREMLfit info: https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/programs/3dREMLfit_sphx.html#ahelp-3dremlfit
        """

        working_directory = dirs["output"] / f"task-{task_name}" / "3dREMLfit"

        # Create the list of arguments to pass to 3dREMLfit.
        args = f"""
                -matrix {results[task_name]["3dDeconvolve"].matrix}
                -input {results[task_name]["3dcalc"].outfile}
                -fout 
                -tout
                -Rbuck sub-{subject_id}_task-{task_name}_bold_reml_stats
                -Rvar sub-{subject_id}_task-{task_name}_bold_reml_varianceparameters
                -verb

        """.split()

        # Run 3dREMLfit.
        results = AFNI(program="3dREMLfit", args=args, working_directory=working_directory)

        # Copy anatomy file into working directory to use with AFNI viewer.
        shutil.copyfile(src=anat_path, dst=working_directory / anat_path.name)

        return results

def _split_columns_into_text_files(tsv_path, output_dir) -> None:
    """
    Converts a tsv file into a collection of text files.

    Each column name becomes the name of a text file. Each value in that column is then
    placed into the text file. Don't worry - this won't hurt your .tsv file, which will lay
    happily in its original location.

    Parameters
    ----------
    tsv_path : str or Path
            Path to the .tsv file to break up.
    output_dir : str or Path
        Directory to write columns of the .tsv file to.
    """
    # Alert the user and prepare our paths.
    tsv_path = Path(tsv_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(exist_ok=True, parents=True)
    print(f"Storing the columns of {tsv_path.name} as text files in directory {output_dir}")

    # Read the .tsv file into a DataFrame and fill n/a values with zero.
    tsv_info = pandas.read_table(tsv_path, sep="\t", na_values="n/a").fillna(value=0)

    # Write each column of the dataframe as a text file.
    for column_name in tsv_info:
        column_path = output_dir / f"{column_name}.txt"
        tsv_info[column_name].to_csv(column_path, sep=' ', index=False, header=False)
