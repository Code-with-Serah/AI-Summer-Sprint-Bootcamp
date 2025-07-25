#!/usr/bin/env python3
"""
Test script for facial expression analysis functionality.
"""

import sys
import cv2
import numpy as np
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.face_detector import FaceDetector
from src.core.facial_expression_analyzer import FacialExpressionAnalyzer

def test_expression_analysis():
    """Test facial expression analysis with webcam input."""
    
    # Initialize components
    face_detector = FaceDetector()
    expression_analyzer = FacialExpressionAnalyzer()
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Starting facial expression analysis test...")
    print("Press 'q' to quit, 'r' to reset")
    
    try:
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect faces
            detection_result = face_detector.detect_faces(frame)
            
            if detection_result['faces_detected']:
                landmarks = detection_result['landmarks']
                
                # Analyze expression
                expression_result = expression_analyzer.analyze_expression(landmarks)
                
                # Draw landmarks
                frame_with_landmarks = face_detector.draw_landmarks(frame, landmarks)
                
                # Display expression information
                expression = expression_result.get('expression', 'unknown')
                confidence = expression_result.get('confidence', 0.0)
                
                cv2.putText(frame_with_landmarks, f"Expression: {expression}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame_with_landmarks, f"Confidence: {confidence:.2f}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Display number of faces detected
                cv2.putText(frame_with_landmarks, f"Faces: {detection_result['num_faces']}", 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                cv2.imshow('Facial Expression Analysis', frame_with_landmarks)
            else:
                # No face detected
                cv2.putText(frame, "No face detected", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow('Facial Expression Analysis', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                print("Resetting...")
                # Add reset functionality if needed
                
    except KeyboardInterrupt:
        print("\nStopping...")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("Test completed.")

if __name__ == "__main__":
    test_expression_analysis()
