#!/usr/bin/env python

from enigmaObjPipe.enigma_chr_pipeline import EnigmaChrStudy

if __name__ == '__main__':
    project_root = '/data'
    enigmaChrStudy = EnigmaChrStudy(project_root)
    if len(enigmaChrStudy.subjects) > 1:
        enigmaChrStudy.project_pipeline()
    else:
        print('Please check if there are dicom directories under /data')
        print('(the input to -v option in the docker run command could be '
               'wrong)')
