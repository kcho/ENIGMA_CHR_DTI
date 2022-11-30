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

The toolbox is deployed in a container, so as long as either Docker or Singularity is installed on the server, the toolbox should be functional regardless of the operating system. 


Please note the pipeline does not support Apple Mac with M1 Chips yet, due to an issue with tensorflow installation on M1 Chip machines. Also, since this pipeline is specifically developed for ENIGMA-CHR DTI project, it does not support EPI distortion correction using reverse-encoding maps or field maps. If your data for ENIGMA-CHR project has multiple DWI series, blip-up / blip-down, fieldmaps, or other reverse-encoding diffusion scans, please reach out to the coordinating team.


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
