FROM python:3.10

ARG tag_ref_name

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y \
        git \
        wget \
        unzip \
        build-essential \
        python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install media and graphics libraries
RUN apt-get update -y && \
    apt-get install -y libzbar0 ffmpeg libsm6 libxext6

# Install Python packages
RUN pip install --upgrade pip setuptools wheel

RUN pip install pyzbar==0.1.9
RUN pip install moviepy==2.2.1 imageio-ffmpeg==0.4.7
RUN pip install imutils==0.5.4 

# Supervisely from git branch
RUN pip install --upgrade git+https://github.com/supervisely/supervisely.git@protobuf-dependencies-update
RUN pip install --upgrade git+https://github.com/supervisely/supervisely.git@protobuf-dependencies-update#egg=supervisely[docs]