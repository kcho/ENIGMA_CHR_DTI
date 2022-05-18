#!/usr/bin/env python

import argparse
import sys
from enigmaObjPipe.enigma_chr_pipeline import EnigmaChrStudy

def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='ENIGMA CHR DTI pipeline')

    argparser.add_argument("--test", "-test", action='store_true',
                           help='Test run')

    args = argparser.parse_args(argv)
    return args

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    project_root = '/data'
    enigmaChrStudy = EnigmaChrStudy(project_root)
    if len(enigmaChrStudy.subjects) > 1:
        enigmaChrStudy.project_pipeline(test=args.test)
    else:
        print('Please check if there are dicom directories under /data')
        print('(the input to -v option in the docker run command could be '
               'wrong)')
