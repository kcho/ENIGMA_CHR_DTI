# ENIGMA CHR DTI pipeline

Kevin Cho and Yoobin Kwak

kevincho@bwh.harvard.edu
yoobinkwak@gmail.com


## Contents

* [Introduction](#introduction)
* [Installation](#installation)
* [Arranging the data for the pipeline](#arranging-the-data-for-the-pipeline)
* [Running the ENIGMA CHR DTI Pipeline](#running-the-enigma-chr-dti-pipeline)
* [Sharing outputs to other teams](#sharing-outputs-to-other-teams)
* [Citation](#citation)


## Introduction

ENIGMA CHR DTI pipeline is an automated toolbox for analyzing diffusion-weighted imaging (DWI) data developed for the ENIGMA-CHR DTI project. The pipeline expects Dicom files of a DWI session arranged in the required structure (described in "Arranging data for the pipeline") and automatically processes available data.

The Dicom files will be converted to a Nifti file, bval, and bvec file along with the BIDS sidecar json file using dcm2niix. Then the following steps will be applied to each subject data.
- Gibbs unring (FSL)
- FSL Eddy (6.0.4)
- Tensor decomposition to create fractional anisotropy (FA), axial diffusivity (AD), mean diffusivity (MD), and radial diffusivity (RD) maps.
- Skeletonization of the FA, AD, MD, and RD maps using PNL-TBSS.
- Estimation of mean diffusion measures in the major JHU bundles.

To increase the homogeneity of the diffusion acquisition parameters within site, the pipeline curates the following Dicom tags from all data and highlights in the report if there is any deviation in Dicom tags within a site.

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

Although it's recommended to provide Dicom data as the input to the pipeline, you can also provide diffusion data in the nifti format if your DWI data requires a specific Dicom to nifti conversion or if the Dicom files not available by some reason. You would need to provide DWI nifti file, bvector and bvalue file in a structure that the pipeline expects. Please make sure you are providing the raw Nifti file without any preprocessing. The pipeline will raise an error if any of the three files are missing. (See `Arranging data for the pipeline` section.) Please let the study coordinator know about your situation, and the study coordinator will guide you through the process.

The toolbox is deployed in a container, so if either Docker or Singularity is installed on the server, the toolbox should be functional regardless of the operating system. 
Please note the pipeline does not yet support Apple Mac with M1 Chips due to an issue with TensorFlow installation on M1 Chip machines. Also, since this pipeline is specifically developed for the ENIGMA-CHR DTI project, it does not support EPI distortion correction using reverse-encoding maps or field maps. If your data for the ENIGMA-CHR project has multiple DWI series, blip-up / blip-down, fieldmaps, or other reverse-encoding diffusion scans, please get in touch with the coordinating team.

Please let the study coordinator know if you need more powerful servers to process your diffusion data. The study coordinator will arrange a cloud server for you to run the pipeline.


## Installation

### Installation with Docker

Installing the pipeline through Docker would be a preferred option for the research centers with **sudo (administrator) access** on their computing system.

#### 1. Install Docker.

- [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
    - configure Docker to have at least 4 cores (12 cores preferably) and 4 GB RAM (16 GB preferably)


#### 2. Download ENIGMA CHR DTI docker image.

In terminal or power-shell (as an administrator), type
```
$ docker pull kcho/enigma-chr-pipeline
```

This command will automatically download the pipeline including all the dependencies.

#### 3. [Test the pipeline](how_to_test_pipeline.md)


### Installation with Singularity

#### 1. Install Singularity.

If you can only use your institution's computation system for the analysis without sudo access,
check with your institution's computation team to get the singularity installed.


#### 2. Download ENIGMA CHR DTI singularity image

In terminal or power-shell, type
```
$ singularity build enigma-chr-pipeline.simg docker://kcho/enigma-chr-pipeline
```

This command will automatically download the pipeline including all the dependencies.


#### 3. [Test the pipeline](how_to_test_pipeline.md)



## Arranging the data for the pipeline

### Arrange your Dicom files as the following structure.

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


If you are providing nifti files to the pipeline as the raw input, [click here](nifti_input.md)


## Running the ENIGMA CHR DTI Pipeline

Once you have your dicom files arranged for each subject, run following command in terminal or power-shell (as an administrator) 

```
# use your data location
$ docker run -it -v /Users/kc244/enigma_chr_data:/data kcho/enigma-chr-pipeline
```

For singularity,
```
# use your data location
$ singularity run -e -B /Users/kc244/enigma_chr_data:/data:rw enigma-chr-pipeline.simg
```

**The pipeline is expected to take about 2~3 hours to process a single subject data.** If you get memory error, follow the steps in [this link](memory_error.md). 


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

Then, upload the zip file to the Dropbox link share to you by the study coordinator.


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
