# Troubleshooting

## Contents
- [DWI data in both encoding acquisition for EPI distortion correction](https://github.com/kcho/ENIGMA_CHR_DTI/edit/main/troubleshooting.md#dwi-data-in-both-encoding-acquisition-for-epi-distortion-correction)
- [`ProcessingFailure` before the TBSS step](https://github.com/kcho/ENIGMA_CHR_DTI/edit/main/troubleshooting.md#philips-data-with-parrec-dicom-files)
- [Resource error in the TBSS step](https://github.com/kcho/ENIGMA_CHR_DTI/edit/main/troubleshooting.md#resource-error-in-the-tbss-step)


## DWI data in both encoding acquisition for EPI distortion correction

The ENIGMA-CHR diffusion data should be preprocessed without EPI-distortion correction. Given that most ENIGMA-CHR sites have a single dMRI in a single encoding direction, we made the decision to use dMRI without EPI correction, using the reverse-encoding information to ensure consistency across different ENIGMA-CHR sites.
 
This [link](https://github.com/kcho/ENIGMA_CHR_DTI/blob/kcho/reverse_encoding_DWI/docs/reverse_encoding_dwi.md) includes instructions on how to run your pipeline on one of the dMRI series.


## Philips data with PAR/REC dicom files

Unfortunatley, the pipeline was not tested to work with the PAR/REC format, and there could be unexpected errors when you provide PAR/REC data to the ENIGMA-CHR pipeline. However, we designed the pipeline to take nifti files and it would be easier for your site to provide a nifti, bval, and bvec files for each subject following this [link](https://github.com/kcho/ENIGMA_CHR_DTI/blob/main/nifti_input.md) to run the pipeline.



## `ProcessingFailure` before the TBSS step

```sh
X case(s) failed processing. Please check the log file
```

If you see this error message, it means the pipeline raised `ProcessingFailure` error. This error is raised right before executing `PNL TBSS` step, when there is any incompleted preprocessing. One or more of the following could have raised the issue.

1. Input DWI data is completely missing for some subjects.
2. Input DWI data is partial, meaning there were some missing dicom files for some subjects.
3. Input DWI data includes non-DWI dicoms. This may led to failures in one of the preprocessing steps.
4. One of the preprocessing step failed becuase of the bad quality data (Rare).


### To resolve the issue, identify and correct the data.

Please find the problematic cases by following below and correct the input data.

1. (Without going into the docker), browse through all subject directories under `/PATH/TO/YOUR/DATA/rawdata` to see if any of the subject does not have DWI nifti file, bval, or bvec file.
2. (Without going into the docker), browse through all subject directories under `/PATH/TO/YOUR/DATA/derivatives/eddy_qc` to identify any subject without the `eddy_summary.html`. These subject would be the problematic cases. Investigate if there is anything different in the `/PATH/TO/YOUR/DATA/rawdata` and `/PATH/TO/YOUR/DATA/sourcedata` for these subjects.
3. (Without going into the docker), browse through the subject directories under `/PATH/TO/YOUR/DATA/derivatives/web_summary` and take a look at the `pdf` files created for each subject. Take a look at the figures included in the `pdf` file and see if you can detect anything wrong with the data.


Once you've identified the subject with issue, please provide the correct dicom files to its correponding directory under `/PATH/TO/YOUR/DATA/sourcedata` and rerun the [ENIGMA-CHR container](https://github.com/kcho/ENIGMA_CHR_DTI#running-the-enigma-chr-dti-pipeline)


## Resource error in the TBSS step

```sh
terminate called after throwing an instance of 'std::system_error'
  what():  Resource temporarily unavailable
```

If you see this error message, the ENIGMA-CHR pipeline may have assinged to use too many processors on your server. In this cases, the job could be terminated by your system administrator.

A new version of ENIGMA-CHR Diffusion pipeline code is added to resolve this issue. Please see [here](https://github.com/kcho/ENIGMA_CHR_DTI/blob/main/docs/nproc_error.md).
