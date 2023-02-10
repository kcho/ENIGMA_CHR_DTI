### If you get memory error, follow the steps below

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

singularity run -e -B ${data_location}:/data:rw enigma-chr-pipeline.simg xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/preproc_enigma_chr_study.py -b /data -l /data/log.txt
```
