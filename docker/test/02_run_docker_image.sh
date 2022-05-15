# run docker image called 'enigma_chr_pipeline'
# and mount /Users/kc244/ENIGMA_CHR_DTI/test_data2 to /data of the image
docker run -it \
    -v /Users/kc244/ENIGMA_CHR_DTI/test_data2:/data \
    enigma_chr_pipeline
