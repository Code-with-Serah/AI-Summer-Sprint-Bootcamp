"""
Face Detection and Tracking Module
Implements real-time face detection and landmark tracking using MediaPipe.
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import List, Tuple, Optional, Dict, Any
import logging

class FaceDetector:
    """
    Face detection and landmark tracking using MediaPipe Face Mesh.
    Provides robust face detection and precise facial landmark coordinates.
    """
    
    def __init__(self, 
                 max_num_faces: int = 1, 
                 refine_landmarks: bool = True,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Initialize the face detector.
        
        Args:
            max_num_faces: Maximum number of faces to detect
            refine_landmarks: Whether to refine eye and lip landmarks
            min_detection_confidence: Minimum confidence for face detection
            min_tracking_confidence: Minimum confidence for face tracking
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Face detection state
        self.is_face_detected = False
        self.face_landmarks = None
        self.face_bbox = None
        
        # Define key facial landmarks indices (MediaPipe Face Mesh)
        # Using 6-point eye model for EAR calculation: [outer_corner, top_1, top_2, inner_corner, bottom_2, bottom_1]
        self.EYE_LANDMARKS = {
            'left_eye': [33, 160, 158, 133, 153, 144],   # Left eye 6-point model
            'right_eye': [362, 385, 387, 263, 373, 380], # Right eye 6-point model
            'left_eyebrow': [46, 53, 52, 51, 48, 115, 131, 134, 102, 49, 220, 305],
            'right_eyebrow': [276, 283, 282, 281, 278, 344, 360, 363, 331, 279, 440, 75]
        }
        
        self.MOUTH_LANDMARKS = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
        
        self.JAW_LANDMARKS = [172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323]
        
        self.logger.info("FaceDetector initialized successfully")
    
    def detect_faces(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Detect faces and extract landmarks from the input frame.
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            Dictionary containing detection results and landmarks
        """
        if frame is None or frame.size == 0:
            return self._empty_result()
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.face_mesh.process(rgb_frame)
        
        # Extract results
        detection_result = {
            'faces_detected': False,
            'num_faces': 0,
            'landmarks': None,
            'bbox': None,
            'confidence': 0.0
        }
        
        if results.multi_face_landmarks:
            detection_result['faces_detected'] = True
            detection_result['num_faces'] = len(results.multi_face_landmarks)
            
            # Get the first face (assuming single face detection)
            face_landmarks = results.multi_face_landmarks[0]
            
            # Convert landmarks to pixel coordinates
            h, w = frame.shape[:2]
            landmarks_px = []
            
            for landmark in face_landmarks.landmark:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                landmarks_px.append([x, y])
            
            detection_result['landmarks'] = np.array(landmarks_px)
            detection_result['bbox'] = self._calculate_face_bbox(landmarks_px)
            detection_result['confidence'] = 1.0  # MediaPipe doesn't provide explicit confidence
            
            # Update internal state
            self.is_face_detected = True
            self.face_landmarks = detection_result['landmarks']
            self.face_bbox = detection_result['bbox']
        else:
            self.is_face_detected = False
            self.face_landmarks = None
            self.face_bbox = None
        
        return detection_result
    
    def get_eye_landmarks(self, landmarks: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract eye landmarks from face landmarks.
        
        Args:
            landmarks: Complete face landmarks array
            
        Returns:
            Dictionary with left and right eye landmarks
        """
        if landmarks is None:
            return {'left_eye': None, 'right_eye': None}
        
        left_eye_points = landmarks[self.EYE_LANDMARKS['left_eye']]
        right_eye_points = landmarks[self.EYE_LANDMARKS['right_eye']]
        
        return {
            'left_eye': left_eye_points,
            'right_eye': right_eye_points
        }
    
    def get_eyebrow_landmarks(self, landmarks: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract eyebrow landmarks from face landmarks.
        
        Args:
            landmarks: Complete face landmarks array
            
        Returns:
            Dictionary with left and right eyebrow landmarks
        """
        if landmarks is None:
            return {'left_eyebrow': None, 'right_eyebrow': None}
        
        left_eyebrow_points = landmarks[self.EYE_LANDMARKS['left_eyebrow']]
        right_eyebrow_points = landmarks[self.EYE_LANDMARKS['right_eyebrow']]
        
        return {
            'left_eyebrow': left_eyebrow_points,
            'right_eyebrow': right_eyebrow_points
        }
    
    def get_mouth_landmarks(self, landmarks: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract mouth landmarks from face landmarks.
        
        Args:
            landmarks: Complete face landmarks array
            
        Returns:
            Mouth landmarks array or None
        """
        if landmarks is None:
            return None
        
        return landmarks[self.MOUTH_LANDMARKS]
    
    def get_jaw_landmarks(self, landmarks: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract jaw landmarks from face landmarks.
        
        Args:
            landmarks: Complete face landmarks array
            
        Returns:
            Jaw landmarks array or None
        """
        if landmarks is None:
            return None
        
        return landmarks[self.JAW_LANDMARKS]
    
    def draw_landmarks(self, frame: np.ndarray, landmarks: np.ndarray, 
                      draw_eyes: bool = True, draw_eyebrows: bool = True,
                      draw_mouth: bool = True, draw_jaw: bool = False) -> np.ndarray:
        """
        Draw facial landmarks on the frame.
        
        Args:
            frame: Input frame to draw on
            landmarks: Face landmarks array
            draw_eyes: Whether to draw eye landmarks
            draw_eyebrows: Whether to draw eyebrow landmarks
            draw_mouth: Whether to draw mouth landmarks
            draw_jaw: Whether to draw jaw landmarks
            
        Returns:
            Frame with drawn landmarks
        """
        if landmarks is None:
            return frame
        
        output_frame = frame.copy()
        
        # Draw eyes
        if draw_eyes:
            eye_landmarks = self.get_eye_landmarks(landmarks)
            if eye_landmarks['left_eye'] is not None:
                self._draw_points(output_frame, eye_landmarks['left_eye'], (0, 255, 0))
            if eye_landmarks['right_eye'] is not None:
                self._draw_points(output_frame, eye_landmarks['right_eye'], (0, 255, 0))
        
        # Draw eyebrows
        if draw_eyebrows:
            eyebrow_landmarks = self.get_eyebrow_landmarks(landmarks)
            if eyebrow_landmarks['left_eyebrow'] is not None:
                self._draw_points(output_frame, eyebrow_landmarks['left_eyebrow'], (255, 0, 0))
            if eyebrow_landmarks['right_eyebrow'] is not None:
                self._draw_points(output_frame, eyebrow_landmarks['right_eyebrow'], (255, 0, 0))
        
        # Draw mouth
        if draw_mouth:
            mouth_landmarks = self.get_mouth_landmarks(landmarks)
            if mouth_landmarks is not None:
                self._draw_points(output_frame, mouth_landmarks, (0, 0, 255))
        
        # Draw jaw
        if draw_jaw:
            jaw_landmarks = self.get_jaw_landmarks(landmarks)
            if jaw_landmarks is not None:
                self._draw_points(output_frame, jaw_landmarks, (255, 255, 0))
        
        return output_frame
    
    def _calculate_face_bbox(self, landmarks: List[List[int]]) -> Tuple[int, int, int, int]:
        """Calculate bounding box for face landmarks."""
        if not landmarks:
            return (0, 0, 0, 0)
        
        landmarks_array = np.array(landmarks)
        x_min = np.min(landmarks_array[:, 0])
        y_min = np.min(landmarks_array[:, 1])
        x_max = np.max(landmarks_array[:, 0])
        y_max = np.max(landmarks_array[:, 1])
        
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    
    def _draw_points(self, frame: np.ndarray, points: np.ndarray, color: Tuple[int, int, int]):
        """Draw points on the frame."""
        for point in points:
            cv2.circle(frame, tuple(point), 2, color, -1)
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty detection result."""
        return {
            'faces_detected': False,
            'num_faces': 0,
            'landmarks': None,
            'bbox': None,
            'confidence': 0.0
        }
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'face_mesh') and self.face_mesh:
            self.face_mesh.close()
