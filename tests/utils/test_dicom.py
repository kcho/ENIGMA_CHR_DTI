import os
from pathlib import Path

SCRIPT_ROOT = Path(__file__).parent.parent.parent
TEST_DATA_ROOT = SCRIPT_ROOT / 'test_data'

import sys
sys.path.append(str(SCRIPT_ROOT))

from pipeline.enigma_chr_pipeline import EnigmaChrStudy

def test_check_dicom_info():
    project_root = TEST_DATA_ROOT

    enigmaChrStudy = EnigmaChrStudy(project_root)
    enigmaChrSubject = enigmaChrStudy.subject_classes[0]
    enigmaChrSubject.check_dicom_info()
    enigmaChrSubject.convert_dicom_into_bids()
    enigmaChrSubject.convert_dicom_into_bids(force=True)
    enigmaChrSubject.check_diff_nifti_info()
    print(enigmaChrSubject.nifti_header_series)
    
