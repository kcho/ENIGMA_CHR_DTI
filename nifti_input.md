# How to run the pipeline on the Nifti data

Although it's recommended to provide Dicom data as the input to the pipeline, you can also provide diffusion data in the nifti format if your DWI data requires a specific Dicom to nifti conversion or if the Dicom files not available by some reason. You would need to provide DWI nifti file, bvector and bvalue file in a structure that the pipeline expects. Please make sure you are providing the raw Nifti file without any preprocessing. Also, please provide compressed Nifti file (`.nii.gz`). The pipeline will raise an error if any of the three files are missing. (See `Arranging data for the pipeline` section.) Please let the study coordinator know about your situation, and the study coordinator will guide you through the process.

## Arranging your data for the pipeline

### Arrange your Nifti, bvec, and bval files as the following structure.
```
/Users/kc244/enigma_chr_data  <-  it could be somewhere else
└── rawdata
    ├── subject_01
    │   ├── subject_01.nii.gz
    │   ├── subject_01.bvec
    │   └── subject_01.bval
    ├── subject_02
    │   ├── subject_02.nii.gz
    │   ├── subject_02.bvec
    │   └── subject_02.bval
    ├── ...
    └── subject_XX
```


## Running the ENIGMA CHR DTI Pipeline

### If you are providing nifti data to the pipeline, follow the steps below.

```
$ enigma_chr_dir=/Users/kc244/enigma_chr_data   # set this to your data location
$ docker run -it \
    -v ${enigma_chr_dir}:/data \
    kcho/enigma-chr-pipeline xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/enigma_chr_pipeline.py -b /data --nifti_input

# for singularity
$ singularity run -e -B ${enigma_chr_dir}:/data \
    enigma-chr-pipeline.simg xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/enigma_chr_pipeline.py -b /data --nifti_input
```


## Known issues

### `ProcessingFailure`

10th May, 2023

The latest version of the pipeline container raises a false alarm of `ProcessingFailure` after preprocessing all available data. This bug is fixed in the core pipeline and will be represented in the next version of the pipeline container. Simple fix to this false alarm would be re-running the pipeline using the same command. The pipeline will not re-run already completed preprocessing steps and this will also bypass the false alarm (assuming there is no real `ProcessingFailure`)

