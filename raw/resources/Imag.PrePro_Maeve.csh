#!/usr/bin/env tcsh
# --------------------------------------------------
set info=`cat MRISub.Info3.txt`
foreach ln ($info)
echo $ln
set sub=`echo $ln | cut -d "z" -f1`
set ord=`echo $ln | cut -d "z" -f2`
set imgfile1=`echo $ln | cut -d "z" -f3`
set imgfile2=`echo $ln | cut -d "z" -f4`
set strucfile=`echo $ln | cut -d "z" -f5`

echo $sub
echo $ord
echo $strucfile
cd KEIL_$sub

3dTcat -prefix "$sub"_cat $imgfile1 $imgfile2

set info2="$sub"_catz
echo $info2
set imgfile=`echo $info2 | cut -d "z" -f1`
echo $imgfile

3dcopy $strucfile "$sub".struc+orig
3dcopy $imgfile "$sub".image+orig
# align the epi data to the anatom
align_epi_anat.py -anat "$sub".struc+orig -epi "$sub".image+orig -epi_base 10
# tlrc anatomy for later use
@auto_tlrc -no_ss -base TT_N27+tlrc -input $sub.struc_al+orig 
# Get skull mask 
3dcalc -a $sub.struc_al+orig -expr 'step(a)'  -prefix $sub.tmp_mask+orig
3dresample -master $sub.image+orig -prefix $sub.skull_al_mask -inset $sub.tmp_mask+orig
rm $sub.tmp*
# Start PreProcessing Steps
#  r1: do slice time correction
 3dTshift -tzero 0 -tpattern alt+z -quintic -prefix r1.$sub.image.tshift      \
            $sub.image+orig
# -------------------------------------------------------
# r2: align each dset to the base volume using same image as used in align epi to anat...
    3dvolreg -verbose -zpad 1 -base r1.$sub.image.tshift+orig'[10]'  \
              -1Dfile $sub.image.Motion.1D -prefix r2.$sub.image.volreg  \
              r1.$sub.image.tshift+orig
# -------------------------------------------------------
# r3: blur each volume; for inplane 2.5 use 5 fwhm --- 2x times inplane is best
    3dmerge -1blur_fwhm 5.0 -doall -prefix r3.$sub.image.blur  r2.$sub.image.volreg+orig
# -------------------------------------------------------
# Get the mean for each of n slices for each timepoint to check on residual motion
# Save the means in the sliceavg file
# Save the plot in a jpg file
3dROIstats -mask '3dcalc(-a '$sub'.skull_al_mask+orig -expr a*(k+1) -datum short -nscale)' -quiet r2.$sub.image.volreg+orig > $sub.image.sliceavg.1D
#1dplot -one $sub.sliceavg.1d
 1dplot -one -jpg $sub.image.sliceavg.jpg $sub.image.sliceavg.1D
# -------------------------------------------------------  
# Get the mean outliers over each of N slices for each timepoint 
# Save the means in the outlier files and the plot in a jpg file
3dToutcount -mask '3dcalc(-a  '$sub'.skull_al_mask+orig -expr a*(k+1) -datum short -nscale)' -fraction r2.$sub.image.volreg+orig > $sub.image.WholeBrainF.outliers.1D
#1dplot -one $sub.outliers.1D
1dplot -jpg $sub.image.WholeBrainF.outliers.jpg $sub.image.WholeBrainF.outliers.1D
 # -------------------------------------------------------  
 # Flag trials with more outliers than threshold (here, 5%)
1deval -a $sub.image.WholeBrainF.outliers.1D -expr 'step(.05-a)' > $sub.image.WholeBrainF.Censor.1D
# -------------------------------------------------------  
# scale each voxel time series so 0=no change, > 0 increase signal, <0 decrease signal
# a= original data b=mean of voxel over timeseries , 10 & 5 = 10-5/10=.5 x 100=50%
     3dTstat -prefix $sub.image.mean r3.$sub.image.blur+orig
     3dcalc -float -a r3.$sub.image.blur+orig -b $sub.image.mean+orig  \
          -c $sub.skull_al_mask+orig                              \
         -expr 'c *(((a-b)/b)*100)'                        \
         -prefix r4.$sub.image.scale

