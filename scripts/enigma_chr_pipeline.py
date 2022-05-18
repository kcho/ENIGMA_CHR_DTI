#!/usr/bin/env python

from enigmaObjPipe.enigma_chr_pipeline import EnigmaChrStudy

if __name__ == '__main__':
    project_root = '/data'
    enigmaChrStudy = EnigmaChrStudy(project_root)
    enigmaChrStudy.project_pipeline()
