# Debuging issues


### How to limit number of processes used in the TBSS step

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
