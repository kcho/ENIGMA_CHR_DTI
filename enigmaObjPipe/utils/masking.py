import shutil
import tempfile as tf
import re
import nibabel as nb
import numpy as np
from dipy.segment.mask import median_otsu


class MaskingPipe(object):
    '''Masking module'''
    def run_cpu_cnn_masking(self, input, output) -> None:
        '''Saves CPU CNN masking

        Key Arguments:
            input: input nifti image path, str or Path.
            output: mask output path, str or Path

        Requirements:
            conda environment set up following https://github.com/pnlbwh/
            CNN-Diffusion-MRIBrain-Segmentation for CPU version.
        '''
        with tf.NamedTemporaryFile() as tmp:
            with open(tmp.name, 'w') as fp:
                fp.write(input)

            command = f'conda run \
                    -n {self.conda_cnn_masking_env_name} \
                    {self.CNN_DMS}/pipeline/dwi_masking.py -\
                    i test.txt -f {self.CNN_DMS}/model_folder'
            self.run(command)

        shutil.move(re.sub('.nii.gz', '_bse-multi_BrainMask.nii.gz', input),
                    output)


    def run_gpu_cnn_masking(self, input, output) -> None:
        '''Saves CPU CNN masking using GPU

        Key Arguments:
            input: input nifti image path, str or Path.
            output: mask output path, str or Path

        Requirements:
            conda environment set up following https://github.com/pnlbwh/
            CNN-Diffusion-MRIBrain-Segmentation for GPU version.
        '''
        with tf.NamedTemporaryFile() as tmp:
            with open(tmp.name, 'w') as fp:
                fp.write(input)

            command = f'conda run \
                    -n {self.conda_cnn_masking_env_name} \
                    {self.CNN_DMS}/pipeline/dwi_masking.py \
                    -i test.txt -f {self.CNN_DMS}/model_folder'
            self.run(command)

        shutil.move(re.sub('.nii.gz', '_bse-multi_BrainMask.nii.gz', input),
                    output)


    def run_otsu_masking(self, input, output) -> None:
        '''Run median otsu on a nifti image and save a mask file

        Key Arguments:
            input: input nifti image path, str or Path.
            output: mask output path, str or Path
        '''
        img = nb.load(input)
        data = img.get_fdata()
        _, mask = median_otsu(data, median_radius=2, numpass=1)

        nb.Nifti1Image(mask.astype(np.float32),
                       affine=img.affine).to_filename(output)


