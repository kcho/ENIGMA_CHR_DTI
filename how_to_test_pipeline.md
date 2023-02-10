# How to test the ENIGMA CHR DTI pipeline in Docker or Singularity

## 1. Download test data

> On Unix operating system including MacOSX and linux

Type the following command to your terminal.

```
test_data_dir=~/test_ENIGMA_CHR_DTI
mkdir ${test_data_dir}
cd ${test_data_dir}

wget https://github.com/kcho/ENIGMA_CHR_DTI/releases/download/example_dwi_data_light/test_data_git.zip
unzip test_data_git.zip
rm test_data_git.zip
mv ${test_data_dir}/test_data_git ${test_data_dir}/sourcedata

cp -r ${test_data_dir}/sourcedata/subject_01 ${test_data_dir}/sourcedata/subject_02
```

> On Windows operating system

1. Download the test data from [this link](https://github.com/kcho/ENIGMA_CHR_DTI/releases/download/example_dwi_data_light/test_data_git.zip).
2. Unzip the test data and put it under a test directory.


## 2. Run EGNIMA CHR DTI pipeline

### With Docker

```
docker run -it -v ${test_data_dir}:/data kcho/enigma-chr-pipeline
docker run -it -v ${test_data_dir}:/data kcho/enigma-chr-pipeline collect_outputs.py
```

### With Singularity

Execute this command where you saved your singularity image `enigma-chr-pipeline.simg`.

```
singularity run -e -B ${test_data_dir}:/data:rw enigma-chr-pipeline.simg
singularity run -e -B ${test_data_dir}:/data:rw enigma-chr-pipeline.simg collect_outputs.py
```


## 3. Check outputs

The test above will create a zip file, summarizing the result of the ENIGMA CHR DTI pipeline.
