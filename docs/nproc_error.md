# Debuging issues


### How to limit number of processes used in the TBSS step

2023-04-21

Singularity will set the image as readable-only, therefore does not allow downloading more recent version of `ENIGMA_CHR_DTI` repository. For a work around, you can download the most recent version of `ENIGMA_CHR_DTI` outside the Singularity image and mount it over the `/opt/ENIGMA_CHR_DTI` path.

1. Download most recent `ENIGMA_CHR_DTI` using git

```sh
git clone https://github.com/kcho/ENIGMA_CHR_DTI
```

2. Mount over the existing `/opt/ENIGMA_CHR_DTI` when you execute the Singularity container.

```sh
path_to_image=/PATH/TO/YOUR/SINGULARITY/IMAGE
singularity exec \
    -B /data/predict1/home/kcho/enigma/ENIGMA_CHR_DTI:/opt/ENIGMA_CHR_DTI \
    ${path_to_image} \
      /bin/bash -c "conda activate /opt/fsl-6.0.6; xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_study.py -b /data -n 4"
```


2023-04-13


1. Enter the container in the interactive mode

```sh
docker run -it -v /YOUR/DATA/LOCATION:/data kcho/enigma-chr-pipeline /bin/bash
```

2. Run the lines below to limit number of processes in the TBSS
```sh
conda activate /opt/fsl-6.0.6
cd /opt/ENIGMA_CHR_DTI/
git checkout main
git pull
xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_study.py -b /data -n 4
```
