from pathlib import Path
import sys
import os
import re
import pandas as pd

from enigmaObjPipe.utils.paths import read_objPipe_config
from enigmaObjPipe.utils.dicom import DicomTools, DicomToolsStudy
from enigmaObjPipe.utils.dicom import PartialDicomException, \
        ExtraDicomException, NoDicomException
from enigmaObjPipe.utils.run import RunCommand
from enigmaObjPipe.utils.snapshots import Snapshot
from enigmaObjPipe.utils.web_summary import create_subject_summary, \
        create_project_summary
from enigmaObjPipe.diffusion.dwi import DwiPipe, DwiToolsStudy
from enigmaObjPipe.diffusion.dwi import MissingBvalException, \
        MissingBvecException, MissingDwiException, WrongBvalException, \
        WrongBvecException, WrongDwiException
from enigmaObjPipe.diffusion.eddy import EddyPipe
from enigmaObjPipe.diffusion.tbss import StudyTBSS
from enigmaObjPipe.denoising.gibbs import NoiseRemovalPipe


class PartialDataCases(Exception):
    pass

class ProcessingFailure(Exception):
    pass


class EnigmaChrSubjectDicomDir(
        DicomTools, RunCommand, DwiPipe, NoiseRemovalPipe, EddyPipe,
        Snapshot):
    def __init__(self, dicom_dir):
        self.dicom_dir = Path(dicom_dir)
        self.subject_name = dicom_dir.name
        self.study_dir = self.dicom_dir.parent.parent
        self.nifti_dir = self.study_dir / 'rawdata' / self.subject_name
        self.derivatives_root = self.study_dir / 'derivatives'
        self.deriv_dwi_root = self.derivatives_root / 'dwi_preproc'
        self.diff_dir = self.deriv_dwi_root / self.subject_name

        self.diff_raw_dwi = self.nifti_dir / f'{self.subject_name}.nii.gz'
        self.diff_raw_bvec = self.nifti_dir / f'{self.subject_name}.bvec'
        self.diff_raw_bval = self.nifti_dir / f'{self.subject_name}.bval'

        self.diff_dwi_unring = self.diff_dir / \
            f'{self.subject_name}_dwi_unring.nii.gz'

        # eddy
        self.diff_mask = self.diff_dir / f'{self.subject_name}_dwi_mask.nii.gz'
        self.eddy_out_dir = self.diff_dir
        self.diff_ep = self.diff_dir / f'{self.subject_name}_eddy_out'
        self.diff_ep_out = self.diff_dir / \
                f'{self.subject_name}_eddy_out.nii.gz'
        self.diff_ep_bvec = self.diff_dir / \
                f'{self.subject_name}_eddy_out.eddy_rotated_bvecs'

        self.repol_on = True


        # diffusion scalar maps from dtifit
        for i in ['FA', 'L1', 'L2', 'L3', 'MD',
                  'MO', 'S0', 'V1', 'V2', 'V3', 'RD']:
            setattr(self, f'dti_{i}', self.diff_dir / f'dti_{i}.nii.gz')

        # preproc completed
        if self.dti_FA.is_file():
            self.preproc_completed = True
        else:
            self.preproc_completed = False

        # eddy qc output directory
        self.eddy_qc_dir = self.derivatives_root / \
                'eddy_qc' / self.subject_name

        # snapshots
        self.screen_shot_dir = self.derivatives_root / \
                'screenshots' / self.subject_name

        # web output
        self.web_summary_dir = self.derivatives_root / \
                'web_summary' / self.subject_name
        self.web_summary_file = self.web_summary_dir / \
                f'{self.subject_name}.html'


    def subject_pipeline(self,
                         force: bool = False,
                         check_run: bool = False,
                         test: bool = False):
        '''Subject-wise pipeline'''
        # 1. check basic dicom information from dicom headers
        self.check_dicom_info(force)

        # 2. convert dicom files into nifti format, in BIDS
        self.convert_dicom_into_bids(force=force, test=test)

        # 3. check if the conversion worked correctly
        self.check_diff_nifti_info(force)

        if check_run:
            return

        self.snapshot_first_b0(self.diff_raw_dwi, 'Raw DWI', force)
                      
        # 4. Diffusion preprocessing
        # 4a. gibbs unring
        print('Gibbs Unring')
        self.run_gibbs_unring(self.diff_raw_dwi, self.diff_dwi_unring, force)
        self.snapshot_first_b0(self.diff_dwi_unring, 'Unring DWI', force)
        self.snapshot_diff_first_b0(self.diff_dwi_unring, self.diff_raw_dwi,
                                    'Unring DWI', 'Raw DWI', force)


        # 4b. topup if site have reverse encoding maps
        # self.topup_preparation_ampscz(force)

        # 4c. run Eddy
        print('Running Eddy - may take 1~2 hours')
        self.eddy(force, test)
        self.snapshot_first_b0(self.diff_mask, 'mask', force)
        self.snapshot_first_b0(self.diff_ep.with_suffix('.nii.gz'),
                               'Eddy DWI', force)
        self.snapshot_diff_first_b0(self.diff_ep.with_suffix('.nii.gz'),
                                    self.diff_dwi_unring,
                                    'Eddy output', 'Unring DWI', force)

        # 5. Eddy QC
        self.eddy_squeeze(force)
        self.eddyRun.df_motion.index = [self.subject_name]

        # 6. Tensor fit & decomp
        print('Tensor fit')
        self.fsl_tensor_fit(force)

        # 7. Capture maps
        print('Snapshots')
        self.snapshot_first_b0(self.dti_FA, 'FA', force)
        self.snapshot_first_b0(self.dti_MD, 'MD', force)
        self.snapshot_first_b0(self.dti_RD, 'RD', force)
        self.snapshot_first_b0(self.dti_L1, 'AD', force)

        self.tree_out = {}
        for title, dir_path in {'Raw Nifti': self.nifti_dir,
                                'Diffusion preproc': self.diff_dir,
                                'Eddy-squeeze': self.eddy_qc_dir,
                                'Nifti snapshots': self.screen_shot_dir,
                                'Web summary': self.web_summary_dir}.items():
            tree_out_text = os.popen(f'tree {dir_path}').read()
            self.tree_out[title] = tree_out_text

        # # 8. HTML summary
        create_subject_summary(self, self.web_summary_file)

        self.preproc_completed = True


