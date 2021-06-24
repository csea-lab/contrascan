#!/bin/tcsh

afni_proc.py 		                                          \
   -subj_id 107		                                    \
   -dsets Keil_107_EPI_2s_Gain_3_1.nii                      \
   -copy_anat Keil_107_sT1W_3D_FFE_SAG_2_1.nii              \
   -blocks tshift align tlrc volreg blur mask scale regress  \
   -tcat_remove_first_trs 1                                  \
   -align_opts_aea -cost lpc+ZZ -giant_move -check_flip      \
   -tlrc_base TT_N27+tlrc                                   \
   -tlrc_NL_warp                                             \
   -volreg_align_to MIN_OUTLIER                             \
   -volreg_align_e2a                                        \
   -volreg_tlrc_warp                                       \
   -blur_size 4.0                                           \
   -regress_stim_times Keil_107.onsetsmin2.txt             \
   -regress_stim_labels stim                             \
   -regress_basis 'CSPLINzero(0,14,8)'                    \
   -regress_opts_3dD -jobs 2                               \
   -regress_motion_per_run                                  \
   -regress_censor_motion 0.3                               \
   -regress_censor_outliers 0.05                            \
   -regress_3dD_stop                                        \
   -regress_reml_exec                                       \
   -regress_compute_fitts                                   \
   -regress_make_ideal_sum sum_ideal.1D                     \
   -regress_est_blur_epits                                  \
   -regress_est_blur_errts                                  \
   -regress_run_clustsim no                                 
