### If you get a memory error, try following the steps below.

#### Step 1.

Run subject preprocessing steps

```
# docker
docker run -it -v ${data_location}:/data enigma-chr-pipeline \
    xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_subjects.py -b /data

# singularity
singularity exec -B ${data_location}:/data enigma-chr-pipeline.simg \
    xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_subjects.py -b /data
```

#### Step 2.
 
Run TBSS step

```
# docker
docker run -it -v ${data_location}:/data enigma-chr-pipeline \
    xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_study.py -b /data

# singularity
singularity exec -B ${data_location}:/data enigma-chr-pipeline.simg \
    xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_study.py -b /data
```


#### Executing the steps above in shell mode of the container

1. Enter the container in the shell mode

```sh
docker run -it -v /YOUR/DATA/LOCATION:/data kcho/enigma-chr-pipeline /bin/bash
```

2. Run the lines below to limit number of processes in the TBSS

```sh
conda activate /opt/fsl-6.0.6
cd /opt/ENIGMA_CHR_DTI/
git checkout main
git pull
xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_subjects.py -b /data

# once completed run the second process
xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_study.py -b /data
```


#### Example of slum job submission code

```
#!/usr/bin/env bash

#SBATCH --partition=bch-largemem # queue to be used
#SBATCH --time=100:00:00 # Running time (in hours-minutes-seconds)
#SBATCH --nodes=1 # Number of compute nodes
#SBATCH --ntasks=32 # Number of cpu cores on one node
#SBATCH --cpus-per-task=32 # Number of cpu cores on one node
#SBATCH --output=Pipeline-pt2_out_%A_%a.log # Name of the output file
#SBATCH --mem=40GB

export SINGULARITY_LOCALCACHEDIR="/temp_work/$(whoami)/temp_build" \
       SINGULARITY_CACHEDIR="/temp_work/$(whoami)/temp_build" \
       SINGULARITY_TMPDIR="/temp_work/$(whoami)/temp_build"
module load singularity/3.2.1

singularity run -e -B ${data_location}:/data:rw enigma-chr-pipeline.simg \
    xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_study.py -b /data -l /data/log.txt
```


