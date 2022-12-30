# ENIGMA CHR DTI pipeline

Kevin Cho and Yoobin Kwak

kevincho@bwh.harvard.edu

yoobinkwak@gmail.com


## Contents
- Introduction
- Citation
- Installation
- Arranging data for the pipeline
- Running the ENIGMA CHR DTI Pipeline
- Sharing outputs to other teams


## Introduction

ENIGMA CHR DTI pipeline is a toolbox for analyzing diffusion weighted imaging (DWI) data developed for ENIGMA-CHR DTI project. The pipeline expects dicom files of a single DWI scan arranged in a required structure (decribed in "Arranging data for the pipeline") and automatically processes available data.

The dicom files will be converted to a Nifti file, bval, and bvec file along with the BIDS sidecar json file. Then the following steps will be applied to each subject data.
- Gibbs unring (FSL)
- FSL Eddy (6.0.4)
- Tensor decomposition to create fractional anisotropy (FA), axial diffusivity (AD), mean diffusivity (MD), and radial diffusivity (RD) maps.
- Skeletonization of the FA, AD, MD and RD maps using PNL-TBSS.
- Extraction of mean diffusion measures in the major JHU bundles.

To increase the homogeneity of the diffusion acquisition parameters within the site, the pipeline curates the following dicom tags from all data, and highlight in the report if there is any deviation in dicom tags within a site.

- SeriesDescription
- ImageType
- AcquisitionMatrix
- DeviceSerialNumber
- EchoTime
- FlipAngle
- InPlanePhaseEncodingDirection
- MagneticFieldStrength
- Manufacturer
- ManufacturerModelName
- ProtocolName
- RepetitionTime
- SequenceName
- SliceThickness
- SoftwareVersions
- SpacingBetweenSlices

Although it's recommended to provide dicom data as the input to the pipeline, you can also provide diffusion files in the nifti format if your DWI data requires a specific dicom to nifti conversion or if the dicom files not available by some reason. You would need to provide DWI nifti file, bvector file, bvalue file in a structure that the pipeline expects. Pleaes make sure you are providing the raw nifti file without any preprocessing. If any of the three files is missing, the pipeline will raise an error. (See `Arranging data for the pipeline` section.) Please let the study coordinator know your situation, and the study coordinate will guide you.

The toolbox is deployed in a container, so as long as either Docker or Singularity is installed on the server, the toolbox should be functional regardless of the operating system. 
Please note the pipeline does not support Apple Mac with M1 Chips yet, due to an issue with tensorflow installation on M1 Chip machines. Also, since this pipeline is specifically developed for ENIGMA-CHR DTI project, it does not support EPI distortion correction using reverse-encoding maps or field maps. If your data for ENIGMA-CHR project has multiple DWI series, blip-up / blip-down, fieldmaps, or other reverse-encoding diffusion scans, please reach out to the coordinating team.

Please let the study coordinator know if you don't have powerful enough servers to process your diffusion data. The study coordinator will arrange a cloud server for you to run the pipeline.


## Citation

This toolbox uses the following softwares. Please cite them if you use this pipeline in your study.

