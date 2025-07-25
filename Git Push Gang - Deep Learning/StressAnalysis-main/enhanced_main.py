#!/usr/bin/env python3
"""
Enhanced Stress Detection System - Main Application Entry Point
Real-time facial stress detection with advanced visualization.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.face_detector import FaceDetector
from src.core.eye_tracker import EyeTracker
from src.core.stress_analyzer import StressAnalyzer
from src.gui.enhanced_main_window import EnhancedStressDetectionGUI
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger


def main():
    """Main application entry point for the enhanced GUI."""
    # Setup logging
    logger = setup_logger()

    # Load configuration
    config = ConfigManager()

    logger.info("Starting Enhanced Stress Detection System...")

    try:
        # Initialize core components
        face_detector = FaceDetector()
        eye_tracker = EyeTracker()
        stress_analyzer = StressAnalyzer()

        # Start Enhanced GUI application
        app = EnhancedStressDetectionGUI(
            face_detector=face_detector,
            eye_tracker=eye_tracker,
            stress_analyzer=stress_analyzer,
            config=config
        )

        app.run()

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

    logger.info("Enhanced Stress Detection System terminated.")


if __name__ == "__main__":
    main()

