Contains EEG data we've preprocessed and downsampled to 500Hz with BrainVision Analyzer v2.1 by hand. Specifically, we've corrected for artifacts created by the fMRI scanner. We've also done basic ballistic cardiogram correction, but later in the pipeline we'll scrub heartbeat artifacts further using ICA.

FILES
-----
- contrascan_workspace.wksp2: Run this with BrainVision Analyzer. Tracks what changes we make to each EEG file.

DIRECTORIES
-----------
- EXPORT: Contains EEG data for which we've removed heartbeat and fMRI artifacts.
- HISTORY: Used by BrainVision Analyzer to store the history of this dataset.
- RAW: The completely raw, unedited EEG data straight from the scanner.
