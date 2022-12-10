import os
import numpy as np
import nibabel as nb
import sys
from dipy.segment.mask import median_otsu
import shutil
from eddy_squeeze.eddy_squeeze_lib import eddy_web
from eddy_squeeze.eddy_squeeze_lib.eddy_present import EddyFigure


class EddyPipe(object):
    def eddy(self, force: bool = False, test: bool = False):
        '''FSL Eddy'''
        # index

        if force or not self.diff_mask.is_file():
            # previous masking using dipy
            # print('Estimating mask')
            # data = data_img.get_fdata()

            # data = data[:, :, :, self.b0_index].mean(axis=3)
            # _, mask = median_otsu(data, median_radius=2, numpass=1)
            # nb.Nifti1Image(mask.astype(int),
                           # affine=data_img.affine).to_filename(
                                   # self.diff_mask)

            # new masking using CNN masking
            # self.CNN_brain_extraction(self.diff_raw_dwi, self.diff_mask)
            shutil.copy(self.diff_raw_bval,
                        str(self.diff_dwi_unring).split('.')[0] + '.bval')
            shutil.copy(self.diff_raw_bvec,
                        str(self.diff_dwi_unring).split('.')[0] + '.bvec')
            self.CNN_brain_extraction(self.diff_dwi_unring, self.diff_mask)

        data_img = nb.load(self.diff_dwi_unring)
        index_array = np.tile(1, data_img.shape[-1])
        index_loc = self.eddy_out_dir / 'index.txt'
        if force or not index_loc.is_file():
            np.savetxt(str(index_loc), index_array, fmt='%d', newline=' ')

        # acqp
        # acqp_num = (256-1) * echo_spacing * 0.001
        acqp_num = 0.05
        acqp_line = '0 -1 0 {}'.format(acqp_num)
        acqp_loc = self.eddy_out_dir / 'acqp.txt'

        if force or not acqp_loc.is_file():
            with open(acqp_loc, 'w') as f:
                f.write(acqp_line)

        # eddy_command
        eddy_command = f'OMP_NUM_THREADS={self.omp_num_threads} {self.eddy_openmp} \
            --imain={self.diff_dwi_unring} \
            --mask={self.diff_mask} \
            --index={index_loc} \
            --acqp={acqp_loc} \
            --bvecs={self.diff_raw_bvec} \
            --bvals={self.diff_raw_bval} \
            --out={self.diff_ep}'

        if self.repol_on:
            eddy_command = eddy_command + ' --repol'

        if self.is_multishell:
            eddy_command = eddy_command + ' --data_is_shelled'

        if not self.diff_ep.with_suffix('.nii.gz').is_file() or force:
            if test:
                self.create_fake_eddy_output(eddy_command)
            else:
                self.run(eddy_command)

    def eddy_squeeze(self, force: bool = False):
        '''Eddy QC', force: bool = False'''
        out_dir = self.diff_ep.parent / 'outlier_figures'

        self.eddyQc = EddyFigure(
                self.diff_ep.parent,
                out_dir)

        self.eddyQc.summary_df()
        self.image_list = []

        if not out_dir.is_dir() or force:
            self.eddyQc.save_all_outlier_slices()

        if not (out_dir / 'motion.csv').is_file() or force:
            self.eddyQc.df_motion.to_csv(out_dir / 'motion.csv')

        if not (out_dir / 'outlier_slices.csv').is_file() or force:
            self.eddyQc.df.to_csv(out_dir / 'outlier_slices.csv')

        eddy_web.create_html(self.eddyQc, out_dir=out_dir)

    def create_fake_eddy_output(self, eddy_command):
        '''Create fake eddy output'''
        shutil.copy(self.diff_dwi_unring, self.diff_ep.with_suffix('.nii.gz'))
        shutil.copy(self.diff_dwi_unring,
                    str(self.diff_ep) + '.eddy_outlier_free_data.nii.gz')
        shutil.copy(self.diff_raw_bvec,
                    str(self.diff_ep) + '.eddy_rotated_bvecs')

        with open(self.diff_ep.with_suffix('.eddy_command_txt'), 'w') as fp:
            fp.write(eddy_command)

        motion_array = np.random.rand(100, 2)
        np.savetxt(str(self.diff_ep) + '.eddy_movement_rms',
                   motion_array)
        np.savetxt(str(self.diff_ep) + '.eddy_restricted_movement_rms',
                   motion_array)

        outlier_map_arr = np.random.randint(0, 100, 25).reshape(5, 5)
        np.savetxt(str(self.diff_ep) + '.eddy_outlier_map',
                   outlier_map_arr, header='fake header')
        np.savetxt(str(self.diff_ep) + '.eddy_outlier_n_sqr_stdev_map',
                   outlier_map_arr, header='fake header')

        with open(self.diff_ep.with_suffix('.eddy_outlier_report'), 'w') as fp:
            fp.write('Slice 28 in scan 80 is an outlier with mean -5.12091 '
                     'standard deviations off, and mean squared 2.95609 '
                     'standard deviations off.')
        np.savetxt(str(self.diff_ep) + '.eeddy_parameters',
                   outlier_map_arr, header='fake header')


        text_to_write = '''
        These between shell PE-translations were calculated using MI between shell means
        PE-translations (mm) relative b0-shell from direct registration to mean b0
        Shell 1e+03 to b0-shell: PE-translation = -0.285 mm
        Shell 2e+03 to b0-shell: PE-translation = 0.847 mm
        Shell 3e+03 to b0-shell: PE-translation = 0.846 mm

        Relative PE-translations (mm) between the shells
        Shell 2e+03 to shell 1e+03: PE-translation = 0.874 mm
        Shell 3e+03 to shell 1e+03: PE-translation = 0.878 mm

        Deduced PE-translations (mm) relative b0-shell
        Shell 1e+03 to b0-shell: PE-translation = -0.285 mm
        Shell 2e+03 to b0-shell: PE-translation = 0.847 mm
        Shell 3e+03 to b0-shell: PE-translation = 0.846 mm'''

        with open(self.diff_ep.with_suffix(
            '.eddy_post_eddy_shell_PE_translation_parameters'), 'w') as fp:
            fp.write(text_to_write.strip())
