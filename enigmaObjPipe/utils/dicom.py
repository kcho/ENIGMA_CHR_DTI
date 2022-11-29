import pydicom
import os
import pandas as pd
from pathlib import Path
import shutil

class DicomTools(object):
    def check_dicom_info(self, force: bool = False):
        '''Extract information from dicom header and store it in a dataframe'''

        for root, dirs, files in os.walk(self.dicom_dir):
            for file in [x for x in files if not x.startswith('.')]:
                dicom = pydicom.read_file(
                        Path(root) / file,
                        force=True)

                list_of_items_to_get = [
                    'AcquisitionDate', 'SeriesDescription',
                    'ImageType', 'AcquisitionMatrix',
                    'DeviceSerialNumber', 'EchoTime', 'FlipAngle',
                    'InPlanePhaseEncodingDirection',
                    'MagneticFieldStrength', 'Manufacturer',
                    'ManufacturerModelName', 'ProtocolName',
                    'RepetitionTime', 'SequenceName', 'SliceThickness',
                    'SoftwareVersions', 'SpacingBetweenSlices'
                    ]

                self.dicom_header_series = pd.Series({
                    'subject': self.subject_name,
                    })

                for i in list_of_items_to_get:
                    try:
                        self.dicom_header_series[i] = getattr(dicom, i)
                    except:
                        self.dicom_header_series[i] = 'missing'

                return


    def convert_dicom_into_bids(self, force: bool = False):
        if force:
            shutil.rmtree(self.nifti_dir)

        if not self.nifti_dir.is_dir() or not self.diff_raw_dwi.is_file():
            command = f'{self.dcm2niix} \
                    -o {self.nifti_dir} \
                    -f {self.subject_name} \
                    -z y \
                    {self.dicom_dir}'
            self.nifti_dir.mkdir(exist_ok=True, parents=True)
            self.run(command)


class DicomToolsStudy(object):
    def dicom_header_summary(self):
        self.dicom_df = pd.DataFrame(
                [x.dicom_header_series for x in self.subject_classes])
        self.dicom_df.drop('AcquisitionDate', axis=1, inplace=True)
        self.dicom_df = self.dicom_df.astype(str)
        cols_to_check = [x for x in self.dicom_df.columns if x != 'subject']
        self.dicom_df_unique = self.dicom_df.groupby(cols_to_check)
        self.dicom_df_html = self.dicom_df_unique.count().T.to_html(
                classes=["table-bordered", "table-striped", "table-hover"]
                )

