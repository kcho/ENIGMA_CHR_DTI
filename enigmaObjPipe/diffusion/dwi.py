import numpy as np
import sys
import nibabel as nb
import pandas as pd
import argparse
from typing import Union, List
from pathlib import Path
import shutil
import tempfile
import os
from eddy_squeeze.eddy_squeeze_lib.eddy_files import EddyRun, EddyDirectories
from eddy_squeeze.eddy_squeeze_lib.eddy_web import create_html
from nifti_snapshot import nifti_snapshot

Num = Union[int, float]
Paths = Union[Path, str]


class DwiExtraction(object):
    '''Brain extraction methods'''
    def return_b0_indices(self) -> np.array:
        '''Return b0 indices'''
        bval_arr = np.loadtxt(self.diff_raw_bval)
        nodif_vol_indices = np.where(bval_arr < 10)[0]
        return nodif_vol_indices

    def get_nodif_num(self, return_first=True,
                      b0_num=None, b0_order=None) -> int:
        '''Return B0 number to extract

        Key arguments:
            return_first: return the index of the first b0, default=True
            b0_num: predefine the nodif_num, default=None
            b0_order: predefine the order of the b0, default=None

        Return:
            a integer
        '''
        if return_first:
            nodif_vol_indices = self.return_b0_indices()
            nodif_vol_index = nodif_vol_indices[0]
        elif b0_order is not None:
            nodif_vol_indices = self.return_b0_indices()
            nodif_vol_index = nodif_vol_indices[b0_order]
        else:
            if b0_num is not None:
                nodif_vol_index = b0_num
            else:
                nodif_vol_index = 0

        return nodif_vol_index

    def get_nodif(self):
        # if not self.diff_nodif.is_file():
        nodif_num = self.get_nodif_num()
        command = f'fslroi {self.diff_xc_dwi} {self.diff_nodif} {nodif_num} 1'

        if not self.diff_nodif.is_file() or self.force:
            self.run(command)

    def get_masked_nodif(self):
        # nodif_masked = self.diff_nodif.parent / \
                        # (self.diff_nodif.name.split('.')[0] +'_masked.nii.gz')
        command = f'fslmaths {self.diff_nodif} -mas {self.diff_mask} \
                {self.nodif_masked}'
        if not self.nodif_masked.is_file() or self.force:
            self.run(command)

    def get_nodif_raw(self):
        # if not self.diff_nodif.is_file():
        nodif_num = self.get_nodif_num()
        command = f'fslroi {self.diff_raw_dwi} {self.diff_nodif} {nodif_num} 1'

        if not self.diff_nodif.is_file() or self.force:
            self.run(command)

    def run_bet(self):
        command = f'bet {self.diff_nodif} {self.diff_mask} \
                -f 0.35 -m'

        if not self.diff_mask.is_file() or self.force:
            self.run(command)

            # FSL BET creates masked and mask file
            # mask file name gets '_masked' attached 
            # at the end of it's given input
            shutil.move(
                    self.diff_mask,
                    self.diff_nodif.parent / \
                        (self.diff_nodif.name.split('.')[0] +'_masked.nii.gz'))

            shutil.move(
                    self.diff_mask.parent / \
                        (self.diff_mask.name.split('.nii.gz')[0] + \
                            '_mask.nii.gz'),
                    self.diff_mask)



