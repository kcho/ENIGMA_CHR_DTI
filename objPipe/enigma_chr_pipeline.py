from pathlib import Path
import sys

sys.path.append('/Users/kc244/ENIGMA_CHR_DTI')
from pipeline.utils.paths import read_objPipe_config
from pipeline.utils.dicom import DicomTools
from pipeline.utils.run import RunCommand
from pipeline.diffusion.dwi import DwiPipe
from pipeline.diffusion.eddy import EddyPipe
from pipeline.denoising.gibbs import NoiseRemovalPipe


class EnigmaChrSubjectDicomDir(DicomTools, RunCommand, DwiPipe,
        NoiseRemovalPipe, EddyPipe):
    def __init__(self, dicom_dir):
        self.dicom_dir = Path(dicom_dir)
        self.subject_name = dicom_dir.name
        self.study_dir = self.dicom_dir.parent.parent
        self.nifti_dir = self.study_dir / 'rawdata/dwi' / self.subject_name
        self.diff_dir = self.study_dir / 'derivatives/dwi_preproc' / \
                self.subject_name

        self.diff_raw_dwi = self.nifti_dir / f'{self.subject_name}.nii.gz'
        self.diff_raw_bvec = self.nifti_dir / f'{self.subject_name}.bvec'
        self.diff_raw_bval = self.nifti_dir / f'{self.subject_name}.bval'

        self.diff_dwi_unring = self.diff_dir / \
            f'{self.subject_name}_dwi_unring.nii.gz'

        # eddy
        self.diff_mask = self.diff_dir / f'{self.subject_name}_dwi_mask.nii.gz'
        self.eddy_out_dir = self.diff_dir
        self.diff_ep = self.diff_dir / f'{self.subject_name}_eddy_out'
        self.repol_on = True


    def subject_pipeline(self, force: bool = False):
        '''Subject-wise pipeline'''
        # 1. check basic dicom information from dicom headers
        self.check_dicom_info(force)

        # 2. convert dicom files into nifti format, in BIDS
        self.convert_dicom_into_bids(force)

        # 3. check if the conversion worked correctly
        self.check_diff_nifti_info(force)

        # 4. Diffusion preprocessing
        # 4a. gibbs unring
        self.run_gibbs_unring(self.diff_raw_dwi, self.diff_dwi_unring, force)

        # 4b. topup if site have reverse encoding maps
        # self.topup_preparation_ampscz(force)

        # 4c. run Eddy
        self.eddy(force)

        # 5. Eddy QC
        self.eddy_squeeze(force)

        print(self.dicom_header_series)
        print(self.nifti_header_series)
        # print(self.eddy_qc_series)


class EnigmaChrStudy():
    def __init__(self, root_dir: Path):
        '''ENIGMA CHR Project directory object

        Key argument:
            root_dir: Root of the ENIGMA CHR data directory

        Expected data structure:
            /home/kevin/enigma_root_dir
            └── source
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
        self.root_dir = Path(root_dir)
        self.source_dir = self.root_dir / 'sourcedata'
        self.subjects = list(sorted(self.source_dir.glob('*')))
        self.subject_classes = [EnigmaChrSubjectDicomDir(x) for x in self.subjects]

        # set settings from config
        config_loc = '/Users/kc244/ENIGMA_CHR_DTI/pipeline/config.ini'
        config = read_objPipe_config(config_loc)
        for subject in self.subject_classes:
            for key in config['software']:
                setattr(subject, key, config['software'][key])
        
            for key in config['proc']:

                print(key, config['proc'][key])
                setattr(subject, key, config['proc'][key])

    def project_pipeline(self, force: bool = False):
        '''Study wise pipeline'''
        # 5. run eddy QC
        self.eddy_qc(force)

        # 6. run tbss
        self.run_tbss(force)

        # 7. run randomise
        self.run_randomise(force)

        # 8. log
        self.leave_log_enigma_diff_preproc_pipeline(force)

