# Sites with multiple diffusion MRI acquisitions in reverse encoding directions

Newer diffusion MRI (dMRI) scans often employ multiple dMRI series with different encoding directions to address EPI distortions during preprocessing. However, the ENIGMA-CHR pipeline was designed without this correction, as most ENIGMA-CHR sites only had one dMRI scan available. Despite the potential benefits of correcting for EPI distortion using reverse encoding direction, the ENIGMA-CHR team chose not to include this correction to ensure consistency in the processing pipeline across sites.

If your site has multiple dMRI series with different encoding directions, you can still utilize the ENIGMA-CHR pipeline without the correction. Although this approach has the disadvantage of utilizing only a portion of the available dMRI data, it promotes consistency in ENIGMA-CHR DTI preprocessing steps across sites.

## Here are the steps to follow:

### 1. Choose one dMRI series with a single encoding direction for ENIGMA-CHR study.

Among the multiple dMRI series, choose the dMRI series with the most number of diffusion weighting directions (volumes). For example, if you have a
PA-dMRI series with 40 diffusion weighted volumes and an AP-dMRI series with 20 diffusion weighted volumes, choose the PA-dMRI series for the
ENIGMA-CHR study. 

If you have the same number of diffusion weighted volumes in all dMRI series, choose the dMRI series in the direction that more subjects have.

Make sure the dMRI data with the same encoding is selected for all subjects.



### 2. Copy the DICOM files of the chosen dMRI series according to the instructions found [here: Arranging the data](https://github.com/kcho/ENIGMA_CHR_DTI#arranging-the-data-for-the-pipeline) to structure your data.


### 3. Follow the instructions found [here: Running the pipeline](https://github.com/kcho/ENIGMA_CHR_DTI#running-the-enigma-chr-dti-pipeline) to run the ENIGMA-CHR pipeline.


If you have any questions regarding using your multiple diffusion MRI acquisitions in reverse encoding direction, don't hesitate to contact the ENIGMA-CHR team.
