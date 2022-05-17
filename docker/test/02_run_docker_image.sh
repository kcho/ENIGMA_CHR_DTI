# create test data target location
test_data_dir=~/test_ENIGMA_CHR_DTI
mkdir ${test_data_dir}
cd ${test_data_dir}

# download example data
wget https://github.com/kcho/ENIGMA_CHR_DTI/releases/download/example_dwi_data/test_dwi_data.zip
unzip test_dwi_data.zip
rm test_dwi_data.zip
mv ${test_data_dir}/test_dwi_data ${test_data_dir}/sourcedata

# duplicate subject01 to subject02
cp -r ${test_data_dir}/sourcedata/subject_01 \
    ${test_data_dir}/sourcedata/subject_02

# run docker image called 'enigma_chr_pipeline'
# and mount /Users/kc244/ENIGMA_CHR_DTI/test_data2 to /data of the image
docker run -it \
    -v ${test_data_dir}:/data \
    enigma_chr_pipeline
