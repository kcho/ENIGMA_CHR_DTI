#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
from enigmaObjPipe.enigma_chr_pipeline import EnigmaChrStudy
from enigmaObjPipe.utils.paths import read_objPipe_config
from enigmaObjPipe.utils.web_summary import create_project_summary


def parse_args(argv):
    '''Parse inputs coming from the terminal'''
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='ENIGMA CHR DTI pipeline')

    argparser.add_argument("--bids_root", "-b",
                           required=True,
                           help='BIDS root of the data')

    argparser.add_argument("--site", "-s",
                           default=None,
                           help='Name of the study site')

    argparser.add_argument("--nifti_input", "-ni", action='store_true',
                           help='Input data is nifti files rather than'
                                'dicom files')

    argparser.add_argument("--force", "-f", action='store_true',
                           help='Force re-run')

    argparser.add_argument("--log", "-l", help='Save log')

    argparser.add_argument("--nproc", "-n",
                           default=4,
                           type=int,
                           help='Number of threads to use in parallel '
                                'processing')

    argparser.add_argument("--test", "-test", action='store_true',
                           help='Test run')

    args = argparser.parse_args(argv)
    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    if args.log:
        log_file = args.log
    else:
        log_file = '.pipeline_log'

    if args.nifti_input:
        enigmaChrStudy = EnigmaChrStudy(args.bids_root,
                                        site=args.site,
                                        raw_data_type='nifti')
    else:  # dicom information
        enigmaChrStudy = EnigmaChrStudy(args.bids_root,
                                        site=args.site)
        [x.check_dicom_info() for x in enigmaChrStudy.subject_classes]

    with open(log_file, 'a') as fp:
        fp.write('-'*80 + '\n')
        fp.write(f'Root directory: {enigmaChrStudy.root_dir}\n')
        fp.write(f'sourcedata directory: {enigmaChrStudy.source_dir}\n')
        fp.write(f'rawdata directory: {enigmaChrStudy.rawdata_root} ')
        fp.write(f'({enigmaChrStudy.rawdata_root.is_dir()})\n')
        fp.write(f'derivatives directory: {enigmaChrStudy.derivatives_root}\n')
        fp.write('List of subjects\n')
        for subject_class in enigmaChrStudy.subject_classes:
            fp.write(f'\t{subject_class.subject_name}\n')
            fp.write(f'\tdwi directory: {subject_class.diff_dir} ')
            fp.write(f'({subject_class.diff_dir.is_dir()})\n')
            fp.write(f'\t\tdwi: {subject_class.diff_raw_dwi} ')
            fp.write(f'({subject_class.diff_raw_dwi.is_file()})\n')
            fp.write(f'\t\tbval: {subject_class.diff_raw_bval} ')
            fp.write(f'({subject_class.diff_raw_bval.is_file()})\n')
            fp.write(f'\t\tbvec: {subject_class.diff_raw_bvec} ')
            fp.write(f'({subject_class.diff_raw_bvec.is_file()})\n')
        fp.write('-'*80 + '\n')

    with open(log_file, 'r') as fp:
        for i in fp.readlines():
            print(i)

    [x.check_diff_nifti_info() for x in enigmaChrStudy.subject_classes]
    [x.eddy_squeeze() for x in enigmaChrStudy.subject_classes]

    if len(enigmaChrStudy.subjects) >= 1:
        # Run tbss
        enigmaChrStudy.tbss_all_modalities = ['dti_FA', 'dti_RD',
                                              'dti_MD', 'dti_L1']
        enigmaChrStudy.tbss_all_modalities_str = ['FA', 'RD',
                                                  'MD', 'AD']
        enigmaChrStudy.create_tbss_all_csv(enigmaChrStudy.tbss_all_out_dir)

        if len([x for x in enigmaChrStudy.subject_classes
                if x.preproc_completed]) >= 1:
            enigmaChrStudy.execute_tbss(force=args.force,
                                        nproc=args.nproc)
        else:
            print('***')
            print('Not enough preprocessed subjects to run TBSS')
            print('***')
        
        # Study progress
        enigmaChrStudy.build_study_progress()
        enigmaChrStudy.dicom_header_summary()
        enigmaChrStudy.nifti_header_summary()
        enigmaChrStudy.head_motion_summary()
        enigmaChrStudy.tbss_summary()
        enigmaChrStudy.tbss_qc(force=args.force)

        create_project_summary(enigmaChrStudy, enigmaChrStudy.web_summary_file)

    else:
        print(f'No data detected under {args.bids_root}')
