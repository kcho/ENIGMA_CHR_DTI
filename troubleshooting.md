# Troubleshooting

## Contents
- [DWI data in both encoding acquisition for EPI distortion correction](https://github.com/kcho/ENIGMA_CHR_DTI/blob/main/troubleshooting.md#dwi-data-in-both-encoding-acquisition-for-epi-distortion-correction)
- [`ProcessingFailure` before the TBSS step](https://github.com/kcho/ENIGMA_CHR_DTI/blob/main/troubleshooting.md#philips-data-with-parrec-dicom-files)
- [Resource error in the TBSS step](https://github.com/kcho/ENIGMA_CHR_DTI/blob/main/troubleshooting.md#resource-error-in-the-tbss-step)
- [Docker run hangs infinitely](https://github.com/kcho/ENIGMA_CHR_DTI/blob/main/troubleshooting.md#docker-hangs-infinitely)
- [`collect_outputs.py` does not work](https://github.com/kcho/ENIGMA_CHR_DTI/blob/main/troubleshooting.md#collect_outputspy-does-not-work)


## DWI data in both encoding acquisition for EPI distortion correction

The ENIGMA-CHR diffusion data should be preprocessed without EPI-distortion correction. Given that most ENIGMA-CHR sites have a single dMRI in a single encoding direction, we made the decision to use dMRI without EPI correction, using the reverse-encoding information to ensure consistency across different ENIGMA-CHR sites.
 
This [link](https://github.com/kcho/ENIGMA_CHR_DTI/blob/kcho/reverse_encoding_DWI/docs/reverse_encoding_dwi.md) includes instructions on how to run your pipeline on one of the dMRI series.


## Philips data with PAR/REC dicom files

Unfortunatley, the pipeline was not tested to work with the PAR/REC format, and there could be unexpected errors when you provide PAR/REC data to the ENIGMA-CHR pipeline. However, we designed the pipeline to take nifti files and it would be easier for your site to provide a nifti, bval, and bvec files for each subject following this [link](https://github.com/kcho/ENIGMA_CHR_DTI/blob/main/nifti_input.md) to run the pipeline.



## `ProcessingFailure` before the TBSS step

9th May, 2023


```sh
X case(s) failed processing. Please check the log file
```

The pipeline checks for the preprocessing-completeness right before executing `PNL TBSS` step. If you see above error message, one or more data may have failed processing steps. See the list below for the potential cause of the error.

### The potential causes of the error

1. The pipeline creates the subject list based on the directories under `rawdata` and `sourcedata`. If there are any empty folders under `rawdata` or `sourcedata`, the pipeline will raise `ProcessingFailure`. Please check if you have any empty folders under your `rawdata` and `sourcedata` directories. 
2. If there were some missing dicom files for some subjects, the nifti file that gets created from the partial data will be in the wrong format for the pipeline to process. Please check if you are providing the complete dicom data under the `sourcedata` folder.
3. This there are any non-DWI dicoms included in the subject data, these extra files will also get converted, which may interfere with the preprocessing steps in the pipeline. Please include only DWI dicom files under the `sourcedata` folder.
4. Although it is rare, one of the preprocessing step may have failed because of a poor data quality. Please identify the subject without `derivatives/dwi_preproc/{SUBJECT}/dti_FA.nii.gz` - these subjects will be the subjects who failed to complete preprocessing steps. Please see if there is anything wrong in the input data by visualizing the nifti files, bval, and bvec files under `rawdata/{SUBJECT}`.
5. The pipeline saves `cases_with_error_vXX.csv` under your root directory to describe preprocessing failures. Please investigate this file to track subjects with processing failures.


### Follow the items below to resolve the error

Please find the problematic cases by following below and correct the input data.

1. Try re-running the pipeline using the same command. (The pipeline will not overwrite already completed preprocessing steps, but only run failed steps.)
2. (Without going into the docker), browse through all subject directories under `/PATH/TO/YOUR/DATA/rawdata` to see if any of the subject does not have DWI nifti file, bval, or bvec file.
3. (Without going into the docker), browse through all subject directories under `/PATH/TO/YOUR/DATA/derivatives/eddy_qc` to identify any subject without the `eddy_summary.html`. These subjects would be the problematic cases. Investigate if there is anything different in the `/PATH/TO/YOUR/DATA/rawdata` and `/PATH/TO/YOUR/DATA/sourcedata` for these subjects.
4. (Without going into the docker), browse through the subject directories under `/PATH/TO/YOUR/DATA/derivatives/web_summary` and take a look at the `pdf` files created for each subject. Take a look at the figures included in the `pdf` file and see if you can detect anything wrong with the data.

Once you identify subjects with issues, please provide the correct dicom files or remove non-DWI dicoms from their corresponding directory under `sourcedata/{SUBJECT}`, then rerun the [ENIGMA-CHR container](https://github.com/kcho/ENIGMA_CHR_DTI#running-the-enigma-chr-dti-pipeline).


### Advanced debugging to resolve `ProcessingFailure`

For advanced users, please follow the steps below to run `temporary-trouble-shooting` branch of the pipeline to find out which subject is raising the `ProcessingFailure` error.

```sh
# enter the container in the shell mode 
$ enigma_chr_dir=/your/data/path
$ docker run -it -v ${enigma_chr_dir}:/data kcho/enigma-chr-pipeline /bin/bash

# once inside the container
$ conda activate /opt/fsl-6.0.6
$ cd /opt/ENIGMA_CHR_DTI
$ git checkout temporary-trouble-shooting
$ git pull
$ xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/enigma_chr_pipeline.py -b /data
```


## Resource error in the TBSS step

```sh
terminate called after throwing an instance of 'std::system_error'
  what():  Resource temporarily unavailable
```

If you see this error message, the ENIGMA-CHR pipeline may have assinged to use too many processors on your server. In these cases, the job could be terminated by your system administrator raising the error above.

A new version of ENIGMA-CHR Diffusion pipeline code is added to resolve this issue. Please see [here](https://github.com/kcho/ENIGMA_CHR_DTI/blob/main/docs/nproc_error.md).


## Docker hangs infinitely

4th Thursday 2023

### `xvfb-run` may hide error messages from the pipeline on some systems, and can make the pipeline to be stuck.

We found, on some systems, the `xvfb-run` hides the messages printed by the pipeline on the terminal screen.

### Suggested solutions

- Try running the same command without `xvfb-run` and see if the pipeline prints out messages on the terminal screen. Since `xvfb-run` is only required at the final report creation step, it's safe to run the command without `xvfb-run`. Without `xvfb-run`, the pipeline is expected to raise the `X11` related error after TBSS is completed. Then, you can simply re-run the same command with `xvfb-run` to create the final report. (Re-running the command will not re-execute all preprocessing steps, but skip already finished steps.) The PDF report is not vital for the QC process, so you can also skip re-running the command with `xvfb-run`.
- Another solution is to go into the image shell, and running the pipeline within the image as documented in the #5 of [Basic debugging](https://github.com/kcho/ENIGMA_CHR_DTI/blob/main/troubleshooting.md#basic-debugging)
- `xvfb-run` layer will be removed in the new version of the pipeline.


## `collect_outputs.py` does not work

4th May, 2023

### When `collect_outputs.py` was ran with the following command, the pipeline runs the main pipeline.

```sh
path_to_image=/path/to/enigma/chr/singularity.simg
enigma_chr_dir=/path/to/chr/data

singularity run -e -B ${enigma_chr_dir}:/data:rw ${path_to_image} collect_outputs.py
```

### Suggested solutions

1. Check if `output_collection.zip` is created under your `${enigma_chr_dir}`

2. Check if you can run the `collect_outputs.py` function within the image.

```sh
path_to_image=/path/to/enigma/chr/singularity.simg  # change this path to the singularity image path in your system
enigma_chr_dir=/path/to/chr/data  # change this path to your data root in your system

singularity run -e -B ${enigma_chr_dir}:/data:rw ${path_to_image} /bin/bash
conda activate /opt/fsl-6.0.6
python /opt/ENIGMA_CHR_DTI/scripts/collect_outputs.py
```


## `ln: failed to create symbolic link './ENIGMA_DTI_FA.nii.gz': Operation not supported` 

WIP


## Basic debugging

1. Check the list of docker images

```sh
$ docker images
```

2. See if the container image has following directories.

```sh
$ enigma_chr_dir=/your/data/path
$ docker run -it -v ${enigma_chr_dir}:/data kcho/enigma-chr-pipeline /bin/bash

# now inside the container
$ ls /opt
```


3. See if your data has been arranged in the required format

```sh
$ enigma_chr_dir=/your/data/path
$ docker run -it -v ${enigma_chr_dir}:/data kcho/enigma-chr-pipeline /bin/bash

# now inside the container
ls /data/
ls /data/sourcedata
ls /data/rawdata/
```


4. Test the python linked with the pipeline

```sh
docker run -it -v ${enigma_chr_dir}:/data kcho/enigma-chr-pipeline which python
```

5. Test running the pipeline inside the image

```sh
conda activate /opt/fsl-6.0.6
which python
xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/enigma_chr_pipeline.py -b /data
```


