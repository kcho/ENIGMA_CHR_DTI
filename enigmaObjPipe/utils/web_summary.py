import os
import re
from jinja2 import Environment, FileSystemLoader
import pandas as pd
from scipy.stats import zscore
from pathlib import Path
import pdfkit
from eddy_squeeze.eddy_squeeze_lib.eddy_web import \
        replace_image_locations_to_relative_in_html


root = Path(os.path.abspath(__file__)).parent.parent.parent
print(root)
static_dir = root.parent / 'docs'
templates_dir = root / 'enigmaObjPipe' / 'utils'
bwh_fig_loc = templates_dir / 'pnl-bwh-hms.png'

# jinja2 environment settings
env = Environment(loader=FileSystemLoader(str(templates_dir)))

# type
from typing import NewType
EddyStudy = NewType('EddyStudy', object)


def basename(path):
    '''functions used in the jinja2 template'''
    return Path(path).name


def sorter(file_path):
    '''functions used in the jinja2 template'''
    return int(file_path.name[:3])


def highlight_zscore(val):
    """Highlight Z-scores greater than 3 and less than -3 in red."""
    if isinstance(val, (int, float)) and val > 3:
        return "background-color: red; color: white; font-weight: bold;"
    elif isinstance(val, (int, float)) and val < -3:
        return "background-color: red; color: white; font-weight: bold;"
    return ""

def add_zscore_cols(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=["number"]).columns
    z_score_df = df[numeric_cols].apply(zscore)
    z_score_df.columns = [f"{col}_zscore" for col in numeric_cols]
    
    return pd.concat([df, z_score_df], axis=1)


def replace_zscore_cols(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=["number"]).columns
    z_score_df = df[numeric_cols].apply(zscore)
    z_score_df.columns = [f"{col}_zscore" for col in numeric_cols]
    
    return pd.concat([df.drop(numeric_cols, axis=1), z_score_df], axis=1)


def create_subject_summary(Subject: object, out_html: Path, **kwargs):
    '''Create html that summarizes subject'''

    # summary out directory settings
    out_dir = Path(out_html).parent
    out_dir.mkdir(exist_ok=True, parents=True)

    env.filters['basename'] = basename
    template = env.get_template('subject_base.html')

    with open(out_html, 'w') as fh:
        fh.write(template.render(
            title=Subject.subject_name,
            subject=Subject,
            eddyOut=Subject.eddyRun, bwh_fig_loc=bwh_fig_loc))

    options = {'enable-local-file-access': None}
    pdfkit.from_file(str(out_html),
                     str(out_html.with_suffix('.pdf')),
                     options=options)

    replace_image_locations_to_relative_in_html(Path(out_html), out_dir)


def create_project_summary(Study: object, out_html: Path, **kwargs):
    '''Create html that summarizes subject'''

    # summary out directory settings
    out_dir = Path(out_html).parent
    out_dir.mkdir(exist_ok=True, parents=True)

    env.filters['basename'] = basename
    template = env.get_template('study_base.html')

    with open(out_html, 'w') as fh:
        fh.write(template.render(
            title=Study.site,
            study=Study, bwh_fig_loc=bwh_fig_loc))

    options = {'enable-local-file-access': None}
    pdfkit.from_file(str(out_html),
                     str(out_html.with_suffix('.pdf')),
                     options=options)

    replace_image_locations_to_relative_in_html(Path(out_html), out_dir)

