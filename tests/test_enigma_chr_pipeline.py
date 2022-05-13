import os
from pathlib import Path

SCRIPT_ROOT = Path(__file__).parent.parent
TEST_DATA_ROOT = SCRIPT_ROOT / 'test_data'

import sys
sys.path.append(str(SCRIPT_ROOT))

from enigmaObjPipe.enigma_chr_pipeline import EnigmaChrStudy
from eddy_squeeze.eddy_squeeze_lib.eddy_files import EddyRun, EddyDirectories
from eddy_squeeze.eddy_squeeze_lib.eddy_web import create_html
from enigmaObjPipe.utils.paths import read_objPipe_config


class TestEnigmaChrStudy(EnigmaChrStudy):
    def set_vars(self):
        config_loc = '/Users/kc244/ENIGMA_CHR_DTI/tests/config_mac.ini'
        config = read_objPipe_config(config_loc)
        for subject in self.subject_classes:
            for key in config['software']:
                setattr(subject, key, config['software'][key])
        
            for key in config['proc']:
                setattr(subject, key, config['proc'][key])

def test_enigma_chr_subject():
    project_root = TEST_DATA_ROOT

    enigmaChrStudy = TestEnigmaChrStudy(project_root)
    enigmaChrStudy.set_vars()
    for enigmaChrSubject in enigmaChrStudy.subject_classes:
        enigmaChrSubject.subject_pipeline()

def test_enigma_chr_subject_web():
    project_root = TEST_DATA_ROOT

    enigmaChrStudy = TestEnigmaChrStudy(project_root)
    enigmaChrStudy.set_vars()
    for enigmaChrSubject in enigmaChrStudy.subject_classes:
        print(enigmaChrSubject.subject_name)
        enigmaChrSubject.subject_pipeline()
        # break

    
def test_enigma_chr_project():
    project_root = TEST_DATA_ROOT

    enigmaChrStudy = EnigmaChrStudy(project_root)
    # for subject in enigmaChrStudy.subject_classes:
        # subject.subject_pipeline()

    enigmaChrStudy.project_pipeline()
    # eddy_prefix_list = [x. for x in enigmaChrStudy.subject_classes]
    # eddyDirectories = EddyDirectories(eddy_prefix_list)
    # print(eddyDirectories)
