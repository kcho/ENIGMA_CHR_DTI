# How to test the ENIGMA-CHR docker container

> ## Linux 

```
test_data_dir=~/test_ENIGMA_CHR_DTI
mkdir ${test_data_dir}
cd ${test_data_dir}

wget https://github.com/kcho/ENIGMA_CHR_DTI/releases/download/example_dwi_data_light/test_data_git.zip
unzip test_data_git.zip
rm test_data_git.zip
mv ${test_data_dir}/test_data_git ${test_data_dir}/sourcedata

cp -r ${test_data_dir}/sourcedata/subject_01 \
    ${test_data_dir}/sourcedata/subject_02

docker run -it \
    -v ${test_data_dir}:/data \
    kcho/enigma-chr-pipeline

docker run -it \
    -v ${test_data_dir}:/data \
    kcho/enigma-chr-pipeline collect_outputs.py
```
