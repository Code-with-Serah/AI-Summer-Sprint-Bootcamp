#!/usr/bin/env python3
"""
Test script to verify blink detection functionality
"""

import sys
import numpy as np
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.eye_tracker import EyeTracker

def test_eye_aspect_ratio():
    """Test EAR calculation with sample eye landmarks."""
    print("Testing Eye Aspect Ratio (EAR) calculation...")
    
    eye_tracker = EyeTracker()
    
    # Create sample eye landmarks for testing
    # 6-point eye model: [outer_corner, top_1, top_2, inner_corner, bottom_2, bottom_1]
    
    # Open eye (normal state) - EAR should be around 0.25-0.3
    open_eye = np.array([
        [100, 150],  # outer_corner
        [110, 140],  # top_1
        [120, 138],  # top_2
        [130, 150],  # inner_corner
        [120, 162],  # bottom_2
        [110, 160]   # bottom_1
    ])
    
    # Closed eye (blink state) - EAR should be close to 0
    closed_eye = np.array([
        [100, 150],  # outer_corner
        [110, 150],  # top_1 (same level as corner)
        [120, 150],  # top_2 (same level as corner)
        [130, 150],  # inner_corner
        [120, 150],  # bottom_2 (same level as corner)
        [110, 150]   # bottom_1 (same level as corner)
    ])
    
    # Test open eye
    open_ear = eye_tracker.calculate_ear(open_eye)
    print(f"Open eye EAR: {open_ear:.3f}")
    
    # Test closed eye
    closed_ear = eye_tracker.calculate_ear(closed_eye)
    print(f"Closed eye EAR: {closed_ear:.3f}")
    
    # Test with empty array
    empty_ear = eye_tracker.calculate_ear(np.array([]))
    print(f"Empty array EAR: {empty_ear:.3f}")
    
    print(f"EAR threshold: {eye_tracker.ear_threshold:.3f}")
    print()
    
    return open_ear, closed_ear

def test_blink_detection():
    """Test blink detection process."""
    print("Testing blink detection process...")
    
    eye_tracker = EyeTracker()
    
    # Create sample eye landmarks
    open_eye_left = np.array([
        [100, 150], [110, 140], [120, 138], [130, 150], [120, 162], [110, 160]
    ])
    open_eye_right = np.array([
        [200, 150], [210, 140], [220, 138], [230, 150], [220, 162], [210, 160]
    ])
    
    closed_eye_left = np.array([
        [100, 150], [110, 150], [120, 150], [130, 150], [120, 150], [110, 150]
    ])
    closed_eye_right = np.array([
        [200, 150], [210, 150], [220, 150], [230, 150], [220, 150], [210, 150]
    ])
    
    # Test sequence: open -> blink -> open
    eye_sequences = [
        # Open eyes
        {'left_eye': open_eye_left, 'right_eye': open_eye_right},
        {'left_eye': open_eye_left, 'right_eye': open_eye_right},
        {'left_eye': open_eye_left, 'right_eye': open_eye_right},
        # Start blink
        {'left_eye': closed_eye_left, 'right_eye': closed_eye_right},
        {'left_eye': closed_eye_left, 'right_eye': closed_eye_right},
        {'left_eye': closed_eye_left, 'right_eye': closed_eye_right},
        {'left_eye': closed_eye_left, 'right_eye': closed_eye_right},
        # End blink
        {'left_eye': open_eye_left, 'right_eye': open_eye_right},
        {'left_eye': open_eye_left, 'right_eye': open_eye_right},
    ]
    
    print("Processing eye sequence...")
    for i, eye_landmarks in enumerate(eye_sequences):
        result = eye_tracker.process_eyes(eye_landmarks)
        
        print(f"Frame {i+1}: EAR={result['avg_ear']:.3f}, "
              f"Blinking={result['is_blinking']}, "
              f"Blink Detected={result['blink_detected']}, "
              f"Total Blinks={result['total_blinks']}")
    
    # Display final statistics
    print("\nFinal Statistics:")
    stats = eye_tracker.get_blink_statistics()
    print(f"Total blink count: {stats['blink_count']}")
    print(f"Blink rate: {stats['blink_rate']:.1f} blinks/min")
    if stats['avg_duration'] > 0:
        print(f"Average blink duration: {stats['avg_duration']:.3f} seconds")
    
    stress_metrics = eye_tracker.stress_metrics
    print(f"Current stress metrics: {stress_metrics}")

def main():
    """Main test function."""
    print("=" * 50)
    print("BLINK DETECTION TEST")
    print("=" * 50)
    
    try:
        # Test EAR calculation
        open_ear, closed_ear = test_eye_aspect_ratio()
        
        # Verify EAR values are reasonable
        if open_ear > 0.2 and closed_ear < 0.1:
            print("✓ EAR calculation appears to be working correctly")
        else:
            print("✗ EAR calculation may have issues")
        
        print("-" * 50)
        
        # Test blink detection
        test_blink_detection()
        
        print("-" * 50)
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
