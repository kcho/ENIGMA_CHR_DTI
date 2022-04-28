import os
import numpy as np
import nibabel as nb
import sys
from dipy.segment.mask import median_otsu


class EddyPipe(object):
    def eddy(self, force):
        '''FSL Eddy'''
        # index
        data_img = nb.load(self.diff_dwi_unring)

        if force or not self.diff_mask.is_file():
            print('Estimating mask')
            data = data_img.get_fdata()

            data = data[:, :, :, self.b0_index].mean(axis=3)
            _, mask = median_otsu(data, median_radius=2, numpass=1)
            nb.Nifti1Image(mask.astype(int),
                           affine=data_img.affine).to_filename(
                                   self.diff_mask)

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
            --imain={self.diff_raw_dwi} \
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

        if not self.diff_ep.with_suffix('.nii.gz').is_file() or self.force:
            self.run(eddy_command)


    def eddy_squeeze(self):
        '''Eddy QC'''
        sys.path.append(self.eddy_squeeze_dir + '/eddy_squeeze')
        import eddy_plots
        import eddy_web

        out_dir = self.diff_ep.parent / 'outlier_figures'

        self.eddyQc = eddy_plots.EddyFigure(
                self.diff_ep.parent,
                out_dir)

        self.eddyQc.summary_df()
        self.eddyQc.save_all_outlier_slices()

        self.eddyQc.df_motion.to_csv(out_dir / 'motion.csv')
        self.eddyQc.df.to_csv(out_dir / 'outlier_slices.csv')

        eddy_web.create_html(self.eddyQc, out_dir=out_dir)
