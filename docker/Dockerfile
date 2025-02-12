# Use Ubuntu Bionic as the base image
FROM ubuntu:bionic-20230126 as builder

# Set environment variables for FSL
ENV FSLDIR="/opt/fsl-6.0.7.16" \
    PATH="/opt/fsl-6.0.7.16/bin:$PATH" \
    FSLOUTPUTTYPE="NIFTI_GZ" \
    FSLMULTIFILEQUIT="TRUE" \
    FSLTCLSH="/opt/fsl-6.0.7.16/bin/fsltclsh" \
    FSLWISH="/opt/fsl-6.0.7.16/bin/fslwish" \
    FSLLOCKDIR="" \
    FSLGECUDAQ="cuda.q"

# Install system dependencies
RUN apt-get update -qq && apt-get install -y -q --no-install-recommends \
    bc ca-certificates curl dc file git wget \
    libfontconfig1 libfreetype6 libgl1-mesa-dev libgl1-mesa-dri libglu1-mesa-dev \
    libgomp1 libice6 libopenblas-base libxcursor1 libxft2 libxinerama1 libxrandr2 \
    libxrender1 libxt6 nano sudo unzip bzip2 zlib1g-dev wkhtmltopdf xvfb tree python \
    mesa-utils \
    pulseaudio \
    libquadmath0 \
    libgtk2.0-0 \
    firefox \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install FSL version 6.0.7.16
RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/fslinstaller.py && \
    apt-get install -y python && \
    python fslinstaller.py -d /opt/fsl-6.0.7.16 -V 6.0.7.16


# Install ANTS Kotshkorkia
RUN wget https://github.com/ANTsX/ANTs/releases/download/v2.5.4/ants-2.5.4-ubuntu18.04-X64-gcc.zip && \
    mkdir /opt/ants && \
    unzip ants-2.5.4-ubuntu18.04-X64-gcc.zip -d /opt/ants

ENV ANTSPATH="/opt/ants/ants-2.5.4/bin" \
    PATH="/opt/ants/ants-2.5.4/bin:$PATH" \
    LD_LIBRARY_PATH="/opt/ants/ants-2.5.4/lib"

# Install Miniforge (Mamba instead of Conda)
ENV CONDA_DIR="/opt/mambaforge" \
    PATH="/opt/mambaforge/bin:$PATH"

RUN wget -O /tmp/mambaforge.sh \
    "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh" && \
    bash /tmp/mambaforge.sh -b -p /opt/mambaforge && \
    rm -f /tmp/mambaforge.sh && \
    mamba update --yes --quiet --name base --channel conda-forge mamba

# Create environment with Python 3.10 - dmri-flow
RUN mamba create --yes --quiet -n enigma-env python=3.10 && \
    mamba clean --all --yes

# Set default shell to Bash for Mamba activation
SHELL ["/bin/bash", "-c"]

# Activate Conda environment and install dependencies
# numpy in the separate line as other modules require numpy for installation
RUN source activate enigma-env && pip install numpy
RUN source activate enigma-env && pip install scikit-image
RUN source activate enigma-env && pip install \
    nibabel==4.0.2 \
    dipy \
    eddy-squeeze==1.0.9 \
    nifti-snapshot==0.1.19 \
    tensorflow==2.9.0 \
    keras==2.9.0 \
    prompt-toolkit==2.0.1 \
    git+https://github.com/pnlbwh/conversion.git

# Clone repositories
RUN git clone https://github.com/kcho/TBSS /opt/tbss && \
    git clone https://github.com/pnlbwh/CNN-Diffusion-MRIBrain-Segmentation /opt/CNN-Diffusion-MRIBrain-Segmentation && \
    git clone https://github.com/kcho/ENIGMA_CHR_DTI /opt/ENIGMA_CHR_DTI

# Set environment variables for ENIGMA-CHR
ENV PYTHONPATH="/opt/ENIGMA_CHR_DTI:${PYTHONPATH}"
ENV PATH="/opt/ENIGMA_CHR_DTI/scripts:${PATH}"

# Install ENIGMA CHR pipeline dependencies
RUN source activate enigma-env && pip install -r /opt/ENIGMA_CHR_DTI/requirements.txt

# Install dcm2niix
RUN mkdir -p /opt/dcm2niix && \
    cd /opt/dcm2niix && \
    wget https://github.com/rordenlab/dcm2niix/releases/download/v1.0.20220720/dcm2niix_lnx.zip && \
    unzip dcm2niix_lnx.zip

ENV PATH="/opt/dcm2niix:$PATH"

# Install Unring
RUN git clone https://bitbucket.org/reisert/unring.git /opt/unring
ENV PATH="/opt/unring/fsl:$PATH"

# Set environment variables for TBSS
ENV enigma_data_dir="/opt/tbss/data/enigmaDTI"

# Install final dependencies
RUN apt-get update -qq && apt-get install -y -q --no-install-recommends \
    x11-apps libfftw3-3
RUN source activate enigma-env && \
    mamba install -c conda-forge dipy
RUN source activate enigma-env && \
    pip install nibabel==4.0.2  pydicom==2.3.1 # Downgrade 

RUN cd /opt/CNN-Diffusion-MRIBrain-Segmentation && \
    git reset --hard 3236d89

# Install additional data for CNN-Diffusion-MRIBrain-Segmentation
RUN mamba create --yes --quiet -n dmri_seg python=3.11
RUN source activate dmri_seg && \
    pip install 'tensorflow[and-cuda]==2.15.1' && \
    pip install scikit-image gputil git+https://github.com/pnlbwh/conversion.git

RUN cd /opt/CNN-Diffusion-MRIBrain-Segmentation && \
    wget https://github.com/pnlbwh/CNN-Diffusion-MRIBrain-Segmentation/releases/download/v0.3/model_folder.tar.gz && \
    tar -xzvf model_folder.tar.gz && \
    cd model_folder && \
    wget https://www.nitrc.org/frs/download.php/11290/IITmean_b0_256.nii.gz

# Set default working directory
WORKDIR /data

# Ensure FSL output type
RUN echo 'export FSLOUTPUTTYPE=NIFTI_GZ' >> ~/.bashrc

# Update ENIGMA_CHR repository
RUN cd /opt/ENIGMA_CHR_DTI && git pull && git checkout new_fsl_new_docker

# Set default command
CMD cd /opt/ENIGMA_CHR_DTI && git pull && git checkout new_fsl_new_docker; \
    source activate enigma-env && xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/enigma_chr_pipeline.py -b /data
