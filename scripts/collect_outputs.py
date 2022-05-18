#!/usr/bin/env python

from pathlib import Path
import zipfile
import os
import shutil
import tempfile as tf


def compress_outputs():
    test_root = Path('/data')
    
    derivatives_root = test_root / 'derivatives'
    eddy_qc_root = derivatives_root / 'eddy_qc'
    screenshots_root = derivatives_root / 'screenshots'
    tbss_root = derivatives_root / 'tbss'
    web_summary_root = derivatives_root / 'web_summary'

    with tf.TemporaryDirectory() as fp:
        (Path(fp) / 'tbss' / 'stats').mkdir(parents=True)
        for i in (tbss_root / 'stats').glob('*csv'):
            shutil.copy(i, Path(fp) / 'tbss')

        dirs_to_compress = [eddy_qc_root,
                            screenshots_root,
                            web_summary_root]

        for i in dirs_to_compress:
            shutil.copytree(i, Path(fp) / i.name)

        shutil.copytree(tbss_root / 'snapshots',
                        Path(fp) / 'tbss' / 'snapshots')
        shutil.make_archive('/data/output_collection', 'zip', fp)


if __name__ == '__main__':
    compress_outputs()
