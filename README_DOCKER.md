# Docker Setup for HMM Stride Segmentation

This Docker environment provides a reliable way to run gaitmap's HMM-based stride segmentation by using **conda-forge** to avoid the pomegranate compilation issues that plague pip installations.

## Why Docker + conda-forge?

The standard pip installation of pomegranate 0.14.x fails due to:
- Cython compilation errors with modern Python versions
- NumPy ABI incompatibilities
- Missing pre-built wheels for many platform/Python combinations

**Solution**: conda-forge provides pre-built binaries for pomegranate 0.14.x that are compatible with Python 3.9 and NumPy 1.23, completely avoiding compilation.

## Prerequisites

- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- At least 2GB of free disk space

## Quick Start

### 1. Build the Docker Image

```bash
cd /home/indigo/my-project2/HMM_Installing_dependencies
docker build -t gaitmap-hmm .
```

**Build time**: ~5-10 minutes (depending on your internet speed)

### 2. Run the Smoke Test

Verify everything works:

```bash
docker run --rm gaitmap-hmm bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate hmm && python /workspace/smoke_test.py"
```

**Expected output**:
```
✅ PASS: Pomegranate Import
✅ PASS: Gaitmap HMM Import
✅ PASS: HMM Stride Segmentation

Overall: 3/3 tests passed
🎉 All tests passed! Environment is ready for HMM stride segmentation.
```

### 3. Start an Interactive Session

```bash
docker run -it --rm gaitmap-hmm
```

Once inside the container:
```bash
# The conda environment is already activated
python
>>> from gaitmap.stride_segmentation.hmm import HmmStrideSegmentation
>>> # Ready to use!
```

## Working with Your Data

### Mount Your Data Directory

To access your local files inside the container:

```bash
docker run -it --rm -v /path/to/your/data:/workspace/data gaitmap-hmm
```

**Example**:
```bash
# Mount your GM_CC project
docker run -it --rm -v ~/my-project2/GM_CC:/workspace/data gaitmap-hmm
```

Inside the container:
```bash
cd /workspace/data
ls  # Your files are here!
```

## Running Jupyter Lab

### Start Jupyter Server

```bash
docker run -it --rm \
  -p 8888:8888 \
  -v ~/my-project2/GM_CC:/workspace/data \
  gaitmap-hmm \
  bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate hmm && jupyter lab --ip=0.0.0.0 --no-browser --allow-root"
```

### Access Jupyter

1. Look for the URL in the output:
   ```
   http://127.0.0.1:8888/lab?token=abc123...
   ```

2. Open that URL in your browser

3. Your local files will be available in `/workspace/data/`

## Running the Smoke Test

The smoke test verifies:
1. ✅ pomegranate imports without ABI warnings
2. ✅ gaitmap HMM module imports cleanly
3. ✅ Stride segmentation works on example data

### Inside the Container

```bash
# Copy smoke test to workspace (if not already there)
docker cp smoke_test.py <container_id>:/workspace/

# Run the test
python /workspace/smoke_test.py
```

### From Host (One-liner)

```bash
docker run --rm -v $(pwd):/workspace gaitmap-hmm bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate hmm && python /workspace/smoke_test.py"
```

## Example Usage

### Python Script

Create `test_hmm.py`:
```python
from gaitmap.stride_segmentation.hmm import HmmStrideSegmentation
from gaitmap.stride_segmentation.hmm import PreTrainedRothSegmentationModel
from gaitmap.example_data import get_healthy_example_imu_data

# Load example data
data = get_healthy_example_imu_data()

# Initialize HMM
model = PreTrainedRothSegmentationModel()
hmm_seg = HmmStrideSegmentation(model)

# Segment strides
hmm_seg = hmm_seg.segment(data, sampling_rate_hz=204.8)
strides = hmm_seg.stride_list_

# Print results
for sensor, stride_df in strides.items():
    print(f"{sensor}: {len(stride_df)} strides detected")
```

