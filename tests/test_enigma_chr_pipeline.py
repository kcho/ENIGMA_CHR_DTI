import os
from pathlib import Path

SCRIPT_ROOT = Path(__file__).parent.parent
TEST_DATA_ROOT = SCRIPT_ROOT / 'test_data'

import sys
sys.path.append(str(SCRIPT_ROOT))

from enigmaObjPipe.enigma_chr_pipeline import EnigmaChrStudy
from eddy_squeeze.eddy_squeeze_lib.eddy_files import EddyRun, EddyDirectories
from eddy_squeeze.eddy_squeeze_lib.eddy_web import create_html


def test_enigma_chr_subject():
    project_root = TEST_DATA_ROOT

    enigmaChrStudy = EnigmaChrStudy(project_root)
    enigmaChrSubject = enigmaChrStudy.subject_classes[0]
    enigmaChrSubject.subject_pipeline()

    
def test_enigma_chr_project():
    project_root = TEST_DATA_ROOT

    enigmaChrStudy = EnigmaChrStudy(project_root)
    for subject in enigmaChrStudy.subject_classes:
        subject.subject_pipeline()

    enigmaChrStudy.tbss_all = '/Users/kc244/tbss/lib/tbss_all'
    enigmaChrStudy.tbss_all_modalities = ['dti_FA']
    enigmaChrStudy.tbss_all_modalities_str = ['FA']
    enigmaChrStudy.run_tbss()
    # eddy_prefix_list = [x. for x in enigmaChrStudy.subject_classes]
    # eddyDirectories = EddyDirectories(eddy_prefix_list)
    # print(eddyDirectories)
