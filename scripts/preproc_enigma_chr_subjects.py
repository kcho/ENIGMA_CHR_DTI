#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
from enigmaObjPipe.enigma_chr_pipeline import EnigmaChrSubjectNiftiDir, \
        EnigmaChrSubjectDicomDir
from enigmaObjPipe.utils.paths import read_objPipe_config


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='ENIGMA CHR DTI pipeline')

    argparser.add_argument("--bids_root", "-b",
                           required=True,
                           help='BIDS root of the data')

    argparser.add_argument("--subject_name", "-i",
                           help='Name of the subject to process (folder name)')

    argparser.add_argument("--site", "-s",
                           default=None,
                           help='Name of the study site')

    argparser.add_argument("--nifti_input", "-ni", action='store_true',
                           help='Input data is nifti files rather than'
                                'dicom files')

    argparser.add_argument("--force", "-f", action='store_true',
                           help='Force re-run')

    argparser.add_argument("--test", "-test", action='store_true',
                           help='Test run')

    args = argparser.parse_args(argv)
    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    if args.subject_name is None:
        if args.nifti_input:
            subject_paths = list((Path(args.bids_root) / 'rawdata').glob(
                '*'))
        else:  # dicom inputs
            subject_paths = list((Path(args.bids_root) / 'sourcedata').glob(
                '*'))
    else:  # subject_name is given
        if args.nifti_input:
            subject_paths = [Path(args.bids_root) / 'rawdata' /
                             args.subject_name]
        else:  # dicom input
            subject_paths = [Path(args.bids_root) / 'sourcedata' /
                             args.subject_name]

    config_loc = '/opt/ENIGMA_CHR_DTI/enigmaObjPipe/config.ini'
    config = read_objPipe_config(config_loc)

    for subject_path in subject_paths:
        if subject_path.name.startswith('.'):
            continue

        if args.nifti_input:
            subject = EnigmaChrSubjectNiftiDir(subject_path)
        else:  # dicom input
            subject = EnigmaChrSubjectDicomDir(subject_path)

        for key in config['software']:
            setattr(subject, key, config['software'][key])

        for key in config['proc']:
            setattr(subject, key, config['proc'][key])

        if args.site is not None:
            subject.site = args.site
        else:
            subject.site = 'Study'

        subject.study_summary_file = subject.web_summary_dir / \
            f'{subject.site}.html'

        subject.subject_pipeline(force=args.force)
        del subject