class DwiPipe(object):
    def CNN_brain_extraction(self, input_file: Path, output_file: Path):
        temp = tempfile.NamedTemporaryFile(mode='w+t', suffix='.txt')

        try:
            with open(temp.name, 'w') as f:
                f.write(str(input_file.absolute()))

            command = f'{self.cnn_dms}/pipeline/dwi_masking.py \
                -i {temp.name} \
                -f {self.cnn_dms}/model_folder \
                -nproc 5'

            self.run(command)
            out_mask = input_file.parent / (input_file.name.split('.')[0] + 
                    '_bse-multi_BrainMask.nii.gz')
            shutil.copy(out_mask, output_file)

        finally:
            temp.close()

    def fsl_tensor_fit(self, force: bool = False):
        '''Fit tensor and decompose into diffusion scalar maps'''
        command = f'dtifit \
            --data={self.diff_ep}.nii.gz \
            --out={self.diff_dir / "dti"} \
            --mask={self.diff_mask} \
            --bvecs={self.diff_ep_bvec} \
            --bvals={self.diff_raw_bval}'

        if force or not self.dti_FA.is_file():
            self.run(command)

        command = f'fslmaths \
                {self.dti_L2} -add {self.dti_L3} \
                {self.diff_dir}/L1_L2_added && \
                fslmaths \
                {self.diff_dir}/L1_L2_added -div 2 {self.dti_RD}'
        if force or not self.dti_RD.is_file():
            self.run(command)


    def check_diff_nifti_info(self, force: bool = False):
        assert self.diff_raw_dwi.is_file(), 'Diffusion DWI is missing'
        assert self.diff_raw_bvec.is_file(), 'Diffusion bvec is missing'
        assert self.diff_raw_bval.is_file(), 'Diffusion bval is missing'

        img = nb.load(self.diff_raw_dwi)
        assert len(img.shape) == 4, 'DWI is not 4D file'

        self.nifti_header_series = pd.Series({
            'subject': self.subject_name,
            })

        for i, num in zip(['x', 'y', 'z', 'vol'], img.shape):
            self.nifti_header_series[i] = num

        # load bval
        bval_arr = np.loadtxt(str(self.diff_raw_bval))
        bval_arr = np.round(bval_arr, -2)
        self.nifti_header_series['bval arr'] = len(np.ravel(bval_arr))
        assert img.shape[-1] in bval_arr.shape, 'bval does not match dwi'

        unique_bval = np.unique(bval_arr)
        self.nifti_header_series['bvals'] = unique_bval.astype(int)

        bval_thr = 50
        self.nifti_header_series['b0 nums'] = sum(bval_arr < bval_thr)
        self.b0_index = np.where(bval_arr < bval_thr)[0]
        self.nifti_header_series['b0 vols'] = self.b0_index
        
        self.is_multishell = np.unique(bval_arr[bval_arr >= bval_thr])[0] > 2
        self.nifti_header_series['multishell'] = self.is_multishell

        # load bvec
        bvec_arr = np.loadtxt(str(self.diff_raw_bvec))
        self.nifti_header_series['bvec arr'] = bvec_arr.shape
        assert img.shape[-1] in bvec_arr.shape, 'bvec does not match dwi'


    def eddy_squeeze(self, force: bool = False):
        eddyRun = EddyRun(self.diff_ep)

        # extract eddy information
        eddyRun.subject_name = eddyRun.eddy_dir.parent.name
        eddyRun.read_file_locations_from_command()
        eddyRun.load_eddy_information()
        eddyRun.get_outlier_info()
        eddyRun.estimate_eddy_information()
        eddyRun.outlier_summary_df()
        eddyRun.prepared = True

        # dicom info
        eddyRun.dicom_header_series = self.dicom_header_series
        eddyRun.nifti_header_series = self.nifti_header_series

        self.eddyRun = eddyRun

        eddyRun.save_all_outlier_slices_in_detail(self.eddy_qc_dir, force)

        if force and not (self.eddy_qc_dir / 'motion.csv').is_file():
            eddyRun.df_motion.to_csv(self.eddy_qc_dir / 'motion.csv')

        if force and not (self.eddy_qc_dir / 'outlier_slices.csv').is_file():
            eddyRun.df.to_csv(self.eddy_qc_dir / 'outlier_slices.csv')

        if force or not (self.eddy_qc_dir / 'eddy_summary.html').is_file():
            # create summary
            create_html(eddyRun, out_dir=self.eddy_qc_dir)


    def screen_shots(self, force: bool = False):
        '''Screen shot images'''
        self.fa_screen_shot_dir.mkdir(exist_ok=True, parents=True)
        out_file = self.fa_screen_shot_dir / 'FA_screenshot.png'
        if force or not out_file.is_file():
            nifti_snapshot.SimpleFigure(
                image_files=[self.dti_FA],
                title=f'{self.subject_name} FA',
                make_transparent_zero=True,
                cbar_width=0.5,
                cbar_title='FA',
                output_file=out_file,
                )

