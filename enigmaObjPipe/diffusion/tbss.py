import re
import os
import numpy as np
import pandas as pd
from pathlib import Path
import argparse

class StudyTBSS(object):
    def get_tbss_diff_modalities(self):
        self.tbss_all_modalities = ['fw_fa', 'fw_fat', 'fw']
        self.tbss_all_modalities_str = ['FA', 'FAt', 'FW']

    def create_tbss_all_csv(self, tbss_all_out_dir: str):
        self.tbss_all_out_dir = Path(tbss_all_out_dir)
        self.tbss_all_out_dir.mkdir(exist_ok=True)
        self.log_loc = self.tbss_all_out_dir / 'log.txt'
        # self.start_logging('TBSS')

        # imagelist
        self.tbss_all_input_csv = self.tbss_all_out_dir / 'imagelist.csv'
        with open(self.tbss_all_input_csv, 'w') as f:
            for subject in self.subject_classes:
                print(subject)
                line_to_write = ','.join(
                    [str(getattr(subject, x)) for x in self.tbss_all_modalities])
                f.write(line_to_write+'\n')
        # self.logger.info('TBSS input CSV is written')

        # caselist
        self.tbss_all_caselist_csv = self.tbss_all_out_dir / 'caselist.csv'
        with open(self.tbss_all_caselist_csv, 'w') as f:
            for subject in self.subject_classes:
                f.write(subject.subject_name+'\n')
        # self.logger.info('TBSS input caselist is written')

    def execute_tbss(self, force: bool = False):
        command = f'{self.tbss_all} \
                --modality {",".join(self.tbss_all_modalities_str)} \
                --input {self.tbss_all_input_csv} \
                --caselist {self.tbss_all_caselist_csv} \
                --outDir {self.tbss_all_out_dir} \
                --enigma \
                --space {os.environ["FSLDIR"]}/data/standard/FMRIB58_FA_1mm.nii.gz \
                -n -1'

        self.completed_tbss = (self.tbss_stats_dir / 'FA_combined_roi.csv'
                ).is_file()

        if force or not self.completed_tbss:
            print(command)
            self.run(command)

    def clean_up_df(self, df_loc, group_order=False):
        '''Clean up the dataframe'''
        # set dataframe
        # columns:
        # ID | group | age | sex
        self.df = pd.read_csv(df_loc)

        # strip empty spaces in all columns
        for col in self.df.columns:
            try:  # if the column is string
                self.df[col] = self.df[col].str.strip()
            except:  # if not
                pass

        # remove empty lines
        self.df = self.df[~self.df.isnull()]

        # matrix array part of the df
        # self.df_array = return_one_hot_encoding_for_group_col(self.df, 'group')
        # head())
        self.df_array = pd.get_dummies(self.df['group'])
        # self.df_array = return_one_hot_encoding_for_group_col(self.df, 'group')
        # self.df_array = return_one_hot_encoding_for_group_col(
                # self.df, 'group', order=group_order)
        # self.df_array = pd.get_dummies(self.df['group'])
        # self.df_array = return_one_hot_encoding_for_group_col(self.df, 'group')
        self.df_array = self.df_array[group_order]
        self.group_order = self.df_array.columns

        # change them into float
        self.df_array = self.df_array.astype(float)

        # if age and sex is in the df
        if 'age' in self.df.columns:
            self.df_array['age'] = self.df['age']

        if 'sex' in self.df.columns:
            self.df_array['sex'] = self.df['sex']

        # estimate ppheights
        self.ppheights = self.df_array.apply(
                lambda x: x.max() - x.min(), axis=0)

        self.ppheights = '\t'.join([str(x) for x in self.ppheights])

        # assure there is no duplication in subject ID
        assert len(self.df[self.df.ID.duplicated()])==0, \
                'There is duplication in subjectID.\n'\
                f'{self.df[self.df.subjectID.duplicated()]}'

    def make_up_design_matrix(self):
        '''write up FSL style design matrix file'''
        column_info = []

        # subjectID column is ignored by setting df.columns[1:]
        for col_num, col in enumerate(
                [x for x in self.df_array.columns if x != 'id']):
            column_info.append(f'/col {col_num} {col}')

        self.header = [
            # f'/caselist name :{self.name}',
            f'/NumWaves\t{len(self.df_array.columns)}',
            f'/NumContrasts\t{len(self.df_array)}',
            f'/PPheights\t{self.ppheights}',
            f'/Matrix'
        ]

        self.array_to_write = np.array2string(
            self.df_array.to_numpy(),
            formatter={'float_kind': lambda x: "%.2f" %x})

        self.array_to_write = re.sub(r'[\[\]]', '',
                                     self.array_to_write)

        self.array_to_write = [x.strip() for x in \
                               self.array_to_write.split('\n')]

        self.matrix_lines = column_info + self.header + self.array_to_write

    def save_design_matrix(self, design_mat_loc):
        # self.clean_up_df(df_loc)
        self.make_up_design_matrix()

        if not Path(design_mat_loc).is_file() or self.force:
            with open(design_mat_loc, 'w') as f:
                f.writelines('\n'.join(self.matrix_lines))

    def make_up_design_contrast(self):
        '''write up FSL style design contrast file

        Currenly only works for two group comparison
        '''
        self.group_1 = self.df_array.columns[0]
        self.group_2 = self.df_array.columns[1]

        self.contrast_lines = [
            f'/ContrastName1 {self.group_1} > {self.group_2}',
            f'/ContrastName2 {self.group_1} < {self.group_2}',
            f'/NumWaves {len(self.df_array.columns)}',
            '/NumContrasts\t2',
            '/PPheights\t2\t2' + '\t0' * (len(self.df_array.columns)-2),
            '/Matrix',
            '1	-1' + '\t0' * (len(self.df_array.columns)-2),
            '-1	1' + '\t0' * (len(self.df_array.columns)-2)
        ]

    def save_design_contrast(self, design_con_loc):
        self.make_up_design_contrast()
        if not Path(design_con_loc).is_file() or self.force:
            with open(design_con_loc, 'w') as f:
                f.writelines('\n'.join(self.contrast_lines))


    def run_tbss(self, force: bool = False):
        # self.get_tbss_diff_modalities()
        self.create_tbss_all_csv(self.tbss_all_out_dir)
        self.execute_tbss()


    def tbss_summary(self):
        self.tbss_df = pd.DataFrame()
        for modality in self.tbss_all_modalities_str:
            df_tmp = pd.read_csv(
                    self.tbss_stats_dir / f'{modality}_combined_roi.csv')
            rename_col = lambda x: 'Average' if x == f'Average{modality}' \
                    else x
            df_tmp.columns = [rename_col(x) for x in df_tmp.columns]
            df_tmp['Modality'] = modality
            df_tmp = df_tmp[['Modality', 'Cases', 'Average'] + [x for x in
                df_tmp.columns if x not in ['Modality', 'Cases', 'Average']]]
            self.tbss_df = pd.concat([self.tbss_df, df_tmp])

        self.tbss_df_html = self.tbss_df.to_html(
                classes=["table-bordered", "table-striped", "table-hover"]
            )

    def tbss_qc(self, force):

        # tbss table QC
        self.tbss_qc_df = self.tbss_df.groupby('Modality').describe()[
                'Average']
        self.tbss_qc_df_html = self.tbss_qc_df.to_html(
                classes=["table-bordered", "table-striped", "table-hover"]
            )

        # tbss visualization
        self.tbss_mean_FA = self.tbss_stats_dir / 'mean_FA.nii.gz'
        self.tbss_template_FA = self.tbss_stats_dir / 'ENIGMA_DTI_FA.nii.gz'
        self.tbss_template_FA_skeleton = self.tbss_stats_dir / \
                'ENIGMA_DTI_FA_skeleton.nii.gz'
        self.snapshot_tbss(self.tbss_mean_FA, 'mean FA', force)
        self.snapshot_tbss(self.tbss_template_FA, 'ENIGMA Template FA', force)

        # template skeleton with template FA
        self.snapshot_tbss_gb(self.tbss_template_FA_skeleton,
                              self.tbss_template_FA,
                              'ENIGMA Template FA skeleton', force=force)

        # template skeleton with template FA
        import nibabel as nb
        import numpy as np

        self.tbss_all_FA_skel = self.tbss_stats_dir / \
                'all_FA_skeletonized.nii.gz'

        self.tbss_all_FA_skel_mean = self.tbss_stats_dir / \
                'all_FA_skeletonized_mean.nii.gz'

        img = nb.load(self.tbss_all_FA_skel)
        data = np.mean(img.get_fdata(), axis=3)
        nb.Nifti1Image(data, img.affine).to_filename(
                self.tbss_all_FA_skel_mean)

        self.snapshot_tbss_gb(self.tbss_all_FA_skel_mean,
                              self.tbss_template_FA,
                              'Mean FA skeleton',
                              cmap='Blues_r',
                              force=force)