#
# Get IRFs
#
3dDeconvolve -input r4."$sub".image.scale+orig.HEAD          \
    -polort A           \
    -GOFORIT 4     \
    -censor "$sub".image.WholeBrainF.Censor.1D			\
    -num_stimts 15                   \
    -stim_times 1 O"$ord".ero.txt 'CSPLINzero(0,30,11)'               \
    -stim_label 1 ero			\
      -stim_times 2 O"$ord".neu.txt 'CSPLINzero(0,30,11)'               \
    -stim_label 2 neu       \
      -stim_times 3 O"$ord".contam.txt 'CSPLINzero(0,30,11)'               \
    -stim_label 3 con       \
      -stim_times 4 O"$ord".PerPl.txt 'CSPLINzero(0,30,11)'               \
    -stim_label 4 ppl      \
      -stim_times 5 O"$ord".PerUn.txt 'CSPLINzero(0,30,11)'               \
    -stim_label 5 pun     \
     -stim_times 6 O"$ord".rew.txt 'CSPLINzero(0,30,11)'               \
    -stim_label 6 rew     \
      -stim_times 7 O"$ord".PerNeu.txt 'CSPLINzero(0,30,11)'               \
    -stim_label 7 pnu     \
     -stim_times 8 O"$ord".surv.txt 'CSPLINzero(0,30,11)'               \
    -stim_label 8 sur     \
     -stim_times 9 O"$ord".oth.txt 'CSPLINzero(0,30,11)'               \
    -stim_label 9 oth     \
    -stim_file 10 "$sub".image.Motion.1D'[0]' -stim_base 10 -stim_label 10 roll   \
    -stim_file 11 "$sub".image.Motion.1D'[1]' -stim_base 11 -stim_label 11 pitch  \
    -stim_file 12 "$sub".image.Motion.1D'[2]' -stim_base 12 -stim_label 12 yaw    \
    -stim_file 13 "$sub".image.Motion.1D'[3]' -stim_base 13 -stim_label 13 dS     \
    -stim_file 14 "$sub".image.Motion.1D'[4]' -stim_base 14 -stim_label 14 dL     \
    -stim_file 15 "$sub".image.Motion.1D'[5]' -stim_base 15 -stim_label 15 dP  \
    -jobs 2   		 \
    -fout							\
    -iresp 1 "$sub".image.CSPLINz.ero.IRF						\
    -iresp 2 "$sub".image.CSPLINz.neu.IRF					\
    -iresp 3 "$sub".image.CSPLINz.con.IRF					\
    -iresp 4 "$sub".image.CSPLINz.ppl.IRF					\
    -iresp 5 "$sub".image.CSPLINz.pun.IRF					\
    -iresp 6 "$sub".image.CSPLINz.rew.IRF					\
    -iresp 7 "$sub".image.CSPLINz.pnu.IRF					\
    -iresp 8 "$sub".image.CSPLINz.sur.IRF					\
    -bucket "$sub".image.CSPLINz.8Cat.stats
    
3dDeconvolve -input r4."$sub".image.scale+orig.HEAD          \
    -polort A           \
    -GOFORIT 4     \
    -censor "$sub".image.WholeBrainF.Censor.1D			\
    -num_stimts 7                   \
    -stim_times 1 O"$ord".all.txt 'CSPLINzero(0,30,11)'               \
    -stim_label 1 all			\
    -stim_file 2 "$sub".image.Motion.1D'[0]' -stim_base 2 -stim_label 2 roll   \
    -stim_file 3 "$sub".image.Motion.1D'[1]' -stim_base 3 -stim_label 3 pitch  \
    -stim_file 4 "$sub".image.Motion.1D'[2]' -stim_base 4 -stim_label 4 yaw    \
    -stim_file 5 "$sub".image.Motion.1D'[3]' -stim_base 5 -stim_label 5 dS     \
    -stim_file 6 "$sub".image.Motion.1D'[4]' -stim_base 6 -stim_label 6 dL     \
    -stim_file 7 "$sub".image.Motion.1D'[5]' -stim_base 7 -stim_label 7 dP  \
    -jobs 2   		 \
    -fout							\
    -iresp 1 "$sub".image.CSPLINz.all.IRF						\
    -bucket "$sub".image.CSPLINz.all.stats

@auto_tlrc -apar $sub.struc_al+tlrc -input $sub.image.CSPLINz.ero.IRF+orig -dxyz 2.5
@auto_tlrc -apar $sub.struc_al+tlrc -input $sub.image.CSPLINz.neu.IRF+orig -dxyz 2.5
@auto_tlrc -apar $sub.struc_al+tlrc -input $sub.image.CSPLINz.con.IRF+orig -dxyz 2.5
@auto_tlrc -apar $sub.struc_al+tlrc -input $sub.image.CSPLINz.ppl.IRF+orig -dxyz 2.5
@auto_tlrc -apar $sub.struc_al+tlrc -input $sub.image.CSPLINz.pun.IRF+orig -dxyz 2.5
@auto_tlrc -apar $sub.struc_al+tlrc -input $sub.image.CSPLINz.rew.IRF+orig -dxyz 2.5
@auto_tlrc -apar $sub.struc_al+tlrc -input $sub.image.CSPLINz.pnu.IRF+orig -dxyz 2.5
@auto_tlrc -apar $sub.struc_al+tlrc -input $sub.image.CSPLINz.sur.IRF+orig -dxyz 2.5
@auto_tlrc -apar $sub.struc_al+tlrc -input $sub.image.CSPLINz.8Cat.stats+orig -dxyz 2.5
@auto_tlrc -apar $sub.struc_al+tlrc -input $sub.image.CSPLINz.all.IRF+orig -dxyz 2.5

cd ..
end 
exit
