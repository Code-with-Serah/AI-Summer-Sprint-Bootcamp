"""
Eye Tracking and Blink Detection Module
Implements eye tracking, blink detection, and eye movement analysis using EAR (Eye Aspect Ratio).
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from collections import deque
import time

class EyeTracker:
    """
    Eye tracking and blink detection using Eye Aspect Ratio (EAR) method.
    Tracks eye movements, blink frequency, and eye closure duration for stress analysis.
    """
    
    def __init__(self, 
                 ear_threshold: float = 0.25,
                 blink_frames_threshold: int = 3,
                 history_size: int = 30):
        """
        Initialize the eye tracker.
        
        Args:
            ear_threshold: Eye Aspect Ratio threshold for blink detection
            blink_frames_threshold: Minimum consecutive frames for blink detection
            history_size: Size of the rolling window for metrics calculation
        """
        self.logger = logging.getLogger(__name__)
        
        # Blink detection parameters
        self.ear_threshold = ear_threshold
        self.blink_frames_threshold = blink_frames_threshold
        
        # Data storage for analysis
        self.history_size = history_size
        self.ear_history = deque(maxlen=history_size)
        self.blink_history = deque(maxlen=100)  # Store last 100 blinks
        
        # Blink detection state
        self.consecutive_frames_below_threshold = 0
        self.is_blinking = False
        self.blink_start_time = None
        self.total_blinks = 0
        
        # Eye movement tracking
        self.eye_center_history = deque(maxlen=history_size)
        self.eye_movement_threshold = 5.0  # pixels
        
        # Stress indicators
        self.stress_metrics = {
            'blink_rate': 0.0,
            'avg_blink_duration': 0.0,
            'eye_closure_ratio': 0.0,
            'eye_movement_intensity': 0.0,
            'rapid_blinks': 0,
            'prolonged_closures': 0
        }
        
        self.logger.info("EyeTracker initialized successfully")
    
    def calculate_ear(self, eye_landmarks: np.ndarray) -> float:
        """
        Calculate Eye Aspect Ratio (EAR) for given eye landmarks.
        
        EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
        
        Args:
            eye_landmarks: Array of eye landmark points
            
        Returns:
            Eye Aspect Ratio value
        """
        if eye_landmarks is None or len(eye_landmarks) < 6:
            return 0.0
        
        # Calculate euclidean distances
        # Vertical distances
        vertical_1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        vertical_2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Horizontal distance
        horizontal = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        # Calculate EAR
        if horizontal == 0:
            return 0.0
        
        ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
        return ear
    
    def process_eyes(self, eye_landmarks: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Process eye landmarks to detect blinks and calculate metrics.
        
        Args:
            eye_landmarks: Dictionary containing left and right eye landmarks
            
        Returns:
            Dictionary with eye tracking results and metrics
        """
        current_time = time.time()
        
        # Calculate EAR for both eyes
        left_ear = 0.0
        right_ear = 0.0
        
        if eye_landmarks.get('left_eye') is not None:
            left_ear = self.calculate_ear(eye_landmarks['left_eye'])
        
        if eye_landmarks.get('right_eye') is not None:
            right_ear = self.calculate_ear(eye_landmarks['right_eye'])
        
        # Average EAR
        avg_ear = (left_ear + right_ear) / 2.0 if (left_ear > 0 and right_ear > 0) else max(left_ear, right_ear)
        
        # Store EAR history
        self.ear_history.append(avg_ear)
        
        # Detect blinks
        blink_detected = self._detect_blink(avg_ear, current_time)
        
        # Calculate eye center for movement tracking
        eye_center = self._calculate_eye_center(eye_landmarks)
        if eye_center is not None:
            self.eye_center_history.append(eye_center)
        
        # Update stress metrics
        self._update_stress_metrics(current_time)
        
        return {
            'left_ear': left_ear,
            'right_ear': right_ear,
            'avg_ear': avg_ear,
            'blink_detected': blink_detected,
            'is_blinking': self.is_blinking,
            'total_blinks': self.total_blinks,
            'eye_center': eye_center,
            'stress_metrics': self.stress_metrics.copy()
        }
    
    def _detect_blink(self, ear: float, current_time: float) -> bool:
        """
        Detect blink based on EAR threshold and frame consistency.
        
        Args:
            ear: Current Eye Aspect Ratio
            current_time: Current timestamp
            
        Returns:
            True if blink is detected, False otherwise
        """
        blink_detected = False
        
        if ear < self.ear_threshold:
            self.consecutive_frames_below_threshold += 1
            
            if not self.is_blinking and self.consecutive_frames_below_threshold >= self.blink_frames_threshold:
                # Start of blink
                self.is_blinking = True
                self.blink_start_time = current_time
                
        else:
            if self.is_blinking and self.consecutive_frames_below_threshold >= self.blink_frames_threshold:
                # End of blink
                blink_duration = current_time - self.blink_start_time if self.blink_start_time else 0
                
                # Record blink
                self.blink_history.append({
                    'timestamp': current_time,
                    'duration': blink_duration,
                    'min_ear': min(self.ear_history) if self.ear_history else 0
                })
                
                self.total_blinks += 1
                blink_detected = True
                
                # Check for rapid or prolonged blinks (stress indicators)
                if blink_duration < 0.1:  # Very fast blink
                    self.stress_metrics['rapid_blinks'] += 1
                elif blink_duration > 0.5:  # Prolonged closure
                    self.stress_metrics['prolonged_closures'] += 1
            
            # Reset blink state
            self.is_blinking = False
            self.consecutive_frames_below_threshold = 0
            self.blink_start_time = None
        
        return blink_detected
    
    def _calculate_eye_center(self, eye_landmarks: Dict[str, np.ndarray]) -> Optional[Tuple[float, float]]:
        """
        Calculate the center point of both eyes for movement tracking.
        
        Args:
            eye_landmarks: Dictionary containing left and right eye landmarks
            
        Returns:
            Tuple of (x, y) coordinates of eye center or None
        """
        centers = []
        
        for eye_key in ['left_eye', 'right_eye']:
            if eye_landmarks.get(eye_key) is not None:
                eye_points = eye_landmarks[eye_key]
                center_x = np.mean(eye_points[:, 0])
                center_y = np.mean(eye_points[:, 1])
                centers.append([center_x, center_y])
        
        if centers:
            overall_center = np.mean(centers, axis=0)
            return tuple(overall_center)
        
        return None
    
    def _update_stress_metrics(self, current_time: float):
        """
        Update stress-related metrics based on eye tracking data.
        
        Args:
            current_time: Current timestamp
        """
        # Calculate blink rate (blinks per minute)
        recent_blinks = [b for b in self.blink_history if current_time - b['timestamp'] <= 60]
        self.stress_metrics['blink_rate'] = len(recent_blinks)
        
        # Calculate average blink duration
        if recent_blinks:
            self.stress_metrics['avg_blink_duration'] = np.mean([b['duration'] for b in recent_blinks])
        
        # Calculate eye closure ratio (time spent with eyes closed)
        if self.ear_history:
            closed_frames = sum(1 for ear in self.ear_history if ear < self.ear_threshold)
            self.stress_metrics['eye_closure_ratio'] = closed_frames / len(self.ear_history)
        
        # Calculate eye movement intensity
        if len(self.eye_center_history) >= 2:
            movements = []
            for i in range(1, len(self.eye_center_history)):
                prev_center = self.eye_center_history[i-1]
                curr_center = self.eye_center_history[i]
                movement = np.linalg.norm(np.array(curr_center) - np.array(prev_center))
                movements.append(movement)
            
            if movements:
                self.stress_metrics['eye_movement_intensity'] = np.mean(movements)
    
    def get_blink_statistics(self, time_window: int = 60) -> Dict[str, Any]:
        """
        Get blink statistics for the specified time window.
        
        Args:
            time_window: Time window in seconds (default: 60 seconds)
            
        Returns:
            Dictionary containing blink statistics
        """
        current_time = time.time()
        recent_blinks = [b for b in self.blink_history if current_time - b['timestamp'] <= time_window]
        
        if not recent_blinks:
            return {
                'blink_count': 0,
                'blink_rate': 0.0,
                'avg_duration': 0.0,
                'min_duration': 0.0,
                'max_duration': 0.0,
                'rapid_blinks': 0,
                'prolonged_blinks': 0
            }
        
        durations = [b['duration'] for b in recent_blinks]
        rapid_blinks = len([d for d in durations if d < 0.1])
        prolonged_blinks = len([d for d in durations if d > 0.5])
        
        return {
            'blink_count': len(recent_blinks),
            'blink_rate': len(recent_blinks) / (time_window / 60),  # blinks per minute
            'avg_duration': np.mean(durations),
            'min_duration': np.min(durations),
            'max_duration': np.max(durations),
            'rapid_blinks': rapid_blinks,
            'prolonged_blinks': prolonged_blinks
        }
    
    def draw_eye_tracking_info(self, frame: np.ndarray, 
                              eye_landmarks: Dict[str, np.ndarray],
                              tracking_results: Dict[str, Any]) -> np.ndarray:
        """
        Draw eye tracking information on the frame.
        
        Args:
            frame: Input frame to draw on
            eye_landmarks: Eye landmarks dictionary
            tracking_results: Results from process_eyes method
            
        Returns:
            Frame with eye tracking visualization
        """
        output_frame = frame.copy()
        
        # Draw EAR values
        left_ear = tracking_results.get('left_ear', 0)
        right_ear = tracking_results.get('right_ear', 0)
        avg_ear = tracking_results.get('avg_ear', 0)
        
        cv2.putText(output_frame, f"Left EAR: {left_ear:.3f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(output_frame, f"Right EAR: {right_ear:.3f}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(output_frame, f"Avg EAR: {avg_ear:.3f}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Draw blink information
        blink_status = "BLINKING" if tracking_results.get('is_blinking', False) else "OPEN"
        color = (0, 0, 255) if tracking_results.get('is_blinking', False) else (0, 255, 0)
        cv2.putText(output_frame, f"Status: {blink_status}", (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        cv2.putText(output_frame, f"Total Blinks: {tracking_results.get('total_blinks', 0)}", 
                   (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Draw stress metrics
        stress_metrics = tracking_results.get('stress_metrics', {})
        cv2.putText(output_frame, f"Blink Rate: {stress_metrics.get('blink_rate', 0):.1f}/min", 
                   (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Draw EAR threshold line (visual reference)
        if avg_ear > 0:
            threshold_y = int(300 + (self.ear_threshold - avg_ear) * 500)  # Scale for visualization
            cv2.line(output_frame, (200, threshold_y), (400, threshold_y), (0, 255, 255), 2)
            cv2.putText(output_frame, "EAR Threshold", (410, threshold_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        return output_frame
    
    def reset_metrics(self):
        """Reset all tracking metrics and history."""
        self.ear_history.clear()
        self.blink_history.clear()
        self.eye_center_history.clear()
        
        self.consecutive_frames_below_threshold = 0
        self.is_blinking = False
        self.blink_start_time = None
        self.total_blinks = 0
        
        self.stress_metrics = {
            'blink_rate': 0.0,
            'avg_blink_duration': 0.0,
            'eye_closure_ratio': 0.0,
            'eye_movement_intensity': 0.0,
            'rapid_blinks': 0,
            'prolonged_closures': 0
        }
        
        self.logger.info("Eye tracking metrics reset")
    
    def calibrate_threshold(self, calibration_samples: int = 100) -> float:
        """
        Calibrate EAR threshold based on user's normal eye state.
        This should be called during a calibration period when the user's eyes are open.
        
        Args:
            calibration_samples: Number of samples to use for calibration
            
        Returns:
            Recommended EAR threshold
        """
        if len(self.ear_history) < calibration_samples:
            self.logger.warning(f"Not enough samples for calibration: {len(self.ear_history)}/{calibration_samples}")
            return self.ear_threshold
        
        recent_ears = list(self.ear_history)[-calibration_samples:]
        mean_ear = np.mean(recent_ears)
        std_ear = np.std(recent_ears)
        
        # Set threshold as mean - 2*std (covers ~95% of normal variation)
        recommended_threshold = max(0.15, mean_ear - 2 * std_ear)
        
        self.logger.info(f"Calibrated EAR threshold: {recommended_threshold:.3f} (was {self.ear_threshold:.3f})")
        
        return recommended_threshold