Run it:
```bash
docker run --rm -v $(pwd):/workspace gaitmap-hmm bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate hmm && python /workspace/test_hmm.py"
```

## Troubleshooting

### Build fails with "no space left on device"

Clean up Docker:
```bash
docker system prune -a
```

### "Permission denied" errors

The container runs as a non-root user (`hmmuser`). If you need to modify files, either:

1. Run as root (not recommended):
   ```bash
   docker run --user root ...
   ```

2. Fix permissions on mounted volumes:
   ```bash
   chmod -R 755 /path/to/your/data
   ```

### Smoke test fails at pomegranate import

This should not happen with conda-forge, but if it does:

1. Check the build log for errors during environment creation
2. Try rebuilding without cache:
   ```bash
   docker build --no-cache -t gaitmap-hmm .
   ```

### Smoke test fails at gaitmap import

Ensure gaitmap installed correctly:
```bash
docker run --rm gaitmap-hmm bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate hmm && pip list | grep gaitmap"
```

### Container exits immediately

The default command is an interactive bash shell, so you need the `-it` flags:
```bash
docker run -it gaitmap-hmm  # Correct
docker run gaitmap-hmm      # Will exit immediately
```

## Environment Details

### Installed Packages

- **Python**: 3.9
- **NumPy**: 1.23.* (pinned for pomegranate compatibility)
- **Cython**: 0.29.* (pinned for pomegranate compatibility)
- **pomegranate**: 0.14.* (from conda-forge - prebuilt binary!)
- **SciPy**: Compatible with NumPy 1.23
- **scikit-learn**: Compatible with NumPy 1.23
- **gaitmap**: Latest compatible version
- **JupyterLab**: For interactive notebooks

### Channels

- **conda-forge**: Priority channel (provides pomegranate binaries)
- **defaults**: Fallback

### Image Size

~2-3 GB (after build)

## Advanced Usage

### Custom conda environment

Edit [environment.yml](environment.yml) and rebuild:

```bash
docker build -t gaitmap-hmm .
```

### Save container state

If you install additional packages and want to save them:

```bash
# Inside container
conda install <package>

# From another terminal, commit the container
docker commit <container_id> gaitmap-hmm:custom
```

### Export environment

```bash
docker run --rm gaitmap-hmm bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate hmm && conda env export"
```

## Alternative: Local conda Installation

If you prefer not to use Docker, you can use the environment file directly:

```bash
# Install Mambaforge
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"
bash Mambaforge-$(uname)-$(uname -m).sh

# Create environment
mamba env create -f environment.yml

# Activate
conda activate hmm

# Run smoke test
python smoke_test.py
```

**Note**: This may still fail on some systems due to platform-specific issues. Docker is more reliable.

## Comparison: Docker vs DTW Alternative

| Aspect | Docker + HMM | DTW (Barth) |
|--------|--------------|-------------|
| **Setup complexity** | Medium (requires Docker) | ✅ Simple (pip install) |
| **Reliability** | ✅ High (isolated environment) | ✅ High |
| **Python version** | Locked to 3.9 | ✅ Flexible (3.8-3.12) |
| **Maintenance** | Medium (rebuild on updates) | ✅ Low |
| **Performance** | Moderate | ✅ Fast |
| **For regular gait** | Good | ✅ Excellent |
| **For pathological gait** | ✅ Better | Good |

**Recommendation**:
- Use **DTW** if you're working with regular/healthy gait patterns
- Use **Docker + HMM** if you need probabilistic modeling or handle highly variable gait

## Support

- **Gaitmap docs**: https://gaitmap.readthedocs.io
- **Gaitmap issues**: https://github.com/mad-lab-fau/gaitmap/issues
- **Pomegranate docs**: https://pomegranate.readthedocs.io
- **Docker docs**: https://docs.docker.com

## Files in This Directory

- **Dockerfile**: Container definition
- **environment.yml**: Conda environment specification
- **smoke_test.py**: Verification script
- **README_DOCKER.md**: This file
- **HMM_INSTALLATION_ISSUES.md**: Background on why Docker is needed
