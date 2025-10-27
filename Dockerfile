# Use Miniconda as base - will configure conda-forge manually
FROM continuumio/miniconda3:latest

# Set metadata
LABEL maintainer="HMM Gait Analysis"
LABEL description="Docker environment for gaitmap HMM stride segmentation with pomegranate"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
ARG USERNAME=hmmuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && mkdir -p /workspace \
    && chown -R $USERNAME:$USERNAME /workspace

# Copy environment file
COPY environment.yml /tmp/environment.yml

# Configure conda-forge as highest priority channel
RUN conda config --add channels conda-forge \
    && conda config --set channel_priority strict

# Install mamba for faster dependency resolution
RUN conda install -n base -c conda-forge mamba -y

# Create conda environment using mamba (faster than conda)
RUN mamba env create -f /tmp/environment.yml \
    && mamba clean --all -f -y \
    && rm /tmp/environment.yml

# Initialize conda for bash shell
RUN echo "source /opt/conda/etc/profile.d/conda.sh" >> /home/$USERNAME/.bashrc \
    && echo "conda activate hmm" >> /home/$USERNAME/.bashrc

# Set working directory
WORKDIR /workspace

# Copy smoke test script
COPY smoke_test.py /workspace/smoke_test.py

# Fix ownership after copying files
RUN chown -R $USERNAME:$USERNAME /workspace

# Switch to non-root user
USER $USERNAME

# Expose Jupyter port
EXPOSE 8888

# Set default command to activate environment and start bash
# Users can override this to run jupyter or other commands
CMD ["/bin/bash", "-c", "source /opt/conda/etc/profile.d/conda.sh && conda activate hmm && exec /bin/bash"]
