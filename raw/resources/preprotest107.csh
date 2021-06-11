#! /bin/tcsh
# align the epi data to the anatom
align_epi_anat.py -anat Keil_107.struc+orig -epi Keil_107.image+orig -epi_base 10
# tlrc anatomy for later uses
@auto_tlrc -no_ss -base TT_N27+tlrc -input Keil_107.struc_al+orig 
# Get skull mask 
3dcalc -a Keil_107.struc_al+orig -expr 'step(a)'  -prefix Keil_107.tmp_mask+orig
3dresample -master Keil_107.image+orig -prefix Keil_107.skull_al_mask -inset Keil_107.tmp_mask+orig
rm Keil_107.tmp*
# Start PreProcessing Steps
#  r1: do slice time correction
 3dTshift -tzero 0 -tpattern alt+z -quintic -prefix r1.Keil_107.image.tshift      \
            Keil_107.image+orig
# -------------------------------------------------------
# r2: align each dset to the base volume using same image as used in align epi to anat...
    3dvolreg -verbose -zpad 1 -base r1.Keil_107.image.tshift+orig'[10]'  \
              -1Dfile Keil_107.image.Motion.1D -prefix r2.Keil_107.image.volreg  \
              r1.Keil_107.image.tshift+orig
# -------------------------------------------------------
# r3: blur each volume; for inplane 2.5 use 5 fwhm --- 2x times inplane is best
    3dmerge -1blur_fwhm 5.0 -doall -prefix r3.Keil_107.image.blur  r2.Keil_107.image.volreg+orig
# -------------------------------------------------------
# Get the mean for each of n slices for each timepoint to check on residual motion
# Save the means in the sliceavg file
# Save the plot in a jpg file
3dROIstats -mask '3dcalc(-a Keil_107.skull_al_mask+orig -expr a*(k+1) -datum short -nscale)' -quiet r2.Keil_107.image.volreg+orig > Keil_107.image.sliceavg.1D
#1dplot -one $sub.sliceavg.1d
 1dplot -one -jpg Keil_107.image.sliceavg.jpg Keil_107.image.sliceavg.1D
# -------------------------------------------------------  
# Get the mean outliers over each of N slices for each timepoint 
# Save the means in the outlier files and the plot in a jpg file
3dToutcount -mask '3dcalc(-a  Keil_107.skull_al_mask+orig -expr a*(k+1) -datum short -nscale)' -fraction r2.Keil_107.image.volreg+orig > Keil_107.image.WholeBrainF.outliers.1D
#1dplot -one $sub.outliers.1D
1dplot -jpg Keil_107.image.WholeBrainF.outliers.jpg Keil_107.image.WholeBrainF.outliers.1D
 # -------------------------------------------------------  
 # Flag trials with more outliers than threshold (here, 5%)
1deval -a Keil_107.image.WholeBrainF.outliers.1D -expr 'step(.05-a)' > Keil_107.image.WholeBrainF.Censor.1D
# -------------------------------------------------------  
# scale each voxel time series so 0=no change, > 0 increase signal, <0 decrease signal
# a= original data b=mean of voxel over timeseries , 10 & 5 = 10-5/10=.5 x 100=50%
     3dTstat -prefix Keil_107.image.mean r3.Keil_107.image.blur+orig
     3dcalc -float -a r3.Keil_107.image.blur+orig -b Keil_107.image.mean+orig  \
          -c Keil_107.skull_al_mask+orig                              \
         -expr 'c *(((a-b)/b)*100)'                        \
         -prefix r4.Keil_107.image.scale

#
# Get IRFs
#
    
3dDeconvolve -input r4.Keil_107.image.scale+orig.HEAD          \
    -polort A           \
    -GOFORIT 4     \
    -censor Keil_107.image.WholeBrainF.Censor.1D			\
    -num_stimts 7                   \
    -stim_times 1 Keil_107.onsets.txt 'CSPLINzero(0,18,10)'               \
    -stim_label 1 all			\
    -stim_file 2 Keil_107.image.Motion.1D'[0]' -stim_base 2 -stim_label 2 roll   \
    -stim_file 3 Keil_107.image.Motion.1D'[1]' -stim_base 3 -stim_label 3 pitch  \
    -stim_file 4 Keil_107.image.Motion.1D'[2]' -stim_base 4 -stim_label 4 yaw    \
    -stim_file 5 Keil_107.image.Motion.1D'[3]' -stim_base 5 -stim_label 5 dS     \
    -stim_file 6 Keil_107.image.Motion.1D'[4]' -stim_base 6 -stim_label 6 dL     \
    -stim_file 7 Keil_107.image.Motion.1D'[5]' -stim_base 7 -stim_label 7 dP  \
    -jobs 2   		 \
    -fout							\
    -iresp 1 Keil_107.image.CSPLINz.all.IRF						\
    -bucket Keil_107.image.CSPLINz.all.stats

@auto_tlrc -apar Keil_107.struc_al+tlrc -input Keil_107.image.CSPLINz.all.IRF+orig -dxyz 2.5

cd ..
end 
exit
