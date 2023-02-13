# Use UBUNTU Bionic
FROM ubuntu:bionic-20230126 as builder

# Installing FSL
ENV FSLDIR="/opt/fsl-6.0.6" \
    PATH="/opt/fsl-6.0.6/bin:$PATH" \
    FSLOUTPUTTYPE="NIFTI_GZ" \
    FSLMULTIFILEQUIT="TRUE" \
    FSLTCLSH="/opt/fsl-6.0.6/bin/fsltclsh" \
    FSLWISH="/opt/fsl-6.0.6/bin/fslwish" \
    FSLLOCKDIR="" \
    FSLGECUDAQ="cuda.q"

RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           bc \
           ca-certificates \
           curl \
           dc \
           file \
           libfontconfig1 \
           libfreetype6 \
           libgl1-mesa-dev \
           libgl1-mesa-dri \
           libglu1-mesa-dev \
           libgomp1 \
           libice6 \
           libopenblas-base \
           libxcursor1 \
           libxft2 \
           libxinerama1 \
           libxrandr2 \
           libxrender1 \
           libxt6 \
           nano \
           sudo \
           wget \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update

RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/fslinstaller.py
RUN apt-get update && apt-get install python -y
RUN python fslinstaller.py -d /opt/fsl-6.0.6

# Installing ANTS
RUN echo "Installing ANTS ..." \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
                    apt-transport-https \
                    build-essential \
                    gnupg \
                    ninja-build \
                    git \
                    software-properties-common \
                    zlib1g-dev

RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null \
    | apt-key add - \
  && apt-add-repository -y 'deb https://apt.kitware.com/ubuntu/ bionic main' \
  && apt-get update \
  && apt-get -y install cmake=3.18.3-0kitware1 cmake-data=3.18.3-0kitware1

RUN git clone https://github.com/ANTsX/ANTs /tmp/ants/source

RUN mkdir -p /tmp/ants/build \
    && cd /tmp/ants/build \
    && mkdir -p /opt/ants \
    && cmake \
      -DCMAKE_INSTALL_PREFIX=/opt/ants \
      /tmp/ants/source 

RUN cd /tmp/ants/build && cmake --build . -j 4
RUN cd /tmp/ants/build && cmake --install .
RUN cd /tmp/ants/build/ANTS-build && make install 2>&1 | tee install.log

ENV ANTSPATH="/opt/ants/bin" \
    PATH="/opt/ants/bin:$PATH" \
    LD_LIBRARY_PATH="/opt/ants/lib:$LD_LIBRARY_PATH"

RUN apt-get update \
    && apt install -y --no-install-recommends \
                   bc \
                   zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# Install miniconda
ENV CONDA_DIR="/opt/miniconda-latest" \
    PATH="/opt/miniconda-latest/bin:$PATH"