class EnigmaChrSubjectNiftiDir(EnigmaChrSubjectDicomDir):
    def __init__(self, nifti_dir: Path):
        '''Enigma subject with nifti raw data input

        Key argument:
            nifti_dir: root directory of nifti files for a subject, str.

        Required files:
            Diffusion nifti file, bvec file, and bval file with the matching
            prefix are required for the pipeline to detect the files.

        Expected data structure:
            /home/kevin/enigma_root_dir
            └── rawdata
                ├── subject_01  <- `nifti_dir`
                │   ├── subject_01.nii.gz
                │   ├── subject_01.bvec
                │   └── subject_01.bval
                ├── subject_02
                │   ├── subject_02.nii.gz
                │   ├── subject_02.bvec
                │   └── subject_02.bval
                ├── ...
                └── subject_XX

        How to use this class:
            >> import EnigmaChrProject
            >> nifti_dir = '/home/kevin/enigma_root_dir/rawdata/subject_01'
            >> enigmaChrSubject = EnigmaChrSubjectNiftiDir(nifti_dir)
            >> enigmaChrSubject.subject_pipeline()
        '''
        sourcedata_root = Path(nifti_dir).parent.parent / 'sourcedata'
        subject_name = Path(nifti_dir).name
        dicom_dir_missing = sourcedata_root / subject_name

        EnigmaChrSubjectDicomDir.__init__(self, dicom_dir_missing)

    def subject_pipeline(self,
                         force: bool = False,
                         check_run: bool = False,
                         test: bool = False):
        '''Subject-wise pipeline'''
        # register 'no dicom input' to self.dicom_header_series attr
        self.no_dicom_info(force)

        # 3. check if the conversion worked correctly
        self.check_diff_nifti_info(force)

        if check_run:
            return

        self.snapshot_first_b0(self.diff_raw_dwi, 'Raw DWI', force)
                      
        # 4. Diffusion preprocessing
        # 4a. gibbs unring
        print('Gibbs Unring')
        self.run_gibbs_unring(self.diff_raw_dwi, self.diff_dwi_unring, force)
        self.snapshot_first_b0(self.diff_dwi_unring, 'Unring DWI', force)
        self.snapshot_diff_first_b0(self.diff_dwi_unring, self.diff_raw_dwi,
                                    'Unring DWI', 'Raw DWI', force)


        # 4b. topup if site have reverse encoding maps
        # self.topup_preparation_ampscz(force)

        # 4c. run Eddy
        print('Running Eddy - may take 1~2 hours')
        self.eddy(force, test)
        self.snapshot_first_b0(self.diff_mask, 'mask', force)
        self.snapshot_first_b0(self.diff_ep.with_suffix('.nii.gz'),
                               'Eddy DWI', force)
        self.snapshot_diff_first_b0(self.diff_ep.with_suffix('.nii.gz'),
                                    self.diff_dwi_unring,
                                    'Eddy output', 'Unring DWI', force)

        # 5. Eddy QC
        self.eddy_squeeze(force)
        self.eddyRun.df_motion.index = [self.subject_name]

        # 6. Tensor fit & decomp
        print('Tensor fit')
        self.fsl_tensor_fit(force)

        # 7. Capture maps
        print('Snapshots')
        self.snapshot_first_b0(self.dti_FA, 'FA', force)
        self.snapshot_first_b0(self.dti_MD, 'MD', force)
        self.snapshot_first_b0(self.dti_RD, 'RD', force)
        self.snapshot_first_b0(self.dti_L1, 'AD', force)

        self.tree_out = {}
        for title, dir_path in {'Raw Nifti': self.nifti_dir,
                                'Diffusion preproc': self.diff_dir,
                                'Eddy-squeeze': self.eddy_qc_dir,
                                'Nifti snapshots': self.screen_shot_dir,
                                'Web summary': self.web_summary_dir}.items():
            tree_out_text = os.popen(f'tree {dir_path}').read()
            self.tree_out[title] = tree_out_text

        # # 8. HTML summary
        create_subject_summary(self, self.web_summary_file)

        self.preproc_completed = True


