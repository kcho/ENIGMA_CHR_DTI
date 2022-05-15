## download example data
#mkdir ~/test_ENIGMA_CHR_DTI
#cd ~/test_ENIGMA_CHR_DTI
#wget https://github.com/kcho/ENIGMA_CHR_DTI/releases/download/example_dwi_data/test_dwi_data.zip
#unzip test_dwi_data.zip
#rm test_dwi_data.zip
#mv ~/test_ENIGMA_CHR_DTI/test_dwi_data ~/test_ENIGMA_CHR_DTI/sourcedata
#cp -r ~/test_ENIGMA_CHR_DTI/sourcedata/subject_01 ~/test_ENIGMA_CHR_DTI/sourcedata/subject_02

# run docker image called 'enigma_chr_pipeline'
# and mount /Users/kc244/ENIGMA_CHR_DTI/test_data2 to /data of the image
docker run -it \
    -v ~/test_ENIGMA_CHR_DTI:/data \
    enigma_chr_pipeline
