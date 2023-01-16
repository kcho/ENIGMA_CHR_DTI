import pydicom
import os
import pandas as pd
from pathlib import Path
import shutil


class PartialDicomException(Exception):
    pass


class ExtraDicomException(Exception):
    pass


class NoDicomException(Exception):
    pass


class DicomTools(object):
    def check_dicom_info(self, force: bool = False):
        '''Extract information from dicom header and store it in a dataframe'''
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

        if len(list(self.dicom_dir.glob('*'))) == 0:
            raise NoDicomException

        for root, dirs, files in os.walk(self.dicom_dir):
            for file in [x for x in files if not x.startswith('.')]:
                dicom = pydicom.read_file(Path(root) / file, force=True)
                self.dicom_header_series = pd.Series({
                    'subject': self.subject_name,
                    })

                for i in list_of_items_to_get:
                    try:
                        self.dicom_header_series[i] = getattr(dicom, i)
                    except:
                        self.dicom_header_series[i] = 'missing'

                return

    def no_dicom_info(self, force: bool = False):
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
            self.dicom_header_series[i] = 'no dicom input'


    def convert_dicom_into_bids(self,
                                force: bool = False,
                                re_run: bool = False,
                                test: bool = False):
        if force:
            if self.nifti_dir.is_dir():
                shutil.rmtree(self.nifti_dir)

        if not self.diff_raw_dwi.is_file() and \
                not self.diff_raw_bvec.is_file() and \
                not self.diff_raw_bval.is_file():
            command = f'{self.dcm2niix} \
                    -o {self.nifti_dir} \
                    -f {self.subject_name} \
                    -z y \
                    {self.dicom_dir}'
            self.nifti_dir.mkdir(exist_ok=True, parents=True)
            self.run(command)

        elif not re_run and not all([self.diff_raw_dwi.is_file(),
                                     self.diff_raw_bvec.is_file(),
                                     self.diff_raw_bval.is_file()]):
            print('Rerun')
            self.convert_dicom_into_bids(force=True, test=test)
        elif re_run and not all([self.diff_raw_dwi.is_file(),
                                     self.diff_raw_bvec.is_file(),
                                     self.diff_raw_bval.is_file()]):
            raise PartialDicomException
        else:
            pass

        if test:
            return

        if len(list(self.nifti_dir.glob('*'))) > 4:
            print(list(self.nifti_dir.glob('*')))
            raise ExtraDicomException

        if len(list(self.nifti_dir.glob('*'))) < 4:
            print(list(self.nifti_dir.glob('*')))
            raise PartialDicomException


class DicomToolsStudy(object):
    def dicom_header_summary(self):
        try:
            self.dicom_df = pd.DataFrame(
                    [x.dicom_header_series for x in self.subject_classes])
            self.dicom_df.drop('AcquisitionDate', axis=1, inplace=True)
            self.dicom_df = self.dicom_df.astype(str)
            cols_to_check = [x for x in self.dicom_df.columns if x != 'subject']
            self.dicom_df_unique = self.dicom_df.groupby(cols_to_check)
            self.dicom_df_html = self.dicom_df_unique.count().T.to_html(
                    classes=["table-bordered", "table-striped", "table-hover"]
                    )
        except AttributeError:
            self.dicom_df = pd.DataFrame()
            self.dicom_df_html = self.dicom_df.to_html()