class EnigmaChrStudy(StudyTBSS, RunCommand, Snapshot,
        DicomToolsStudy, DwiToolsStudy):
    def __init__(self, root_dir: Path, site: str = None,
                 raw_data_type: str = 'dicom',
                 config_loc: str = None):
        '''ENIGMA CHR Project directory object

        Key argument:
            root_dir: Root of the ENIGMA CHR data directory, str or Path.
            site: Name of the study site, str.
            raw_data_type: Type of the raw data, either 'dicom' or 'nifti'.
                           'dicom' by default.

        Expected data structure:
            /home/kevin/enigma_root_dir  <- `root_dir`
            └── sourcedata
                ├── subject_01
                │   ├── dicom_00001.dcm
                │   ├── dicom_00002.dcm
                │   ├── ...
                │   └── dicom_00004.dcm
                ├── subject_02
                ├── ...
                └── subject_03

        How to use this class:
            >> import EnigmaChrProject
            >> root_dir = '/home/kevin/enigma_root_dir'
            >> enigmaChrStudy = EnigmaChrStudy(root_dir)
            >> enigmaChrStudy.enigma_chr_diffusion_preproc_pipeline()
        '''
        if site is not None:
            self.site = site
        else:
            self.site = 'Study'

        self.root_dir = Path(root_dir)
        self.source_dir = self.root_dir / 'sourcedata'
        self.sourcedata_root_check = self.source_dir.is_dir()
        self.rawdata_root = self.root_dir / 'rawdata'
        self.rawdata_root_check = self.rawdata_root.is_dir()

        if raw_data_type == 'dicom':
            print(raw_data_type)
            self.subjects = list(sorted([x for x in self.source_dir.glob('*')
                if not x.name.startswith('.')]))
        
            # make sure there are at least one subject
            if len(self.subjects) < 1:
                print('-'*80)
                print('No dicom directories are detected')
                if not self.sourcedata_root_check():
                    print("Your data structure does not have 'sourcedata' "
                          "directory")
                    print("Please see the documentation for how to structure "
                          "the input data")
                sys.exit('Exiting without running the pipeline')

            self.subject_classes = [EnigmaChrSubjectDicomDir(x) for x
                                    in self.subjects]

        else:  # Nifti input
            print(raw_data_type)
            self.subjects = list(sorted([x for x in self.rawdata_root.glob('*')
                if not x.name.startswith('.')]))

            # make sure there are at least one subject
            if len(self.subjects) < 1:
                print('-'*80)
                print('No nifti directories are detected')
                if not self.rawdata_root_check():
                    print("Your data structure does not have 'rawdata' "
                          "directory")
                    print("Please see the documentation for how to structure "
                          "the input data")
                sys.exit('Exiting without running the pipeline')

            self.subject_classes = [EnigmaChrSubjectNiftiDir(x) for x
                                    in self.subjects]

        # tbss
        self.derivatives_root = self.root_dir / 'derivatives'
        self.tbss_all_out_dir = self.derivatives_root / 'tbss'
        self.tbss_stats_dir = self.tbss_all_out_dir / 'stats'
        self.tbss_screen_shot_dir = self.tbss_all_out_dir / 'snapshots'
        self.web_summary_dir = self.derivatives_root / 'web_summary'
        self.web_summary_file = self.web_summary_dir / \
                f'{self.site}.html'

        # set settings from config
        if config_loc is None:
            config_loc = '/opt/ENIGMA_CHR_DTI/enigmaObjPipe/config.ini'
        config = read_objPipe_config(config_loc)
        for subject in self.subject_classes:
            for key in config['software']:
                setattr(subject, key, config['software'][key])

            for key in config['proc']:
                setattr(subject, key, config['proc'][key])

            subject.study_summary_file = self.web_summary_file

        self.tbss_all = subject.tbss_all

    def project_pipeline(self, force: bool = False, test: bool = False):
        '''Study wise pipeline'''

        # Run subject level preprocessing
        error_df = pd.DataFrame(columns=['subject', 'error'])
        for subject in self.subject_classes:
            error_df_tmp = pd.DataFrame(
                    {'subject': [subject.subject_name]})
            try:
                subject.subject_pipeline(force=force,
                                         check_run=True,
                                         test=test)
            except NoDicomException:
                error_df_tmp['error'] = 'No dicom files'
                error_df_tmp['data_loc'] = subject.dicom_dir
                error_df_tmp['note'] = 'Dicom files are missing for this ' \
                    'subject.'
            except PartialDicomException:
                error_df_tmp['error'] = 'Incomplete or incorrect dicom files'
                error_df_tmp['data_loc'] = subject.dicom_dir
                error_df_tmp['note'] = 'The dicom input does not contain ' \
                    'all the DWI related information. Please check if you ' \
                    'provided correct dicom files for this subject. Also ' \
                    'see files created from the given dicom files under ' \
                    f'{subject.nifti_dir}.'
            except ExtraDicomException:
                error_df_tmp['error'] = 'Incomplete or incorrect dicom files'
                error_df_tmp['data_loc'] = subject.dicom_dir
                error_df_tmp['note'] = 'The dicom input creates extra files ' \
                    'that may interfere with diffusion preprocessing. ' \
                    'Please check if you provided correct dicom files for ' \
                    'this subject. Also see files created from the given ' \
                    f'dicom files under {subject.nifti_dir}.'
            except MissingDwiException:
                error_df_tmp['error'] = 'Missing DWI nifti file'
                error_df_tmp['data_loc'] = subject.diff_raw_dwi
                error_df_tmp['note'] = 'The DWI nifti file is missing. ' \
                    'Please check if there is DWI nifti file.'
            except MissingBvalException:
                error_df_tmp['error'] = 'Missing bval file'
                error_df_tmp['data_loc'] = subject.diff_raw_bval
                error_df_tmp['note'] = 'The bval file is missing. ' \
                    'Please check if there is bval file.'
            except MissingBvecException:
                error_df_tmp['error'] = 'Missing bvec file'
                error_df_tmp['data_loc'] = subject.diff_raw_bvec
                error_df_tmp['note'] = 'The bvec file is missing. ' \
                    'Please check if there is bvec file.'
            except WrongDwiException:
                error_df_tmp['error'] = 'Wrong DWI nifti file'
                error_df_tmp['data_loc'] = subject.diff_raw_dwi
                error_df_tmp['note'] = 'The DWI nifti is not 4D. Please ' \
                    'check if you provided the correct data.'
            except WrongBvalException:
                error_df_tmp['error'] = 'Wrong bval file'
                error_df_tmp['data_loc'] = subject.diff_raw_bval
                error_df_tmp['note'] = 'The bval does not match the given ' \
                    'DWI nifti file. Please check if you provided the ' \
                    'correct data.'
            except WrongBvecException:
                error_df_tmp['error'] = 'Wrong bvec file'
                error_df_tmp['data_loc'] = subject.diff_raw_bvec
                error_df_tmp['note'] = 'The bvec does not match the given ' \
                    'DWI nifti file. Please check if you provided the ' \
                    'correct data.'

            error_df = pd.concat([error_df, error_df_tmp]).reset_index(
                    drop=True)

        error_df = error_df[~error_df.error.isnull()]

        if len(error_df) > 0:
            error_files = self.root_dir.glob('cases_with_error_v*.csv')
            max_num = 0
            for error_file in error_files:
                num = int(re.search(r'cases_with_error_v(\d*).csv',
                                    error_file.name).group(1))
                if num > max_num:
                    max_num = num

            error_file_to_write = self.root_dir / \
                    f'cases_with_error_v{max_num + 1}.csv'
            error_df.to_csv(error_file_to_write)
            print(f'There are {len(error_df)} subjects with data deviation. '
                  f'Please check "{error_file_to_write}" under your input '
                  'data directory and resolve all issues before re-running '
                  'the code.')
            raise PartialDataCases

        # Actual processing
        processing_failed_subject_classes = []
        for subject in self.subject_classes:
            error_df_tmp = pd.DataFrame(
                    {'subject': [subject.subject_name]})
            try:
                subject.subject_pipeline(force=force,
                                         check_run=True,
                                         test=test)
            except:
                processing_failed_subject_classes.append(subject)
                print(f'{subject.name}: raised processing error')

        if len(processing_failed_subject_classes) > 0:
            print(f'{len(processing_failed_subject_classes)} case(s) failed '
                  'processing. Please check the log file.')
            raise ProcessingFailure
                
        # Run tbss
        self.tbss_all_modalities = ['dti_FA', 'dti_RD', 'dti_MD', 'dti_L1']
        self.tbss_all_modalities_str = ['FA', 'RD', 'MD', 'AD']
        self.create_tbss_all_csv(self.tbss_all_out_dir)
        if len([x for x in self.subject_classes
                if x.preproc_completed]) > 1:
            self.execute_tbss(force)
        else:
            print('***')
            print('Not enough preprocessed subjects to run TBSS')
            print('***')
        
        # Study progress
        self.build_study_progress()
        self.dicom_header_summary()
        self.nifti_header_summary()
        self.head_motion_summary()
        self.tbss_summary()
        self.tbss_qc(force)

        create_project_summary(self, self.web_summary_file)

