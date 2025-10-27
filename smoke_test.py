#!/usr/bin/env python3
"""
Smoke test for HMM stride segmentation environment.

This script verifies that:
1. pomegranate imports without ABI warnings
2. gaitmap.stride_segmentation.hmm imports cleanly
3. Basic HMM stride segmentation works on example data

Pass/Fail Criteria:
✅ PASS: All imports succeed and stride segmentation returns results
❌ FAIL: ImportError, ABI warnings, or segmentation fails
"""

import sys
import warnings

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_pomegranate_import():
    """Test pomegranate import and check for ABI warnings."""
    print_section("Test 1: Pomegranate Import")

    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import pomegranate

            if w:
                print("❌ FAIL: Warnings detected during pomegranate import:")
                for warning in w:
                    print(f"   {warning.category.__name__}: {warning.message}")
                return False

            print(f"✅ PASS: pomegranate {pomegranate.__version__} imported successfully")
            print(f"   No ABI warnings detected")
            return True

    except ImportError as e:
        print(f"❌ FAIL: Could not import pomegranate")
        print(f"   Error: {e}")
        return False

def test_gaitmap_hmm_import():
    """Test gaitmap HMM module import."""
    print_section("Test 2: Gaitmap HMM Import")

    try:
        from gaitmap.stride_segmentation.hmm import HmmStrideSegmentation
        from gaitmap.stride_segmentation.hmm import PreTrainedRothSegmentationModel

        print("✅ PASS: gaitmap.stride_segmentation.hmm imported successfully")
        print("   HmmStrideSegmentation: available")
        print("   PreTrainedRothSegmentationModel: available")
        return True

    except ImportError as e:
        print(f"❌ FAIL: Could not import gaitmap HMM module")
        print(f"   Error: {e}")
        return False

def test_hmm_segmentation():
    """Test basic HMM stride segmentation on example data."""
    print_section("Test 3: HMM Stride Segmentation")

    try:
        from gaitmap.stride_segmentation.hmm import HmmStrideSegmentation
        from gaitmap.stride_segmentation.hmm import PreTrainedRothSegmentationModel
        from gaitmap.example_data import get_healthy_example_imu_data

        # Load example data
        print("Loading example IMU data...")
        data = get_healthy_example_imu_data()
        print(f"   Loaded data for sensors: {list(data.keys())}")

        # Initialize HMM model
        print("Initializing pre-trained HMM model...")
        model = PreTrainedRothSegmentationModel()
        hmm_seg = HmmStrideSegmentation(model)

        # Perform segmentation
        print("Running HMM stride segmentation...")
        hmm_seg = hmm_seg.segment(data, sampling_rate_hz=204.8)
        strides = hmm_seg.stride_list_

        # Check results
        print("\n✅ PASS: HMM stride segmentation completed successfully")
        print("\nResults:")
        for sensor_name, stride_df in strides.items():
            num_strides = len(stride_df)
            if num_strides > 0:
                mean_duration = (stride_df['end'] - stride_df['start']).mean() / 204.8
                print(f"   {sensor_name}: {num_strides} strides detected")
                print(f"      Mean stride duration: {mean_duration:.3f} seconds")
            else:
                print(f"   {sensor_name}: No strides detected")

        return True

    except Exception as e:
        print(f"❌ FAIL: HMM stride segmentation failed")
        print(f"   Error: {type(e).__name__}: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return False

def main():
    """Run all smoke tests."""
    print("\n" + "="*60)
    print("  HMM Environment Smoke Test")
    print("="*60)

    # Run tests
    results = []
    results.append(("Pomegranate Import", test_pomegranate_import()))
    results.append(("Gaitmap HMM Import", test_gaitmap_hmm_import()))

    # Only run segmentation test if imports succeeded
    if all(r[1] for r in results):
        results.append(("HMM Segmentation", test_hmm_segmentation()))
    else:
        print_section("Test 3: HMM Stride Segmentation")
        print("⏭️  SKIPPED: Previous tests failed")
        results.append(("HMM Segmentation", False))

    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Environment is ready for HMM stride segmentation.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
