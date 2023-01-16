import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

from pathlib import Path
code_loc = Path(__file__).parent.parent.parent
import sys
import os
sys.path.append(str(code_loc))
print(code_loc)
from enigmaObjPipe.pipeline import SubjectDicomDir
from enigmaObjPipe.utils.paths import read_objPipe_config
from enigmaObjPipe.diffusion.dwi import MissingBvecException, \
        MissingBvalException, MissingDwiException, WrongDwiException, \
        WrongBvalException, WrongBvecException
from enigmaObjPipe.enigma_chr_pipeline import EnigmaChrStudy, PartialDataCases
import numpy as np
import nibabel as nb
import pytest


def test_subject_partial_data_error():
    root_dir = code_loc / 'test_data'
    config_loc = code_loc / 'tests' / 'config_mac.ini'
    enigmaChrStudy = EnigmaChrStudy(root_dir, config_loc=config_loc)

    # contains T1w data
    enigmaChrStudy.subjects = [enigmaChrStudy.subjects[-1]]
    print(enigmaChrStudy.subjects)

    with pytest.raises(PartialDataCases) as e_info:
        enigmaChrStudy.project_pipeline()

def test_subject_missing_bval():
    root_dir = code_loc / 'test_data'
    config_loc = code_loc / 'tests' / 'config_mac.ini'
    enigmaChrStudy = EnigmaChrStudy(root_dir, config_loc=config_loc)

    # contains T1w data
    # enigmaChrStudy.subjects = [enigmaChrStudy.subjects[-1]]
    # enigmaChrStudy.subject_classes = [enigmaChrStudy.subject_classes[-1]]

    subject = enigmaChrStudy.subject_classes[-1]

    subject.convert_dicom_into_bids(force=True, test=True)
    subject.diff_raw_bval.touch()
    with pytest.raises(MissingBvecException) as e_info:
        subject.check_diff_nifti_info()

    subject.convert_dicom_into_bids(force=True, test=True)
    subject.diff_raw_bvec.touch()
    with pytest.raises(MissingBvalException) as e_info:
        subject.check_diff_nifti_info()

    subject.convert_dicom_into_bids(force=True, test=True)
    subject.diff_raw_bvec.touch()
    subject.diff_raw_bval.touch()
    os.remove(subject.diff_raw_dwi)
    with pytest.raises(MissingDwiException) as e_info:
        subject.check_diff_nifti_info()

    subject.convert_dicom_into_bids(force=True, test=True)
    subject.diff_raw_bvec.touch()
    subject.diff_raw_bval.touch()
    with pytest.raises(WrongDwiException) as e_info:
        subject.check_diff_nifti_info()

    a = np.arange(16)
    a = np.reshape(a, (2, 2, 2, 2))
    nb.Nifti1Image(a, affine=np.ones((4, 4))).to_filename(subject.diff_raw_dwi)
    img = nb.load(subject.diff_raw_dwi)
    with pytest.raises(WrongBvalException) as e_info:
        subject.check_diff_nifti_info()

    with open(subject.diff_raw_bval, 'w') as fp:
        fp.write('0 200')

    with pytest.raises(WrongBvecException) as e_info:
        subject.check_diff_nifti_info()

    with open(subject.diff_raw_bvec, 'w') as fp:
        fp.write('0 100 100\n0 100 100')

    subject.check_diff_nifti_info()


def test_subject_missing_bval():
    root_dir = code_loc / 'test_data'
    config_loc = code_loc / 'tests' / 'config_mac.ini'
    enigmaChrStudy = EnigmaChrStudy(root_dir, config_loc=config_loc)

    # contains T1w data
    # enigmaChrStudy.subjects = [enigmaChrStudy.subjects[-1]]
    # enigmaChrStudy.subject_classes = [enigmaChrStudy.subject_classes[-1]]

    subject = enigmaChrStudy.subject_classes[-1]

    subject.convert_dicom_into_bids(force=True, test=True)
    subject.diff_raw_bval.touch()
    with pytest.raises(MissingBvecException) as e_info:
        subject.check_diff_nifti_info()

    subject.convert_dicom_into_bids(force=True, test=True)
    subject.diff_raw_bvec.touch()
    with pytest.raises(MissingBvalException) as e_info:
        subject.check_diff_nifti_info()

    subject.convert_dicom_into_bids(force=True, test=True)
    subject.diff_raw_bvec.touch()
    subject.diff_raw_bval.touch()
    os.remove(subject.diff_raw_dwi)
    with pytest.raises(MissingDwiException) as e_info:
        subject.check_diff_nifti_info()

    subject.convert_dicom_into_bids(force=True, test=True)
    subject.diff_raw_bvec.touch()
    subject.diff_raw_bval.touch()
    with pytest.raises(WrongDwiException) as e_info:
        subject.check_diff_nifti_info()

    a = np.arange(16)
    a = np.reshape(a, (2, 2, 2, 2))
    nb.Nifti1Image(a, affine=np.ones((4, 4))).to_filename(subject.diff_raw_dwi)
    img = nb.load(subject.diff_raw_dwi)
    with pytest.raises(WrongBvalException) as e_info:
        subject.check_diff_nifti_info()

    with open(subject.diff_raw_bval, 'w') as fp:
        fp.write('0 200')

    with pytest.raises(WrongBvecException) as e_info:
        subject.check_diff_nifti_info()

    with open(subject.diff_raw_bvec, 'w') as fp:
        fp.write('0 100 100\n0 100 100')

    subject.check_diff_nifti_info()


def test_exception_study_level():
    root_dir = code_loc / 'test_data'
    config_loc = code_loc / 'tests' / 'config_mac.ini'
    enigmaChrStudy = EnigmaChrStudy(root_dir, config_loc=config_loc)

    # contains T1w data
    test_subject_missing_bval()
    enigmaChrStudy.subject_classes = [enigmaChrStudy.subject_classes[-1]]
    enigmaChrStudy.project_pipeline(force=False, test=True)
