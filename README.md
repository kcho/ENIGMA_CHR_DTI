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

1. Install Docker


2. Build a docker image from the `Dockerfile`

`docker build --tag pipeline .`


3. Run test script

`docker run -it enigma_chr_diff_pipe /bin/bash`



## Arranging data for the pipeline

```
enigma_chr_data
└── sourcedata
    ├── subject_01
    │   ├── MR.1.3.12.2.1107.5.2.43.166239.2022042610335278017249630
    │   ├── ...
    │   └── MR.1.3.12.2.1107.5.2.43.166239.2022042610431388254021154
    ├── subject_02
    └── subject_nn

```



## Running the ENIGMA CHR DTI Pipeline

