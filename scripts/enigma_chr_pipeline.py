#!/usr/bin/env python

import argparse
import sys
from enigmaObjPipe.enigma_chr_pipeline import EnigmaChrStudy


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='ENIGMA CHR DTI pipeline')

    argparser.add_argument("--bids_root", "-b", type=str,
                           default='/data',
                           help='BIDS root of the data')

    argparser.add_argument("--nproc", "-n",
                           default=4,
                           type=int,
                           help='Number of threads to use in parallel '
                                'processing')

    argparser.add_argument("--site", "-s",
                           default=None,
                           help='Name of the study site')

    argparser.add_argument("--nifti_input", "-ni", action='store_true',
                           help='Input data is nifti files rather than'
                                'dicom files')

    argparser.add_argument("--test", "-test", action='store_true',
                           help='Test run')

    args = argparser.parse_args(argv)
    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    if args.nifti_input:
        enigmaChrStudy = EnigmaChrStudy(args.bids_root,
                                        site=args.site,
                                        raw_data_type='nifti')
    else:
        enigmaChrStudy = EnigmaChrStudy(args.bids_root,
                                        site=args.site)

    if len(enigmaChrStudy.subjects) >= 1:
        enigmaChrStudy.project_pipeline(test=args.test, nproc=args.nproc)
    else:
        print(f'No data detected under {args.bids_root}')