- [`dcm2niix`](https://github.com/rordenlab/dcm2niix)
- [CNN based diffusion MRI brain segmentation tool](https://github.com/pnlbwh/CNN-Diffusion-MRIBrain-Segmentation)
- [FSL (and FSL unring)](https://fsl.fmrib.ox.ac.uk/)
- [ANTs](https://github.com/ANTsX/ANTs)
- [PNL TBSS](https://github.com/pnlbwh/TBSS)
- [`objPipe`](https://github.com/kcho/objPipe)
- [`eddy-squeeze`](https://github.com/pnlbwh/eddy-squeeze)
- [`nifti-snapshot`](https://github.com/pnlbwh/nifti-snapshot)



## Installation

### with Docker
1. Install and configure Docker Desktop

- [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
    - with at least 4 cores (12 cores preferably) and 4 GB RAM (16 GB preferably)


2. Download ENIGMA CHR DTI docker image.

In terminal or power-shell, type
```
$ docker pull kcho/enigma-chr-pipeline
```


### with Singularity
```
$ singularity build enigma-chr-pipeline.simg docker://kcho/enigma-chr-pipeline
```


3. [Test the pipeline](how_to_test_pipeline.md)


## Arranging data for the pipeline

### If you are providing dicom files to the pipeline

```
/Users/kc244/enigma_chr_data  <-  it could be somewhere else
└── sourcedata
    ├── subject_01
    │   ├── MR.1.3.12.2.1107.5.2.43.166239.2022042610335278017249630.dcm
    │   ├── MR.1.3.12.2.1107.5.2.43.166239.2022042610335278017249631.dcm
    │   ├── ...
    │   └── MR.1.3.12.2.1107.5.2.43.166239.2022042610431388254021154.dcm
    ├── subject_02
    │   ├── MR.1.3.12.2.1107.5.2.43.166239.2022042610335278017239630.dcm
    │   ├── MR.1.3.12.2.1107.5.2.43.166239.2022042610335278011723631.dcm
    │   ├── ...
    │   └── MR.1.3.12.2.1107.5.2.43.166239.202204261043138825403154.dcm
    └── subject_XX
```


### If you are providing nifti files to the pipeline as the raw input

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

Once you have your dicom files arranged for each subject, run following command

```
$ enigma_chr_dir=/Users/kc244/enigma_chr_data   # set this to your data location
$ docker run -it -v ${enigma_chr_dir}:/data kcho/enigma-chr-pipeline
```

For singularity,
```
$ enigma_chr_dir=/Users/kc244/enigma_chr_data   # set this to your data location
$ singularity run -e -B ${enigma_chr_dir}:/data:rw enigma-chr-pipeline.simg
```

**The pipeline is expected to take about 2~3 hours to process a single subject data.**


### If you are providing nifti data to the pipeline, follow the steps below.

```
$ enigma_chr_dir=/Users/kc244/enigma_chr_data   # set this to your data location
$ docker run -it \
    -v ${enigma_chr_dir}:/data \
    enigma_chr_pipeline xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/enigma_chr_pipeline.py -b /data --nifti_input

# for singularity
$ singularity shell -e -B ${enigma_chr_dir}:/data \
    enigma_chr_pipeline.simg xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/enigma_chr_pipeline.py -b /data --nifti_input
```

### If you get memory error, follow the steps below.

#### Step 1.

```
# docker
docker run -it -v ${data_location}:/data enigma-chr-pipeline xvfb-run -a /opt/miniconda-latest/bin/python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_subjects.py -b /data

# singularity
singularity exec -B ${data_location}:/data enigma-chr-pipeline.simg xvfb-run -a /opt/miniconda-latest/bin/python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_subjects.py -b /data
```

#### Step 2.
 
```
# docker
docker run -it -v ${data_location}:/data enigma-chr-pipeline xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_study.py -b /data

# singularity
singularity exec -B ${data_location}:/data enigma-chr-pipeline.simg xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_study.py -b /data

```


## Sharing outputs to other teams

Run the code below to collect and compress the files to share.
```
$ docker run -it -v ${enigma_chr_dir}:/data kcho/enigma-chr-pipeline collect_outputs.py
```

For singularity,
```
$ singularity run -e -B ${enigma_chr_dir}:/data:rw enigma-chr-pipeline.simg collect_outputs.py
```

Here is the list of files collected by `collect_outputs.py`

```
/Users/kc244/enigma_chr_data
    derivatives/
    ├── eddy_qc
    │   ├── subject_01
    │   │   └── eddy_summary.html
    │   └── subject_02
    │       └── eddy_summary.html
    ├── screenshots
    │   ├── subject_01
    │   └── subject_02
    ├── tbss
    │   ├── snapshots
    │   │   ├── ENIGMA\ Template\ FA\ skeleton.jpg
    │   │   ├── ENIGMA\ Template\ FA.jpg
    │   │   ├── Mean\ FA\ skeleton.jpg
    │   │   └── mean\ FA.jpg
    │   └── stats
    │       ├── AD_combined_roi.csv
    │       ├── AD_combined_roi_avg.csv
    │       ├── FA_combined_roi.csv
    │       ├── FA_combined_roi_avg.csv
    │       ├── MD_combined_roi.csv
    │       ├── MD_combined_roi_avg.csv
    │       ├── RD_combined_roi.csv
    │       └── RD_combined_roi_avg.csv
    └── web_summary
        ├── Study.html
        ├── Study.pdf
        ├── subject_01
        │   ├── subject_01.html
        │   └── subject_01.pdf
        └── subject_02
            ├── subject_02.html
            └── subject_02.pdf
```


## Enter into the image shell

```
$ enigma_chr_dir=/Users/kc244/enigma_chr_data   # set this to your data location
$ docker run -it \
    -v ${enigma_chr_dir}:/data \
    enigma_chr_pipeline /bin/bash

# for singularity
$ singularity shell -e -B ${enigma_chr_dir}:/data \
    enigma_chr_pipeline.simg /bin/bash
```
