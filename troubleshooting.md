# Troubleshooting


## `X case(s) failed processing. Please check the log file`

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
