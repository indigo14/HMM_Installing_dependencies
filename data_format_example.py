#!/usr/bin/env python
"""
Example script showing how to convert common IMU data formats to HMM-compatible format.

This demonstrates the most common data format conversions for gaitmap HMM stride segmentation.
"""

import pandas as pd
import numpy as np

# ==============================================================================
# Example 1: Standard XYZ format (most common)
# ==============================================================================

print("="*60)
print("Example 1: Converting XYZ format to gyr_ml")
print("="*60)

# Your typical IMU data with xyz columns
raw_data_xyz = pd.DataFrame({
    'timestamp': np.arange(0, 10, 0.01),
    'gyr_x': np.random.randn(1000),
    'gyr_y': np.random.randn(1000),  # This is typically medio-lateral
    'gyr_z': np.random.randn(1000),
    'acc_x': np.random.randn(1000),
    'acc_y': np.random.randn(1000),
    'acc_z': np.random.randn(1000),
})

print("\nOriginal columns:", raw_data_xyz.columns.tolist())

# Convert for HMM (assuming typical foot-mounted sensor)
hmm_data_1 = pd.DataFrame({
    'gyr_ml': raw_data_xyz['gyr_y']  # Y-axis is medio-lateral
})

print("HMM-compatible columns:", hmm_data_1.columns.tolist())
print("✓ Ready for HMM segmentation")

# ==============================================================================
# Example 2: Multi-level columns (sensor_name, axis)
# ==============================================================================

print("\n" + "="*60)
print("Example 2: Converting multi-level columns")
print("="*60)

# Data with hierarchical columns (common in gaitmap example data)
columns_multilevel = pd.MultiIndex.from_tuples([
    ('left_sensor', 'gyr_x'),
    ('left_sensor', 'gyr_y'),
    ('left_sensor', 'gyr_z'),
    ('right_sensor', 'gyr_x'),
    ('right_sensor', 'gyr_y'),
    ('right_sensor', 'gyr_z'),
])

raw_data_multilevel = pd.DataFrame(
    np.random.randn(1000, 6),
    columns=columns_multilevel
)

print("\nOriginal columns (multi-level):")
print(raw_data_multilevel.columns.tolist()[:3], "...")

# Convert to HMM format (dictionary with one DataFrame per sensor)
hmm_data_2 = {
    'left_sensor': pd.DataFrame({
        'gyr_ml': raw_data_multilevel[('left_sensor', 'gyr_y')]
    }),
    'right_sensor': pd.DataFrame({
        'gyr_ml': raw_data_multilevel[('right_sensor', 'gyr_y')]
    })
}

print("\nHMM-compatible structure:")
print(f"  Dictionary with {len(hmm_data_2)} sensors")
for sensor_name, sensor_data in hmm_data_2.items():
    print(f"  - {sensor_name}: {sensor_data.columns.tolist()}")
print("✓ Ready for HMM segmentation")

# ==============================================================================
# Example 3: Data already in correct format
# ==============================================================================

print("\n" + "="*60)
print("Example 3: Data already has gyr_ml")
print("="*60)

raw_data_correct = pd.DataFrame({
    'gyr_ml': np.random.randn(1000),
    'gyr_pa': np.random.randn(1000),
    'gyr_si': np.random.randn(1000),
})

print("\nOriginal columns:", raw_data_correct.columns.tolist())
print("✓ Already in correct format! No conversion needed.")

# ==============================================================================
# Example 4: Complete workflow with actual HMM (if environment is active)
# ==============================================================================

print("\n" + "="*60)
print("Example 4: Complete HMM workflow")
print("="*60)

try:
    from gaitmap.stride_segmentation.hmm import HmmStrideSegmentation
    from gaitmap.stride_segmentation.hmm import PreTrainedRothSegmentationModel

    print("\n✓ HMM modules available")

    # Create synthetic walking data (simplified)
    # In reality, this would be your actual sensor data
    synthetic_data = pd.DataFrame({
        'gyr_ml': np.sin(np.linspace(0, 10*np.pi, 2000)) + np.random.randn(2000) * 0.1
    })

    print("✓ Prepared synthetic data with gyr_ml column")

    # Initialize HMM
    model = PreTrainedRothSegmentationModel()
    hmm_seg = HmmStrideSegmentation(model)
    print("✓ HMM model initialized")

    # Run segmentation
    # Note: This may fail on synthetic data, but shows the workflow
    print("\nAttempting stride segmentation...")
    print("(Note: May fail on synthetic data - use real gait data)")

    try:
        hmm_seg = hmm_seg.segment(synthetic_data, sampling_rate_hz=100.0)
        strides = hmm_seg.stride_list_
        print(f"✓ Detected {len(strides)} strides")
    except Exception as e:
        print(f"✗ Segmentation failed (expected with synthetic data): {type(e).__name__}")

except ImportError as e:
    print(f"\n✗ HMM modules not available: {e}")
    print("  This is normal if not running in the HMM environment")
    print("  To run HMM: conda activate hmm")

# ==============================================================================
# Summary
# ==============================================================================

print("\n" + "="*60)
print("SUMMARY: Data Conversion Quick Reference")
print("="*60)

print("""
Most common conversion (foot-mounted sensor):
    data_hmm = pd.DataFrame({'gyr_ml': raw_data['gyr_y']})

For multi-level columns:
    data_hmm = {'sensor_name': pd.DataFrame({'gyr_ml': data[('sensor_name', 'gyr_y')]})}

Already correct format:
    data_hmm = data[['gyr_ml']]  # Use as-is

Key requirement:
    ✓ Must have column named 'gyr_ml' (medio-lateral gyroscope)
    ✓ DataFrame format (or dict of DataFrames for multiple sensors)
    ✓ Know your sampling rate

Then run HMM:
    from gaitmap.stride_segmentation.hmm import HmmStrideSegmentation, PreTrainedRothSegmentationModel
    model = PreTrainedRothSegmentationModel()
    hmm_seg = HmmStrideSegmentation(model)
    hmm_seg = hmm_seg.segment(data_hmm, sampling_rate_hz=YOUR_RATE)
    strides = hmm_seg.stride_list_
""")

print("="*60)
