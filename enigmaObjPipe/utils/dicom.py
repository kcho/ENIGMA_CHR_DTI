import pydicom
import os
import pandas as pd
import shutil

class DicomTools(object):
    def check_dicom_info(self, force: bool = False):
        '''Extract information from dicom header and store it in a dataframe'''

        for root, dirs, files in os.walk(self.dicom_dir):
            for file in files:
                dicom = pydicom.read_file(
                        str(self.dicom_dir / file),
                        force=True)
                break
            break

        list_of_items_to_get = [
            'AcquisitionDate', 'AcquisitionMatrix',
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
            self.dicom_header_series[i] = getattr(dicom, i)


    def convert_dicom_into_bids(self, force: bool = False):
        if force:
            shutil.rmtree(self.nifti_dir)

        if not self.nifti_dir.is_dir():
            command = f'{self.dcm2niix} \
                    -o {self.nifti_dir} \
                    -f {self.subject_name} \
                    -z y \
                    {self.dicom_dir}'
            self.nifti_dir.mkdir(exist_ok=True, parents=True)
            self.run(command)

