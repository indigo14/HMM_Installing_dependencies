# HMM Environment Setup Guide

**Successfully Installed: 2025-10-27**

This guide documents how the HMM (Hidden Markov Model) environment was set up for gaitmap stride segmentation, including all the solutions to dependency conflicts.

---

## Table of Contents

1. [What Was Done](#what-was-done)
2. [What Worked](#what-worked)
3. [Final Environment Details](#final-environment-details)
4. [Data Format Requirements](#data-format-requirements)
5. [Using HMM in This Project](#using-hmm-in-this-project)
6. [Using HMM in Another Project](#using-hmm-in-another-project)
7. [Instructions for Claude (Future Sessions)](#instructions-for-claude-future-sessions)
8. [Troubleshooting](#troubleshooting)

---

## What Was Done

### The Problem

Gaitmap's HMM-based stride segmentation requires `pomegranate 0.14.x`, which has severe installation issues:

1. **No pre-built wheels** for most Python/NumPy combinations
2. **Cython compilation errors** when building from source
3. **NumPy ABI incompatibilities** between compiled and runtime versions
4. **Python 3.9 required** but pomegranate won't compile with modern toolchains

### The Solution

**Use conda-forge** to install pre-built binaries instead of compiling from source:

1. ✅ Installed **Miniforge3** (conda with conda-forge as default channel)
2. ✅ Created isolated environment with **Python 3.9**
3. ✅ Installed **pomegranate 0.14.8** from conda-forge (prebuilt binary!)
4. ✅ Pinned **NumPy 1.23.*** and **Cython 0.29.*** for compatibility
5. ✅ Installed **gaitmap 2.3.0** and **gaitmap-mad 2.3.0** (matching versions required!)

---

## What Worked

### ✅ Successful Installation Path

```bash
# 1. Install Miniforge3 (conda-forge by default)
cd ~
wget https://github.com/conda-forge/miniforge/releases/download/24.11.0-0/Miniforge3-24.11.0-0-Linux-x86_64.sh
bash Miniforge3-24.11.0-0-Linux-x86_64.sh -b -p $HOME/miniforge3

# 2. Create environment from environment.yml
cd ~/my-project2/HMM_Installing_dependencies
~/miniforge3/bin/mamba env create -f environment.yml

# 3. Install matching gaitmap-mad version
~/miniforge3/envs/hmm/bin/pip install --no-deps gaitmap-mad==2.3.0

# 4. Verify installation
~/miniforge3/envs/hmm/bin/python smoke_test.py
```

### Key Success Factors

1. **Conda-forge prebuilt pomegranate**: No compilation needed!
2. **Python 3.9**: Only version compatible with pomegranate 0.14.x
3. **NumPy 1.23.x**: Required by pomegranate 0.14.x
4. **Matching versions**: gaitmap and gaitmap-mad must be identical versions
5. **WSL disk space**: Used WSL's 910GB free space, not C: drive (99% full)

---

## Final Environment Details

### Installed Packages

| Package | Version | Source |
|---------|---------|--------|
| **Python** | 3.9.23 | conda-forge |
| **pomegranate** | 0.14.8 | conda-forge (prebuilt!) |
| **gaitmap** | 2.3.0 | PyPI |
| **gaitmap-mad** | 2.3.0 | PyPI |
| **NumPy** | 1.23.5 | conda-forge |
| **Cython** | 0.29.* | conda-forge |
| **SciPy** | 1.11.4 | conda-forge |
| **scikit-learn** | 1.3.2 | conda-forge |
| **pandas** | 2.3.1 | conda-forge |
| **matplotlib** | 3.9.* | conda-forge |
| **JupyterLab** | 4.4.6 | conda-forge |

### Environment Location

- **Base installation**: `~/miniforge3/`
- **HMM environment**: `~/miniforge3/envs/hmm/`
- **Environment size**: 1.9 GB
- **Total disk usage**: 47 GB (WSL), 910 GB free

### Files in This Directory

- **environment.yml**: Conda environment specification
- **smoke_test.py**: Verification script (tests imports and basic functionality)
- **data_format_example.py**: Example code showing data format conversions
- **Dockerfile**: Docker alternative (not used due to disk space)
- **README_DOCKER.md**: Docker instructions (archived)
- **HMM_INSTALLATION_ISSUES.md**: Original problem analysis
- **HMM_SETUP_GUIDE.md**: This file

---

## Data Format Requirements

### Critical: Column Naming Convention

HMM stride segmentation requires **specific column names** that differ from standard IMU data formats.

#### Required Column Names

The pre-trained HMM model expects gyroscope data with this naming:

| Required Column | Description | Anatomical Reference |
|----------------|-------------|---------------------|
| **gyr_ml** | Gyroscope medio-lateral | Side-to-side rotation (most important for gait) |
| gyr_pa | Gyroscope posterior-anterior | Forward-backward rotation (optional) |
| gyr_si | Gyroscope superior-inferior | Up-down rotation (optional) |

**Note**: The pre-trained model primarily uses `gyr_ml` (medio-lateral gyroscope).

#### Common Data Formats and How to Convert

##### Format 1: Standard XYZ Convention

If your data uses `gyr_x`, `gyr_y`, `gyr_z`:

```python
import pandas as pd

# Load your data
data = pd.read_csv('your_imu_data.csv')

# Map to gaitmap coordinate system
# This mapping depends on your sensor orientation!
# Example for foot-mounted sensor (typical orientation):
data_hmm = data.rename(columns={
    'gyr_x': 'gyr_si',   # X axis = superior-inferior
    'gyr_y': 'gyr_ml',   # Y axis = medio-lateral (CRITICAL for HMM)
    'gyr_z': 'gyr_pa'    # Z axis = posterior-anterior
})

# Or if you only need gyr_ml:
data_hmm = pd.DataFrame({
    'gyr_ml': data['gyr_y']  # Adjust based on your sensor orientation
})
```

##### Format 2: Multi-Level Column Index

If your data has multi-level columns like `(sensor_name, axis)`:

```python
# Example: columns = [('left_sensor', 'gyr_x'), ('left_sensor', 'gyr_y'), ...]
data = pd.read_csv('imu_data.csv', header=[0, 1])

# Flatten and rename
left_data = pd.DataFrame({
    'gyr_ml': data[('left_sensor', 'gyr_y')]  # Adjust axis based on orientation
})

right_data = pd.DataFrame({
    'gyr_ml': data[('right_sensor', 'gyr_y')]
})

# Create dictionary for HMM (if processing multiple sensors)
data_dict = {
    'left_sensor': left_data,
    'right_sensor': right_data
}
```

##### Format 3: Already in Gaitmap Format

If your data already has `gyr_ml`, `gyr_pa`, `gyr_si`:

```python
# No conversion needed!
data_hmm = data[['gyr_ml']]  # Or data[['gyr_ml', 'gyr_pa', 'gyr_si']]
```

### Complete Example: Data Preparation and HMM Segmentation

```python
import pandas as pd
from gaitmap.stride_segmentation.hmm import HmmStrideSegmentation
from gaitmap.stride_segmentation.hmm import PreTrainedRothSegmentationModel

# Step 1: Load your raw IMU data
raw_data = pd.read_csv('your_sensor_data.csv')

# Step 2: Convert to HMM-compatible format
# IMPORTANT: Adjust column mapping based on YOUR sensor orientation!
data_hmm = pd.DataFrame({
    'gyr_ml': raw_data['gyr_y']  # Example: Y-axis = medio-lateral
    # Add other axes if available:
    # 'gyr_pa': raw_data['gyr_z'],
    # 'gyr_si': raw_data['gyr_x'],
})

# Step 3: Initialize HMM with pre-trained model
model = PreTrainedRothSegmentationModel()
hmm_seg = HmmStrideSegmentation(model)

# Step 4: Segment strides
hmm_seg = hmm_seg.segment(data_hmm, sampling_rate_hz=204.8)  # Adjust sampling rate!

# Step 5: Get results
strides = hmm_seg.stride_list_

# Step 6: Analyze results
print(f"Detected {len(strides)} strides")
print(f"Stride start indices: {strides['start'].values}")
print(f"Stride end indices: {strides['end'].values}")

# Calculate stride durations (in seconds)
sampling_rate = 204.8  # Hz
stride_durations = (strides['end'] - strides['start']) / sampling_rate
print(f"Mean stride duration: {stride_durations.mean():.3f} seconds")
```

### Determining Your Sensor Orientation

To map your axes correctly, you need to know your sensor's orientation:

#### Method 1: Check Sensor Documentation

Look for:
- Sensor coordinate system diagram
- Axis definitions (which physical direction each axis represents)

#### Method 2: Analyze Data During Known Movements

```python
import matplotlib.pyplot as plt

# Plot gyroscope data during walking
fig, axes = plt.subplots(3, 1, figsize=(12, 8))

axes[0].plot(data['gyr_x'])
axes[0].set_ylabel('gyr_x')

axes[1].plot(data['gyr_y'])
axes[1].set_ylabel('gyr_y')

axes[2].plot(data['gyr_z'])
axes[2].set_ylabel('gyr_z')

plt.xlabel('Sample')
plt.suptitle('Gyroscope Data - Identify Medio-Lateral Axis')
plt.show()
```

**What to look for**:
- **Medio-lateral (gyr_ml)**: Shows regular oscillations during walking (foot rolling inward/outward)
- This is the axis you need for HMM!

#### Common Sensor Orientations

**Foot-mounted IMU (typical):**
```python
# Sensor on top of foot, facing forward
mapping = {
    'gyr_x': 'gyr_si',   # X points up (superior-inferior)
    'gyr_y': 'gyr_ml',   # Y points sideways (medio-lateral) ✓
    'gyr_z': 'gyr_pa'    # Z points forward (posterior-anterior)
}
```

**Ankle-mounted IMU:**
```python
# Sensor on lateral ankle
mapping = {
    'gyr_x': 'gyr_pa',   # X points forward
    'gyr_y': 'gyr_si',   # Y points up
    'gyr_z': 'gyr_ml'    # Z points sideways ✓
}
```

### Data Structure Requirements

#### Single Sensor

```python
# DataFrame with at least 'gyr_ml' column
data = pd.DataFrame({
    'gyr_ml': [0.1, 0.2, ...],  # Required
    # Optional additional axes:
    # 'gyr_pa': [...],
    # 'gyr_si': [...]
})
```

#### Multiple Sensors (Dictionary)

```python
# Dictionary with sensor names as keys
data_dict = {
    'left_sensor': pd.DataFrame({'gyr_ml': [...]}),
    'right_sensor': pd.DataFrame({'gyr_ml': [...]})
}

# Pass to HMM
hmm_seg = hmm_seg.segment(data_dict, sampling_rate_hz=204.8)
```

### Common Errors and Solutions

#### Error: `KeyError: "None of [Index(['gyr_ml'])] are in the [columns]"`

**Cause**: Your data doesn't have a column named `gyr_ml`

**Solution**: Rename your gyroscope column to `gyr_ml`:
```python
# Check your current columns
print(data.columns.tolist())

# Rename the appropriate column
data = data.rename(columns={'your_gyr_column': 'gyr_ml'})
```

#### Error: Multi-level column index issues

**Cause**: Your DataFrame has hierarchical columns

**Solution**: Flatten or select specific level:
```python
# Option 1: Flatten columns
data.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in data.columns]

# Option 2: Select single sensor
data_single = data['left_sensor']  # Now has simple column names
```

### Sampling Rate

HMM requires you to specify the sampling rate of your data:

```python
# Common IMU sampling rates:
sampling_rate_hz = 204.8   # Gaitmap example data
sampling_rate_hz = 100.0   # Common wearable sensors
sampling_rate_hz = 128.0   # Another common rate

hmm_seg = hmm_seg.segment(data, sampling_rate_hz=sampling_rate_hz)
```

**How to determine your sampling rate:**
1. Check sensor documentation
2. Check data file metadata
3. Calculate from timestamps: `rate = 1 / (timestamps[1] - timestamps[0])`

### Summary: Data Preparation Checklist

Before running HMM segmentation:

- [ ] Data is in pandas DataFrame format
- [ ] Column named `gyr_ml` exists (medio-lateral gyroscope)
- [ ] Column mapping matches your sensor orientation
- [ ] No multi-level column indices (or properly handled)
- [ ] Sampling rate is known and specified
- [ ] Data contains enough samples for at least one gait cycle (~1-2 seconds minimum)

### Practical Example Script

See **[data_format_example.py](data_format_example.py)** for working examples of all common data format conversions.

Run it to see examples:
```bash
conda activate hmm
python data_format_example.py
```

---

## Using HMM in This Project

### Quick Start

```bash
# Navigate to your project
cd ~/my-project2/HMM_Installing_dependencies

# Activate environment
source ~/miniforge3/bin/activate
conda activate hmm

# Your Python scripts now have access to HMM
python your_script.py

# Deactivate when done
conda deactivate
```

### Example Script

```python
#!/usr/bin/env python
"""Example HMM stride segmentation script."""

from gaitmap.stride_segmentation.hmm import HmmStrideSegmentation
from gaitmap.stride_segmentation.hmm import PreTrainedRothSegmentationModel
import pandas as pd

# Load your IMU data
# Data should be a DataFrame with proper axis naming (e.g., gyr_ml, acc_pa, etc.)
data = pd.read_csv('your_imu_data.csv')

# Initialize HMM with pre-trained model
model = PreTrainedRothSegmentationModel()
hmm_seg = HmmStrideSegmentation(model)

# Segment strides
hmm_seg = hmm_seg.segment(data, sampling_rate_hz=204.8)

# Get results
strides = hmm_seg.stride_list_

# Print results
for sensor, stride_df in strides.items():
    print(f"{sensor}: {len(stride_df)} strides detected")
```

### Running Jupyter Notebooks

```bash
# Activate environment
conda activate hmm

# Start Jupyter Lab
jupyter lab

# Or Jupyter Notebook
jupyter notebook
```

---

## Using HMM in Another Project

The HMM environment is **global** and can be used from **any project directory**.

### Method 1: Use Environment Directly

```bash
# From any project directory
cd ~/my-project2/my-other-hmm-project

# Activate HMM environment
source ~/miniforge3/bin/activate
conda activate hmm

# Run your scripts
python my_hmm_analysis.py

# Deactivate when done
conda deactivate
```

### Method 2: Create Project-Specific Scripts

Create a shell script in your new project:

**`run_hmm.sh`**:
```bash
#!/bin/bash
# Activate HMM environment and run script

source ~/miniforge3/bin/activate
conda activate hmm
python "$@"
conda deactivate
```

Make it executable:
```bash
chmod +x run_hmm.sh
```

Use it:
```bash
./run_hmm.sh my_analysis.py
```

### Method 3: Add Environment to IDE

#### VS Code

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type: "Python: Select Interpreter"
3. Choose: `~/miniforge3/envs/hmm/bin/python`

#### PyCharm

1. Settings → Project → Python Interpreter
2. Add Interpreter → Conda Environment
3. Select existing environment: `~/miniforge3/envs/hmm`

### Method 4: Create Symlink to Environment

```bash
# In your new project
cd ~/my-project2/my-new-hmm-project
ln -s ~/miniforge3/envs/hmm venv

# Activate like a regular venv
source venv/bin/activate
python your_script.py
deactivate
```

---

## Instructions for Claude (Future Sessions)

### When User Asks to Set Up HMM Environment

**If environment already exists** (check with `ls ~/miniforge3/envs/hmm`):

```bash
# Verify environment exists
ls ~/miniforge3/envs/hmm

# Activate and test
source ~/miniforge3/bin/activate
conda activate hmm
python -c "from gaitmap.stride_segmentation.hmm import HmmStrideSegmentation; print('HMM ready!')"
```

**If environment doesn't exist**, follow these steps:

#### Step 1: Check if Miniforge3 is installed

```bash
ls ~/miniforge3
```

If not installed:
```bash
cd ~
wget https://github.com/conda-forge/miniforge/releases/download/24.11.0-0/Miniforge3-24.11.0-0-Linux-x86_64.sh -O miniforge.sh
bash miniforge.sh -b -p $HOME/miniforge3
rm miniforge.sh
```

#### Step 2: Create environment from environment.yml

```bash
cd ~/my-project2/HMM_Installing_dependencies
~/miniforge3/bin/mamba env create -f environment.yml
```

**Expected time**: 5-10 minutes (downloads ~500MB of packages)

#### Step 3: Install gaitmap-mad (critical!)

```bash
~/miniforge3/envs/hmm/bin/pip install --no-deps gaitmap-mad==2.3.0
```

**Why this matters**: gaitmap requires gaitmap-mad as a companion package. The versions **must match exactly** or imports will fail.

#### Step 4: Verify installation

```bash
~/miniforge3/envs/hmm/bin/python smoke_test.py
```

**Expected output**:
```
✅ PASS: pomegranate 0.14.8 imported successfully
✅ PASS: gaitmap.stride_segmentation.hmm imported successfully
```

The third test (HMM Segmentation) may fail due to data format, but if the first two pass, **the environment is ready**.

### Quick Reference Environment File

If `environment.yml` is missing or corrupted, recreate it:

**`environment.yml`**:
```yaml
name: hmm
channels:
  - conda-forge
dependencies:
  # Core Python
  - python=3.9

  # Numerical computing (pinned for pomegranate compatibility)
  - numpy=1.23.*
  - cython=0.29.*

  # HMM dependencies
  - pomegranate=0.14.*

  # Scientific computing (conda-forge versions compatible with NumPy 1.23)
  - scipy>=1.9,<1.12
  - scikit-learn>=1.1,<1.4

  # Additional dependencies for pomegranate
  - networkx
  - pyyaml
  - joblib

  # Gait analysis (will be installed via pip as it's not in conda-forge)
  - pip

  # Development tools
  - jupyterlab
  - matplotlib
  - pandas

  # Pip-installed packages
  - pip:
      - gaitmap>=2.0,<2.5  # Pin to avoid lazy import issues in 2.5.x
```

### Common Issues and Fixes

#### Issue: "KeyError: '__path__'" when importing gaitmap HMM

**Cause**: Missing or mismatched gaitmap-mad version

**Fix**:
```bash
~/miniforge3/envs/hmm/bin/pip list | grep gaitmap
# Should show both gaitmap and gaitmap_mad with SAME version (e.g., 2.3.0)

# If missing or mismatched:
~/miniforge3/envs/hmm/bin/pip install --no-deps gaitmap-mad==2.3.0
```

#### Issue: Conda commands fail with "TOS not accepted"

**Cause**: Miniconda's default channels require Terms of Service acceptance

**Fix**: Use conda-forge only (which is why we use Miniforge3)

#### Issue: "No space left on device"

**Check disk space**:
```bash
df -h | grep -E '(Filesystem|/$)'
```

**If WSL is full**, clean conda cache:
```bash
~/miniforge3/bin/mamba clean --all -f -y
```

**If C: drive is full**, user needs to free space on Windows (environment is in WSL, not C:)

---

## Troubleshooting

### Verify Environment is Working

```bash
# Activate environment
source ~/miniforge3/bin/activate
conda activate hmm

# Test 1: Check Python version
python --version
# Expected: Python 3.9.23

# Test 2: Import pomegranate
python -c "import pomegranate; print(f'pomegranate {pomegranate.__version__}')"
# Expected: pomegranate 0.14.8

# Test 3: Import gaitmap HMM
python -c "from gaitmap.stride_segmentation.hmm import HmmStrideSegmentation; print('HMM module loaded!')"
# Expected: HMM module loaded!

# Test 4: Check versions match
python -c "import gaitmap; import gaitmap_mad; print(f'gaitmap: {gaitmap.__version__}'); print(f'gaitmap_mad: {gaitmap_mad.__version__}')"
# Expected: Both should be 2.3.0
```

### Reset Environment (if corrupted)

```bash
# Remove environment
~/miniforge3/bin/conda env remove -n hmm

# Recreate from environment.yml
cd ~/my-project2/HMM_Installing_dependencies
~/miniforge3/bin/mamba env create -f environment.yml

# Install gaitmap-mad
~/miniforge3/envs/hmm/bin/pip install --no-deps gaitmap-mad==2.3.0
```

### Export Environment (for backup)

```bash
# Export exact package list
conda activate hmm
conda env export > hmm_environment_backup.yml

# Or export with pip freeze
pip freeze > hmm_requirements.txt
```

### Check Disk Usage

```bash
# Check environment size
du -sh ~/miniforge3/envs/hmm

# Check total conda size
du -sh ~/miniforge3

# List all conda environments
conda env list
```

---

## Why This Setup is Different

### vs. pip install (doesn't work)

```bash
# ❌ This fails with Cython compilation errors
pip install pomegranate==0.14.8
```

**Problem**: No pre-built wheels, requires compiling from source, compilation fails

### vs. Docker (disk space issues)

```bash
# ❌ This works but requires 5-6 GB free on C: drive
docker build -t gaitmap-hmm .
```

**Problem**: Docker stores images on C: drive which was 99% full

### ✅ conda-forge solution

```bash
# ✅ This works! Prebuilt binaries, no compilation
mamba env create -f environment.yml
```

**Advantages**:
- Pre-built pomegranate binary from conda-forge
- No compilation needed
- Uses WSL disk space (910 GB free) not C: drive
- Reproducible environment
- Can be used from any project directory

---

## Summary

### What You Have Now

- ✅ Working HMM environment at `~/miniforge3/envs/hmm/`
- ✅ Pomegranate 0.14.8 (prebuilt from conda-forge)
- ✅ Gaitmap 2.3.0 + Gaitmap-MAD 2.3.0 (matching versions)
- ✅ Python 3.9, NumPy 1.23, all dependencies installed
- ✅ Can be used from any project directory
- ✅ 1.9 GB environment, plenty of disk space remaining (910 GB free)

### Quick Commands Reference

```bash
# Activate environment (from any directory)
source ~/miniforge3/bin/activate && conda activate hmm

# Deactivate
conda deactivate

# Run Python with HMM environment (one-liner)
~/miniforge3/envs/hmm/bin/python your_script.py

# Start Jupyter in HMM environment
conda activate hmm && jupyter lab

# Verify environment is working
~/miniforge3/envs/hmm/bin/python smoke_test.py

# Check installed versions
~/miniforge3/envs/hmm/bin/pip list | grep -E '(gaitmap|pomegranate)'
```

---

## For Future Reference

**Date Created**: 2025-10-27
**System**: Windows 10 Home + WSL2 (Ubuntu)
**Working Directory**: `/home/indigo/my-project2/HMM_Installing_dependencies/`
**Environment Path**: `~/miniforge3/envs/hmm/`
**Disk Usage**: 1.9 GB (environment), 47 GB total (WSL)

**Key Files**:
- `environment.yml` - Conda environment specification
- `smoke_test.py` - Verification script
- `HMM_SETUP_GUIDE.md` - This file

**Success Criteria**:
- ✅ Pomegranate 0.14.8 imports without warnings
- ✅ Gaitmap HMM module imports successfully
- ✅ HmmStrideSegmentation and PreTrainedRothSegmentationModel available
- ✅ No compilation errors
- ✅ No NumPy ABI warnings

---

**Need Help?**

- Check [HMM_INSTALLATION_ISSUES.md](HMM_INSTALLATION_ISSUES.md) for background on the problems
- Run `smoke_test.py` to verify environment
- See Troubleshooting section above
- Review conda-forge documentation: https://conda-forge.org/docs/
