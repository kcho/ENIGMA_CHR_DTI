# ENIGMA CHR DTI pipeline

ENIGMA CHR DTI repository

github: @kcho

email: kevincho@bwh.harvard.edu



## Contents

Introduction

Installation

Arranging data for the pipeline

Running the ENIGMA CHR DTI Pipeline

Example output





## Introduction

This repository has all the codes required 

1. Pipeline



## Installation

1. Install Docker Desktop

[Download Docker Desktop](https://www.docker.com/products/docker-desktop/)


2. Configure Docker

- Preferences
- at least 4 cores (8 cores preferably)
- at least 4 GB RAM (8 GB preferably)
- at least 40 GB of space (8 GB preferably)


3. Download ENIGMA CHR DTI pipeline docker container.

In terminal or power-shell, type
```
$ docker pull kcho/enigma-chr-pipeline
```

4. Test the pipeline


## Arranging data for the pipeline

```
/Users/kc244/enigma_chr_data  <-  it could be somewhere else
└── sourcedata
    ├── subject_01
    │   ├── MR.1.3.12.2.1107.5.2.43.166239.2022042610335278017249630
    │   ├── ...
    │   └── MR.1.3.12.2.1107.5.2.43.166239.2022042610431388254021154
    ├── subject_02
    │   └── ...
    └── subject_XX

```



## Running the ENIGMA CHR DTI Pipeline

Once you have your dicom files arranged for each subject, run following command

```
enigma_chr_dir=/Users/kc244/enigma_chr_data   # set this to your data location
docker run -it -v ${enigma_chr_dir}:/data kcho/enigma-chr-pipeline
```


## Sharing the outputs

Run the code below to compress the file to share.

Here is the list of files to share

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