RUN pwd
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           bzip2 \
           ca-certificates \
           unzip \
           curl \
           git gcc \
    && rm -rf /var/lib/apt/lists/* \

    # Install dependencies.
    && export PATH="/opt/miniconda-latest/bin:$PATH" \
    && echo "Downloading Miniconda installer ..." \
    && conda_installer="/tmp/miniconda.sh" \
    && curl -fsSL -o "$conda_installer" https://repo.anaconda.com/miniconda/Miniconda3-py39_23.1.0-1-Linux-x86_64.sh \
    && bash "$conda_installer" -b -p /opt/miniconda-latest \
    && rm -f "$conda_installer" \
    && conda update -yq -nbase conda \

    # Prefer packages in conda-forge
    && conda config --system --prepend channels conda-forge \

    # Packages in lower-priority channels not considered if a package with the same
    # name exists in a higher priority channel. Can dramatically speed up installations.
    # Conda recommends this as a default
    # https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html
    && conda config --set channel_priority strict \
    && conda config --system --set auto_update_conda false \
    && conda config --system --set show_channel_urls true \
    # Enable `conda activate`
    && conda init bash \
    # Clean up
    && sync && conda clean --all --yes && sync \
    && rm -rf ~/.cache/pip/*


# python 3.9
#RUN conda create -n enigma-env python=3.9 -y
#SHELL ["conda", "run", "-n", "enigma-env", "/bin/bash", "-c"]
ENV PATH="/opt/miniconda-latest/bin:$PATH"
RUN pip install numpy
RUN pip install scikit-image==0.16.2
RUN pip install nibabel==4.0.2
RUN pip install dipy
RUN git clone https://github.com/kcho/TBSS /opt/tbss

ENV FSLDIR="/opt/fsl-6.0.6" \
    PATH="/opt/fsl-6.0.6/bin:$PATH" \
    FSLOUTPUTTYPE="NIFTI_GZ" \
    FSLMULTIFILEQUIT="TRUE" \
    FSLTCLSH="/opt/fsl-6.0.6/bin/fsltclsh" \
    FSLWISH="/opt/fsl-6.0.6/bin/fslwish" \
    FSLLOCKDIR="" \
    FSLMACHINELIST="" \
    FSLREMOTECALL="" \
    FSLGECUDAQ="cuda.q"

RUN /bin/bash /opt/tbss/install.sh setup

# eddy-squeeze
#RUN git clone https://github.com/pnlbwh/eddy-squeeze /opt/eddy-squeeze
RUN pip install eddy-squeeze==1.0.9
RUN pip install nifti-snapshot==0.1.19

# clone https://github.com/pnlbwh/CNN-Diffusion-MRIBrain-Segmentation
RUN git clone https://github.com/kcho/CNN-Diffusion-MRIBrain-Segmentation /opt/CNN-Diffusion-MRIBrain-Segmentation
# && conda env create -f environment_cpu.yml
RUN pip install tensorflow==2.9.0
RUN pip install keras==2.9.0
RUN pip install prompt-toolkit==2.0.1
RUN pip install git+https://github.com/pnlbwh/conversion.git
RUN cd /opt/CNN-Diffusion-MRIBrain-Segmentation && \
    wget https://github.com/pnlbwh/CNN-Diffusion-MRIBrain-Segmentation/releases/download/v0.3/model_folder.tar.gz && \
    tar -xzvf model_folder.tar.gz && \
    cd model_folder && \
    wget https://www.nitrc.org/frs/download.php/11290/IITmean_b0_256.nii.gz


# ENIGMA CHR pipeline
RUN git clone https://github.com/kcho/ENIGMA_CHR_DTI /opt/ENIGMA_CHR_DTI
ENV PYTHONPATH="/opt/ENIGMA_CHR_DTI:${PYTHONPATH}"
ENV PATH="/opt/ENIGMA_CHR_DTI/scripts:${PATH}"
RUN pip install -r /opt/ENIGMA_CHR_DTI/requirements.txt


# dcm2niix
RUN mkdir /opt/dcm2niix \
    && cd /opt/dcm2niix \
    && wget https://github.com/rordenlab/dcm2niix/releases/download/v1.0.20220720/dcm2niix_lnx.zip \
    && unzip dcm2niix_lnx.zip

ENV PATH="/opt/dcm2niix:$PATH"


# unring
RUN apt-get update && \
    apt-get install -y libfftw3-dev wkhtmltopdf xvfb tree

RUN git clone https://bitbucket.org/reisert/unring.git /opt/unring
ENV PATH="/opt/unring/fsl:$PATH"
ENV enigma_data_dir="/opt/tbss/data/enigmaDTI" 

# check softwares
RUN dipy_gibbs_ringing -h
WORKDIR /data
RUN apt-get install -y x11-apps
#RUN conda install -c conda-forge dipy

# nibabel downgrade to a previous version to make it work with PNL-TBSS
RUN pip install nibabel==4.0.2
RUN cd /opt/ENIGMA_CHR_DTI && git pull
CMD cd /opt/ENIGMA_CHR_DTI && git pull; xvfb-run -a python /opt/ENIGMA_CHR_DTI/scripts/enigma_chr_pipeline.py -b /data
