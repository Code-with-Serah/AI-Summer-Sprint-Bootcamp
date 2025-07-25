#!/usr/bin/env python3
"""
Simple test script to verify face detection and eye tracking functionality.
This script will open your webcam and display real-time face detection with eye tracking.
"""

import cv2
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.face_detector import FaceDetector
from src.core.eye_tracker import EyeTracker

def main():
    """Test face detection and eye tracking with webcam."""
    print("Starting Face Detection and Eye Tracking Test...")
    print("Press 'q' to quit, 'r' to reset metrics")
    
    # Initialize components
    try:
        face_detector = FaceDetector()
        eye_tracker = EyeTracker()
        print("✓ Components initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing components: {e}")
        return
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("✗ Error: Could not open webcam")
        return
    
    print("✓ Webcam opened successfully")
    print("\n=== CONTROLS ===")
    print("q - Quit application")
    print("r - Reset eye tracking metrics")
    print("c - Calibrate EAR threshold")
    print("================\n")
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("✗ Error: Could not read frame from webcam")
                break
            
            frame_count += 1
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect faces
            face_results = face_detector.detect_faces(frame)
            
            # Process eyes if face is detected
            if face_results['faces_detected']:
                landmarks = face_results['landmarks']
                
                # Get eye landmarks
                eye_landmarks = face_detector.get_eye_landmarks(landmarks)
                
                # Process eye tracking
                eye_results = eye_tracker.process_eyes(eye_landmarks)
                
                # Draw face landmarks
                frame = face_detector.draw_landmarks(
                    frame, landmarks, 
                    draw_eyes=True, 
                    draw_eyebrows=True, 
                    draw_mouth=True
                )
                
                # Draw eye tracking info
                frame = eye_tracker.draw_eye_tracking_info(
                    frame, eye_landmarks, eye_results
                )
                
                # Draw face bounding box
                bbox = face_results['bbox']
                if bbox:
                    x, y, w, h = bbox
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(frame, "Face Detected", (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            
            else:
                # No face detected
                cv2.putText(frame, "No Face Detected", (50, 50), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Draw frame counter
            cv2.putText(frame, f"Frame: {frame_count}", (10, frame.shape[0] - 10), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Display the frame
            cv2.imshow('Stress Detection - Face & Eye Tracking Test', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                eye_tracker.reset_metrics()
                print("Eye tracking metrics reset")
            elif key == ord('c'):
                new_threshold = eye_tracker.calibrate_threshold()
                eye_tracker.ear_threshold = new_threshold
                print(f"EAR threshold calibrated to: {new_threshold:.3f}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"✗ Error during processing: {e}")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("✓ Cleanup completed")
        
        # Print final statistics
        if 'eye_tracker' in locals():
            stats = eye_tracker.get_blink_statistics()
            print("\n=== SESSION STATISTICS ===")
            print(f"Total blinks: {eye_tracker.total_blinks}")
            print(f"Blink rate: {stats['blink_rate']:.1f} blinks/min")
            print(f"Average blink duration: {stats['avg_duration']:.3f}s")
            print(f"Rapid blinks: {stats['rapid_blinks']}")
            print(f"Prolonged blinks: {stats['prolonged_blinks']}")
            print("=========================")

if __name__ == "__main__":
    main()
