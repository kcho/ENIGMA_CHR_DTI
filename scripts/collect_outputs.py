#!/usr/bin/env python

from pathlib import Path
import zipfile
import os
import shutil
import tempfile as tf


def compress_outputs():
    '''Collect container based TBSS outputs
    TODO:
        - clean up the code
    '''
    test_root = Path('/data')

    if not test_root.is_dir():
        print('No data mounted at /data')
        return
    
    derivatives_root = test_root / 'derivatives'
    if not derivatives_root.is_dir():
        print(f'No {derivatives_root}')
        return
    eddy_qc_root = derivatives_root / 'eddy_qc'
    screenshots_root = derivatives_root / 'screenshots'
    tbss_root = derivatives_root / 'tbss'
    web_summary_root = derivatives_root / 'web_summary'

    with tf.TemporaryDirectory() as fp:
        if not (tbss_root / 'stats').is_dir():
            print('No TBSS')
        else:
            (Path(fp) / 'tbss' / 'stats').mkdir(parents=True)
            for i in (tbss_root / 'stats').glob('*csv'):
                shutil.copy(i, Path(fp) / 'tbss')

        dirs_to_compress = [eddy_qc_root,
                            screenshots_root,
                            web_summary_root]

        for i in dirs_to_compress:
            if i.is_dir():
                shutil.copytree(i, Path(fp) / i.name)
            else:
                print(f'No data under {i}')

        if not (tbss_root / 'snapshots').is_dir():
            shutil.copytree(tbss_root / 'snapshots',
                            Path(fp) / 'tbss' / 'snapshots')

        if len(list(Path(fp).glob('*'))) > 1:
            shutil.make_archive('/data/output_collection', 'zip', fp)
        else:
            print('No data to collect')


if __name__ == '__main__':
    compress_outputs()
