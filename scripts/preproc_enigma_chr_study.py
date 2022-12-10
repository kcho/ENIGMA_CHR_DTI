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
        [x.check_diff_nifti_info() for x in enigmaChrStudy.subject_classes]
    else:
        enigmaChrStudy = EnigmaChrStudy(args.bids_root,
                                        site=args.site)
        [x.check_dicom_info() for x in enigmaChrStudy.subject_classes]
        [x.check_diff_nifti_info() for x in enigmaChrStudy.subject_classes]

    if len(enigmaChrStudy.subjects) >= 1:
        # Run tbss
        enigmaChrStudy.tbss_all_modalities = ['dti_FA', 'dti_RD',
                                              'dti_MD', 'dti_L1']
        enigmaChrStudy.tbss_all_modalities_str = ['FA', 'RD',
                                                  'MD', 'AD']
        enigmaChrStudy.create_tbss_all_csv(enigmaChrStudy.tbss_all_out_dir)

        if len([x for x in enigmaChrStudy.subject_classes
                if x.preproc_completed]) >= 1:
            enigmaChrStudy.execute_tbss(force=args.force)
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
