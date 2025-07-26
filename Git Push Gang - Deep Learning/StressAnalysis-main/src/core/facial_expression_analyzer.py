"""
Facial Expression Analysis Module
Implements emotion recognition and stress detection using facial landmarks.
Detects micro-expressions, facial action units, and stress indicators.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import logging
from collections import deque
import time

class FacialExpressionAnalyzer:
    """
    Analyzes facial expressions and detects stress indicators using facial landmarks.
    Implements facial action units (AU) recognition and micro-expression detection.
    """
    
    def __init__(self, history_size: int = 30):
        """Initialize the expression analyzer."""
        self.logger = logging.getLogger(__name__)
        
        # MediaPipe landmark indices for key facial features
        self.MOUTH_LANDMARKS = {
            'outer_lip': [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318],
            'inner_lip': [78, 81, 13, 311, 402, 317, 304, 376, 310, 415, 324, 320],
            'corners': [61, 291],  # Left and right mouth corners
            'top_lip': [13, 311, 15, 16, 17, 18, 200],
            'bottom_lip': [14, 317, 316, 315, 314, 313, 312]
        }
        
        self.EYEBROW_LANDMARKS = {
            'left_eyebrow': [46, 53, 52, 51, 48],
            'right_eyebrow': [276, 283, 282, 281, 278]
        }
        
        self.JAW_LANDMARKS = [172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323]
        
        # History tracking for micro-expressions
        self.history_size = history_size
        self.expression_history = deque(maxlen=history_size)
        self.stress_indicators_history = deque(maxlen=history_size)
        
        # Stress detection thresholds (will be calibrated)
        self.thresholds = {
            'mouth_tension': 0.7,
            'eyebrow_furrow': 0.6,
            'jaw_clench': 0.8,
            'smile_intensity': 0.5,
            'frown_intensity': 0.4
        }
        
        # Baseline measurements for normalization
        self.baseline = {
            'mouth_width': None,
            'mouth_height': None,
            'eyebrow_distance': None,
            'jaw_width': None
        }
        
        self.logger.info("FacialExpressionAnalyzer initialized successfully")

    def analyze_expression(self, landmarks: np.ndarray) -> Dict[str, Any]:
        """
        Analyze facial expression and detect stress indicators.
        
        Args:
            landmarks: Complete face landmarks array (MediaPipe format)
            
        Returns:
            Dictionary with comprehensive expression analysis results
        """
        if landmarks is None or len(landmarks) == 0:
            return self._empty_result()

        try:
            # Calculate facial action units
            action_units = self._calculate_action_units(landmarks)
            
            # Detect micro-expressions
            expressions = self._detect_expressions(action_units)
            
            # Detect stress indicators
            stress_indicators = self._detect_stress_indicators(landmarks, action_units)
            
            # Calculate overall stress score
            stress_score = self._calculate_stress_score(stress_indicators)
            
            # Store in history for trend analysis
            analysis_result = {
                'timestamp': time.time(),
                'expressions': expressions,
                'action_units': action_units,
                'stress_indicators': stress_indicators,
                'stress_score': stress_score,
                'primary_expression': self._get_primary_expression(expressions),
                'stress_level': self._categorize_stress_level(stress_score)
            }
            
            self.expression_history.append(analysis_result)
            
            self.logger.debug(f"Expression analysis: {analysis_result['primary_expression']}, Stress: {analysis_result['stress_level']}")
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error in expression analysis: {str(e)}")
            return self._empty_result()
    
    def _calculate_action_units(self, landmarks: np.ndarray) -> Dict[str, float]:
        """
        Calculate Facial Action Units (AU) based on landmark positions.
        
        Args:
            landmarks: Face landmarks array
            
        Returns:
            Dictionary of action unit intensities
        """
        action_units = {}
        
        try:
            # AU12: Lip Corner Puller (Smile)
            action_units['AU12'] = self._calculate_smile_intensity(landmarks)
            
            # AU15: Lip Corner Depressor (Frown)
            action_units['AU15'] = self._calculate_frown_intensity(landmarks)
            
            # AU4: Brow Lowerer (Furrow)
            action_units['AU4'] = self._calculate_brow_furrow(landmarks)
            
            # AU1: Inner Brow Raiser
            action_units['AU1'] = self._calculate_inner_brow_raise(landmarks)
            
            # AU2: Outer Brow Raiser
            action_units['AU2'] = self._calculate_outer_brow_raise(landmarks)
            
            # AU26: Jaw Drop
            action_units['AU26'] = self._calculate_jaw_drop(landmarks)
            
            # Custom: Jaw Clench (stress indicator)
            action_units['JAW_CLENCH'] = self._calculate_jaw_clench(landmarks)
            
            # AU23: Lip Tightener
            action_units['AU23'] = self._calculate_lip_tightness(landmarks)
            
        except Exception as e:
            self.logger.error(f"Error calculating action units: {str(e)}")
            
        return action_units
    
    def _calculate_smile_intensity(self, landmarks: np.ndarray) -> float:
        """Calculate smile intensity based on mouth corner elevation."""
        try:
            # Get mouth corners and center points
            left_corner = landmarks[61]  # Left mouth corner
            right_corner = landmarks[291]  # Right mouth corner
            mouth_center_top = landmarks[13]  # Top lip center
            mouth_center_bottom = landmarks[14]  # Bottom lip center
            
            # Calculate mouth width and corner elevation
            mouth_width = np.linalg.norm(right_corner - left_corner)
            mouth_center = (mouth_center_top + mouth_center_bottom) / 2
            
            # Calculate how much corners are raised relative to center
            left_elevation = left_corner[1] - mouth_center[1]  # Negative = raised
            right_elevation = right_corner[1] - mouth_center[1]
            
            # Normalize by mouth width
            smile_intensity = max(0, -(left_elevation + right_elevation) / (2 * mouth_width))
            
            return min(1.0, smile_intensity * 2)  # Scale and cap at 1.0
            
        except Exception:
            return 0.0
    
    def _calculate_frown_intensity(self, landmarks: np.ndarray) -> float:
        """Calculate frown intensity based on mouth corner depression."""
        try:
            left_corner = landmarks[61]
            right_corner = landmarks[291]
            mouth_center_top = landmarks[13]
            mouth_center_bottom = landmarks[14]
            
            mouth_width = np.linalg.norm(right_corner - left_corner)
            mouth_center = (mouth_center_top + mouth_center_bottom) / 2
            
            # Calculate how much corners are lowered
            left_depression = mouth_center[1] - left_corner[1]  # Positive = lowered
            right_depression = mouth_center[1] - right_corner[1]
            
            frown_intensity = max(0, (left_depression + right_depression) / (2 * mouth_width))
            
            return min(1.0, frown_intensity * 2)
            
        except Exception:
            return 0.0
    
    def _calculate_brow_furrow(self, landmarks: np.ndarray) -> float:
        """Calculate eyebrow furrowing intensity."""
        try:
            # Inner eyebrow points
            left_inner = landmarks[46]
            right_inner = landmarks[276]
            
            # Outer eyebrow points
            left_outer = landmarks[53]
            right_outer = landmarks[283]
            
            # Calculate the angle and distance between inner brow points
            inner_distance = np.linalg.norm(right_inner - left_inner)
            outer_distance = np.linalg.norm(right_outer - left_outer)
            
            # Furrowing reduces inner distance relative to outer distance
            furrow_ratio = 1 - (inner_distance / outer_distance) if outer_distance > 0 else 0
            
            return max(0, min(1.0, furrow_ratio * 3))  # Scale appropriately
            
        except Exception:
            return 0.0
    
    def _calculate_inner_brow_raise(self, landmarks: np.ndarray) -> float:
        """Calculate inner eyebrow raise intensity."""
        try:
            # Inner eyebrow points
            left_inner = landmarks[46]
            right_inner = landmarks[276]
            
            # Eye centers for reference
            left_eye_center = np.mean(landmarks[[33, 133]], axis=0)
            right_eye_center = np.mean(landmarks[[362, 263]], axis=0)
            
            # Calculate vertical distance from eye to inner brow
            left_raise = left_eye_center[1] - left_inner[1]
            right_raise = right_eye_center[1] - right_inner[1]
            
            # Normalize by face height approximation
            face_height = abs(landmarks[10][1] - landmarks[152][1])
            
            raise_intensity = (left_raise + right_raise) / (2 * face_height) if face_height > 0 else 0
            
            return max(0, min(1.0, raise_intensity * 5))
            
        except Exception:
            return 0.0
    
    def _calculate_outer_brow_raise(self, landmarks: np.ndarray) -> float:
        """Calculate outer eyebrow raise intensity."""
        try:
            # Outer eyebrow points
            left_outer = landmarks[53]
            right_outer = landmarks[283]
            
            # Outer eye corners for reference
            left_eye_outer = landmarks[33]
            right_eye_outer = landmarks[362]
            
            # Calculate vertical distance
            left_raise = left_eye_outer[1] - left_outer[1]
            right_raise = right_eye_outer[1] - right_outer[1]
            
            face_height = abs(landmarks[10][1] - landmarks[152][1])
            
            raise_intensity = (left_raise + right_raise) / (2 * face_height) if face_height > 0 else 0
            
            return max(0, min(1.0, raise_intensity * 5))
            
        except Exception:
            return 0.0
    
    def _calculate_jaw_drop(self, landmarks: np.ndarray) -> float:
        """Calculate jaw drop intensity."""
        try:
            # Jaw points
            jaw_bottom = landmarks[17]  # Bottom of jaw
            mouth_top = landmarks[13]  # Top lip center
            
            # Calculate jaw opening
            jaw_opening = abs(jaw_bottom[1] - mouth_top[1])
            
            # Normalize by face height
            face_height = abs(landmarks[10][1] - landmarks[152][1])
            
            jaw_drop_ratio = jaw_opening / face_height if face_height > 0 else 0
            
            return max(0, min(1.0, jaw_drop_ratio * 10))
            
        except Exception:
            return 0.0
    
    def _calculate_jaw_clench(self, landmarks: np.ndarray) -> float:
        """Calculate jaw clenching intensity (stress indicator)."""
        try:
            # Jaw width points
            left_jaw = landmarks[172]
            right_jaw = landmarks[397]
            
            # Calculate jaw width
            jaw_width = np.linalg.norm(right_jaw - left_jaw)
            
            # Compare with baseline or use relative measure
            if self.baseline['jaw_width'] is None:
                self.baseline['jaw_width'] = jaw_width
                return 0.0
            
            # Clenching typically increases jaw width slightly
            clench_ratio = (jaw_width - self.baseline['jaw_width']) / self.baseline['jaw_width']
            
            return max(0, min(1.0, clench_ratio * 5))
            
        except Exception:
            return 0.0
    
    def _calculate_lip_tightness(self, landmarks: np.ndarray) -> float:
        """Calculate lip tightness (stress indicator)."""
        try:
            # Outer lip points
            top_lip = landmarks[13]
            bottom_lip = landmarks[14]
            left_corner = landmarks[61]
            right_corner = landmarks[291]
            
            # Calculate lip height and width
            lip_height = abs(top_lip[1] - bottom_lip[1])
            lip_width = np.linalg.norm(right_corner - left_corner)
            
            # Lip aspect ratio (lower = tighter lips)
            lip_ratio = lip_height / lip_width if lip_width > 0 else 0
            
            # Tightness is inverse of the ratio
            tightness = max(0, 1 - (lip_ratio * 10))
            
            return min(1.0, tightness)
            
        except Exception:
            return 0.0
    
    def _detect_expressions(self, action_units: Dict[str, float]) -> Dict[str, float]:
        """
        Detect facial expressions based on action units.
        
        Args:
            action_units: Dictionary of calculated action unit intensities
            
        Returns:
            Dictionary of expression probabilities
        """
        expressions = {
            'happy': 0.0,
            'sad': 0.0,
            'angry': 0.0,
            'surprised': 0.0,
            'disgusted': 0.0,
            'fearful': 0.0,
            'neutral': 0.0,
            'stressed': 0.0
        }
        
        try:
            # Happy: Strong AU12 (lip corner puller)
            if 'AU12' in action_units:
                expressions['happy'] = min(1.0, action_units['AU12'])
            
            # Sad: Strong AU15 (lip corner depressor)
            if 'AU15' in action_units:
                expressions['sad'] = min(1.0, action_units['AU15'])
            
            # Angry: AU4 (brow lowerer) + AU23 (lip tightener)
            angry_score = 0.0
            if 'AU4' in action_units:
                angry_score += action_units['AU4'] * 0.6
            if 'AU23' in action_units:
                angry_score += action_units['AU23'] * 0.4
            expressions['angry'] = min(1.0, angry_score)
            
            # Surprised: AU1 + AU2 (inner and outer brow raiser) + AU26 (jaw drop)
            surprised_score = 0.0
            if 'AU1' in action_units:
                surprised_score += action_units['AU1'] * 0.4
            if 'AU2' in action_units:
                surprised_score += action_units['AU2'] * 0.3
            if 'AU26' in action_units:
                surprised_score += action_units['AU26'] * 0.3
            expressions['surprised'] = min(1.0, surprised_score)
            
            # Stressed: Combination of jaw clench, brow furrow, and lip tightness
            stressed_score = 0.0
            if 'JAW_CLENCH' in action_units:
                stressed_score += action_units['JAW_CLENCH'] * 0.4
            if 'AU4' in action_units:
                stressed_score += action_units['AU4'] * 0.3
            if 'AU23' in action_units:
                stressed_score += action_units['AU23'] * 0.3
            expressions['stressed'] = min(1.0, stressed_score)
            
            # Neutral: inverse of all other expressions
            total_expression = sum([v for k, v in expressions.items() if k != 'neutral'])
            expressions['neutral'] = max(0.0, 1.0 - total_expression)
            
        except Exception as e:
            self.logger.error(f"Error detecting expressions: {str(e)}")
            expressions['neutral'] = 1.0
        
        return expressions
    
    def _detect_stress_indicators(self, landmarks: np.ndarray, action_units: Dict[str, float]) -> Dict[str, float]:
        """
        Detect specific stress indicators from facial analysis.
        
        Args:
            landmarks: Face landmarks array
            action_units: Calculated action units
            
        Returns:
            Dictionary of stress indicator intensities
        """
        indicators = {
            'jaw_clench': action_units.get('JAW_CLENCH', 0.0),
            'lip_tightness': action_units.get('AU23', 0.0),
            'brow_furrow': action_units.get('AU4', 0.0),
            'mouth_tension': self._calculate_mouth_tension(landmarks),
            'facial_asymmetry': self._calculate_facial_asymmetry(landmarks)
        }
        
        return indicators
    
    def _calculate_mouth_tension(self, landmarks: np.ndarray) -> float:
        """
        Calculate mouth tension as a stress indicator.
        
        Args:
            landmarks: Face landmarks array
            
        Returns:
            Mouth tension intensity (0.0 to 1.0)
        """
        try:
            # Get mouth landmarks
            top_lip = landmarks[13]
            bottom_lip = landmarks[14]
            left_corner = landmarks[61]
            right_corner = landmarks[291]
            
            # Calculate mouth dimensions
            mouth_height = abs(top_lip[1] - bottom_lip[1])
            mouth_width = np.linalg.norm(right_corner - left_corner)
            
            # Mouth aspect ratio - tension reduces height relative to width
            aspect_ratio = mouth_height / mouth_width if mouth_width > 0 else 0
            
            # Tension is indicated by very low aspect ratio
            tension = max(0.0, (0.1 - aspect_ratio) * 10) if aspect_ratio < 0.1 else 0.0
            
            return min(1.0, tension)
            
        except Exception:
            return 0.0
    
    def _calculate_facial_asymmetry(self, landmarks: np.ndarray) -> float:
        """
        Calculate facial asymmetry as a stress indicator.
        
        Args:
            landmarks: Face landmarks array
            
        Returns:
            Facial asymmetry intensity (0.0 to 1.0)
        """
        try:
            # Compare left and right side features
            # Mouth corners
            left_mouth = landmarks[61]
            right_mouth = landmarks[291]
            mouth_center = landmarks[13]
            
            # Calculate distances from center
            left_dist = np.linalg.norm(left_mouth - mouth_center)
            right_dist = np.linalg.norm(right_mouth - mouth_center)
            
            # Asymmetry ratio
            asymmetry = abs(left_dist - right_dist) / max(left_dist, right_dist, 1e-6)
            
            return min(1.0, asymmetry * 2)
            
        except Exception:
            return 0.0
    
    def _calculate_stress_score(self, stress_indicators: Dict[str, float]) -> float:
        """
        Calculate overall stress score from individual indicators.
        
        Args:
            stress_indicators: Dictionary of stress indicator intensities
            
        Returns:
            Overall stress score (0.0 to 1.0)
        """
        weights = {
            'jaw_clench': 0.3,
            'lip_tightness': 0.2,
            'brow_furrow': 0.2,
            'mouth_tension': 0.15,
            'facial_asymmetry': 0.15
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for indicator, value in stress_indicators.items():
            if indicator in weights:
                weight = weights[indicator]
                total_score += value * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _get_primary_expression(self, expressions: Dict[str, float]) -> str:
        """
        Get the primary (strongest) expression.
        
        Args:
            expressions: Dictionary of expression probabilities
            
        Returns:
            Name of the primary expression
        """
        if not expressions:
            return 'neutral'
        
        return max(expressions.items(), key=lambda x: x[1])[0]
    
    def _categorize_stress_level(self, stress_score: float) -> str:
        """
        Categorize stress level based on stress score.
        
        Args:
            stress_score: Overall stress score (0.0 to 1.0)
            
        Returns:
            Stress level category
        """
        if stress_score < 0.2:
            return 'low'
        elif stress_score < 0.4:
            return 'mild'
        elif stress_score < 0.6:
            return 'moderate'
        elif stress_score < 0.8:
            return 'high'
        else:
            return 'very_high'
    
    def _empty_result(self) -> Dict[str, Any]:
        """
        Return empty/default analysis result.
        
        Returns:
            Dictionary with default values
        """
        return {
            'timestamp': time.time(),
            'expressions': {
                'happy': 0.0,
                'sad': 0.0,
                'angry': 0.0,
                'surprised': 0.0,
                'disgusted': 0.0,
                'fearful': 0.0,
                'neutral': 1.0,
                'stressed': 0.0
            },
            'action_units': {},
            'stress_indicators': {
                'jaw_clench': 0.0,
                'lip_tightness': 0.0,
                'brow_furrow': 0.0,
                'mouth_tension': 0.0,
                'facial_asymmetry': 0.0
            },
            'stress_score': 0.0,
            'primary_expression': 'neutral',
            'stress_level': 'low'
        }
    
    def get_trend_analysis(self) -> Dict[str, Any]:
        """
        Analyze trends in expression and stress over recent history.
        
        Returns:
            Dictionary with trend analysis results
        """
        if len(self.expression_history) < 5:
            return {
                'stress_trend': 'stable',
                'expression_stability': 1.0,
                'average_stress': 0.0,
                'peak_stress': 0.0
            }
        
        recent_data = list(self.expression_history)[-10:]  # Last 10 readings
        
        # Calculate stress trend
        stress_scores = [data['stress_score'] for data in recent_data]
        stress_trend = 'increasing' if stress_scores[-1] > stress_scores[0] else 'decreasing'
        if abs(stress_scores[-1] - stress_scores[0]) < 0.1:
            stress_trend = 'stable'
        
        # Calculate expression stability
        primary_expressions = [data['primary_expression'] for data in recent_data]
        unique_expressions = len(set(primary_expressions))
        expression_stability = max(0.0, 1.0 - (unique_expressions - 1) / len(primary_expressions))
        
        return {
            'stress_trend': stress_trend,
            'expression_stability': expression_stability,
            'average_stress': np.mean(stress_scores),
            'peak_stress': max(stress_scores),
            'recent_expressions': primary_expressions
        }
    
    def calibrate_baseline(self, landmarks: np.ndarray):
        """
        Calibrate baseline measurements for stress detection.
        
        Args:
            landmarks: Face landmarks for baseline calibration
        """
        try:
            if landmarks is not None and len(landmarks) > 0:
                # Calculate baseline mouth dimensions
                left_corner = landmarks[61]
                right_corner = landmarks[291]
                top_lip = landmarks[13]
                bottom_lip = landmarks[14]
                
                self.baseline['mouth_width'] = np.linalg.norm(right_corner - left_corner)
                self.baseline['mouth_height'] = abs(top_lip[1] - bottom_lip[1])
                
                # Calculate baseline eyebrow distance
                left_brow = landmarks[46]
                right_brow = landmarks[276]
                self.baseline['eyebrow_distance'] = np.linalg.norm(right_brow - left_brow)
                
                # Calculate baseline jaw width
                left_jaw = landmarks[172]
                right_jaw = landmarks[397]
                self.baseline['jaw_width'] = np.linalg.norm(right_jaw - left_jaw)
                
                self.logger.info("Baseline calibration completed")
                
        except Exception as e:
            self.logger.error(f"Error during baseline calibration: {str(e)}")
    
    def reset_history(self):
        """
        Reset expression and stress history.
        """
        self.expression_history.clear()
        self.stress_indicators_history.clear()
        self.logger.info("Expression history reset")