class DwiToolsStudy(object):
    def head_motion_summary(self):
        self.head_motion_df_html = pd.concat(
                [x.eddyRun.df_motion for x in self.subject_classes]).to_html(
                classes=["table-bordered", "table-striped", "table-hover"]
            )

    def nifti_header_summary(self):
        self.nifti_df = pd.DataFrame(
                [x.nifti_header_series for x in self.subject_classes])
        self.nifti_df = self.nifti_df.astype(str)
        cols_to_check = [x for x in self.nifti_df.columns if x != 'subject']
        self.nifti_df_unique = self.nifti_df.groupby(cols_to_check)
        self.nifti_df_html = self.nifti_df_unique.count().T.to_html(
                classes=["table-bordered", "table-striped", "table-hover"]
                )

    def count_subject(self, var):
        '''Count subjects with existing file for var attribute'''
        num = sum([getattr(x, var).is_file() for x in self.subject_classes])
        return num

    def build_study_progress(self):
        '''Build for study summary'''
        self.number_of_subjects = len(self.subjects)
        self.pass_dicom = len(
                [sum(~x.dicom_header_series.isnull()) > 3 for x
                    in self.subject_classes])
        self.pass_bvec = self.count_subject('diff_raw_bvec')
        self.pass_bval = self.count_subject('diff_raw_bval')
        self.pass_dwi = self.count_subject('diff_raw_dwi')
        self.pass_unring = self.count_subject('diff_dwi_unring')
        self.pass_mask = self.count_subject('diff_mask')
        self.pass_eddy = self.count_subject('diff_ep_out')
        self.pass_eddy_bvec = self.count_subject('diff_ep_bvec')
        self.pass_dtifit = self.count_subject('dti_FA')
        self.completed_preproc = len([x for x in self.subject_classes
                                      if x.preproc_completed])

        self.started_tbss = self.tbss_stats_dir.is_dir()
        self.completed_tbss = (self.tbss_stats_dir / 'FA_combined_roi.csv'
                ).is_file()

        self.tree_out = {}
        for title, dir_path in {'TBSS': self.tbss_all_out_dir}.items():
            tree_out_text = os.popen(f'tree {dir_path}').read()
            self.tree_out[title] = tree_out_text

def merge_dwis(dwi1:Paths, bval1:Paths, bvec1:Paths, 
               dwi2:Paths, bval2:Paths, bvec2:Paths,
               ndwi:Paths, nbval:Paths, nbvec:Paths) -> None:
    '''Save the dwi, bvec and bal with on the specified shells'''

    # load bval
    bval_arr_1 = np.loadtxt(str(bval1))
    bval_arr_2 = np.loadtxt(str(bval2))

    # load bvec
    bvec_arr_1 = np.loadtxt(str(bvec1))
    bvec_arr_2 = np.loadtxt(str(bvec2))

    # load dwi
    dwi_img_1 = nb.load(str(dwi1))
    dwi_data_1 = dwi_img_1.get_fdata()

    dwi_img_2 = nb.load(str(dwi2))
    dwi_data_2 = dwi_img_2.get_fdata()

    # new merged arrays
    new_dwi_data = np.concatenate([dwi_data_1, dwi_data_2], axis=3)
    new_bval = np.concatenate([bval_arr_1, bval_arr_2])
    new_bvec = np.concatenate([bvec_arr_1, bvec_arr_2], axis=1)

    nb.Nifti1Image(new_dwi_data, affine=dwi_img_1.affine).to_filename(str(ndwi))
    np.savetxt(nbval, new_bval, fmt='%.1f')
    np.savetxt(nbvec, new_bvec, fmt='%.6f')
