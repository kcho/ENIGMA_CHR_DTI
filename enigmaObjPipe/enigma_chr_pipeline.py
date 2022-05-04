from pathlib import Path
import sys

sys.path.append('/Users/kc244/ENIGMA_CHR_DTI')
from enigmaObjPipe.utils.paths import read_objPipe_config
from enigmaObjPipe.utils.dicom import DicomTools
from enigmaObjPipe.utils.run import RunCommand
from enigmaObjPipe.diffusion.dwi import DwiPipe
from enigmaObjPipe.diffusion.eddy import EddyPipe
from enigmaObjPipe.diffusion.tbss import StudyTBSS
from enigmaObjPipe.denoising.gibbs import NoiseRemovalPipe


class EnigmaChrSubjectDicomDir(
        DicomTools, RunCommand, DwiPipe, NoiseRemovalPipe, EddyPipe):
    def __init__(self, dicom_dir):
        self.dicom_dir = Path(dicom_dir)
        self.subject_name = dicom_dir.name
        self.study_dir = self.dicom_dir.parent.parent
        self.nifti_dir = self.study_dir / 'rawdata/dwi' / self.subject_name
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
        self.repol_on = True

        # eddy qc output directory
        self.eddy_qc_dir = self.derivatives_root / 'eddy_qc' / self.subject_name


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

        # 6. Tensor fit & decomp
        self.fsl_tensor_fit(force)

        # 7. Capture maps
        self.fa_screen_shot_dir = self.derivatives_root / 'FA_screenshots' / \
                self.subject_name
        self.screen_shots(force)



class EnigmaChrStudy(StudyTBSS, RunCommand):
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
        config_loc = '/Users/kc244/ENIGMA_CHR_DTI/enigmaObjPipe/config.ini'
        config = read_objPipe_config(config_loc)
        for subject in self.subject_classes:
            for key in config['software']:
                setattr(subject, key, config['software'][key])
        
            for key in config['proc']:
                setattr(subject, key, config['proc'][key])

    def project_pipeline(self, force: bool = False):
        '''Study wise pipeline'''
        # 5. run eddy QC
        self.eddy_qc(force)

        # 6. run tbss
        self.tbss_all = '/Users/kc244/tbss/lib/tbss_all'
        self.tbss_all_modalities = ['dti_FA']
        self.tbss_all_modalities_str = ['FA']
        self.run_tbss(force)

        # 7. run randomise
        self.run_randomise(force)

        # 8. log
        self.leave_log_enigma_diff_preproc_pipeline(force)


    # def eddy_qc_study(self, force: bool = False):
        # '''pass'''

        # eddy_prefix_list = [x.diff_ep for x in self.subject_classes]
        # eddyDirectories = EddyDirectories(eddy_prefix_list, pnl=args.pnl)
