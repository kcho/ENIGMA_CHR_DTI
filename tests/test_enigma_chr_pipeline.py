import os
from pathlib import Path

SCRIPT_ROOT = Path(__file__).parent.parent
TEST_DATA_ROOT = SCRIPT_ROOT / 'test_data'

import sys
sys.path.append(str(SCRIPT_ROOT))

from pipeline.enigma_chr_pipeline import EnigmaChrStudy

def test_check_dicom_info():
    project_root = TEST_DATA_ROOT

    enigmaChrStudy = EnigmaChrStudy(project_root)
    enigmaChrSubject = enigmaChrStudy.subject_classes[0]
    enigmaChrSubject.subject_pipeline()
    


