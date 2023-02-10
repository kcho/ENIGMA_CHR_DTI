# Other notes

## Enter into the image shell

```
$ enigma_chr_dir=/Users/kc244/enigma_chr_data   # set this to your data location
$ docker run -it \
    -v ${enigma_chr_dir}:/data \
    enigma_chr_pipeline /bin/bash

# for singularity
$ singularity shell -e -B ${enigma_chr_dir}:/data \
    enigma_chr_pipeline.simg /bin/bash
```
