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

    def CNN_brain_extraction(self):

        temp = tempfile.NamedTemporaryFile(mode='w+t', suffix='.txt')

        try:
            with open(temp.name, 'w') as f:
                f.write(str(self.diff_xc_dwi.absolute()))

            command = f'source /home/kcho/anaconda3/bin/activate;\
                    conda activate dmri_seg; \
                    {self.CNN_DMS}/pipeline/dwi_masking.py \
                    -i {temp.name} \
                    -f {self.CNN_DMS}/model_folder \
                    -nproc 5'

            self.run(command)
            out_mask = self.diff_dir / (self.diff_xc_dwi.name.split('.')[0] + 
                    '_bse-multi_BrainMask.nii.gz')
            shutil.copy(out_mask, self.diff_mask)

        finally:
            temp.close()



class DwiPipe(object):
    def fsl_tensor_fit(self, force: bool = False):
        '''Fit tensor and decompose into diffusion scalar maps'''
        for i in ['FA', 'L1', 'L2', 'L3', 'MD', 'MO', 'S0', 'V1', 'V2', 'V3']:
            setattr(self, f'dti_{i}', self.diff_dir / f'dti_{i}.nii.gz')

        command = f'dtifit \
            --data={self.diff_ep}.nii.gz \
            --out={self.diff_dir / "dti"} \
            --mask={self.diff_mask} \
            --bvecs={self.diff_ep}.eddy_rotated_bvecs \
            --bvals={self.diff_raw_bval}'

        if force or not self.dti_FA.is_file():
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

        if force or not (self.eddy_qc_dir / 'eddy_summary.html').is_file():
            # create summary
            eddyRun.save_all_outlier_slices_in_detail(self.eddy_qc_dir)
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
