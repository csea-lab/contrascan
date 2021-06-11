Our raw EEG data is really messy. We have to do lots of stuff to clean it. The first thing we need to do manually import the data into BrainVision analyzer, which we use to:
* Remove heartbeat artifacts (though not completely)
* Remove artifacts created by the electromagnetic behemoth that is the fMRI machine

FILES
-----
* contrascan_workspace.wksp2: Run this with BrainVision Analyzer. We save stuff we do in BrainVision Analyzer using this file.

DIRECTORIES
-----------
* output: Contains EEG data for which we've removed heartbeat and fMRI artifacts.
* temp: Used by BrainVision Analyzer to store the history of this dataset.
* input: The completely raw, unedited EEG data straight from the scanner.

Last edited 6/11/2021