#!/usr/bin/env python3
"""
Stress Detection System - Main Application Entry Point
Real-time facial stress detection using computer vision techniques.
"""

import sys
import cv2
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.face_detector import FaceDetector
from src.core.eye_tracker import EyeTracker
from src.core.stress_analyzer import StressAnalyzer
from src.core.facial_expression_analyzer import FacialExpressionAnalyzer
from src.gui.main_window import StressDetectionGUI
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger

def main():
    """Main application entry point."""
    # Setup logging
    logger = setup_logger()
    
    # Load configuration
    config = ConfigManager()
    
    logger.info("Starting Stress Detection System...")
    
    try:
        # Initialize core components
        face_detector = FaceDetector()
        eye_tracker = EyeTracker()
        stress_analyzer = StressAnalyzer()
        expression_analyzer = FacialExpressionAnalyzer()
        
        # Start GUI application
        app = StressDetectionGUI(
            face_detector=face_detector,
            eye_tracker=eye_tracker,
            stress_analyzer=stress_analyzer,
            config=config
        )
        
        app.run()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
    
    logger.info("Stress Detection System terminated.")

if __name__ == "__main__":
    main()
