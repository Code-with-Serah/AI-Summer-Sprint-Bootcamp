"""
GUI Module for Stress Detection Application
Manages the main window and user interface with real-time video feed.
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading
import time
from PIL import Image, ImageTk
from core.facial_expression_analyzer import FacialExpressionAnalyzer

class StressDetectionGUI:
    """
    Real-time stress detection GUI with video feed and analysis display.
    """
    
    def __init__(self, face_detector, eye_tracker, stress_analyzer, config):
        """
        Initialize the GUI.

        Args:
            face_detector: Instance of the FaceDetector class
            eye_tracker: Instance of the EyeTracker class
            stress_analyzer: Instance of the StressAnalyzer class
            config: Application configuration manager
        """
        self.face_detector = face_detector
        self.eye_tracker = eye_tracker
        self.stress_analyzer = stress_analyzer
        self.expression_analyzer = FacialExpressionAnalyzer()
        self.config = config
        
        # Video capture setup
        self.cap = None
        self.is_running = False
        
        # GUI components
        self.root = None
        self.video_label = None
        self.metrics_frame = None
        
        # Current analysis data
        self.current_metrics = {
            'face_detected': False,
            'blink_rate': 0.0,
            'expression': 'neutral',
            'stress_score': 0.0,
            'stress_level': 'low'
        }
        
    def run(self):
        """Start the GUI application."""
        try:
            # Initialize video capture
            self.cap = cv2.VideoCapture(self.config.get('camera_id', 0))
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return
            
            # Create GUI window
            self.create_gui()
            
            # Start video processing thread
            self.is_running = True
            video_thread = threading.Thread(target=self.video_loop, daemon=True)
            video_thread.start()
            
            # Start GUI main loop
            self.root.mainloop()
            
        except Exception as e:
            print(f"GUI Error: {str(e)}")
        finally:
            self.cleanup()
    
    def create_gui(self):
        """Create the main GUI window and components."""
        self.root = tk.Tk()
        self.root.title("Stress Detection System")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video display
        video_frame = ttk.LabelFrame(main_frame, text="Live Video Feed", padding="5")
        video_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.video_label = ttk.Label(video_frame)
        self.video_label.grid(row=0, column=0)
        
        # Metrics display
        self.metrics_frame = ttk.LabelFrame(main_frame, text="Real-time Metrics", padding="10")
        self.metrics_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Create metric labels
        self.create_metrics_display()
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons
        ttk.Button(control_frame, text="Reset Metrics", command=self.reset_metrics).grid(row=0, column=0, pady=5)
        ttk.Button(control_frame, text="Calibrate", command=self.calibrate).grid(row=1, column=0, pady=5)
        ttk.Button(control_frame, text="Exit", command=self.on_closing).grid(row=2, column=0, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
    
    def create_metrics_display(self):
        """Create the metrics display panel."""
        # Face detection status
        ttk.Label(self.metrics_frame, text="Face Detection:").grid(row=0, column=0, sticky=tk.W)
        self.face_status_var = tk.StringVar(value="No Face")
        ttk.Label(self.metrics_frame, textvariable=self.face_status_var).grid(row=0, column=1, sticky=tk.W)
        
        # Expression
        ttk.Label(self.metrics_frame, text="Expression:").grid(row=1, column=0, sticky=tk.W)
        self.expression_var = tk.StringVar(value="neutral")
        ttk.Label(self.metrics_frame, textvariable=self.expression_var).grid(row=1, column=1, sticky=tk.W)
        
        # Blink rate
        ttk.Label(self.metrics_frame, text="Blink Rate:").grid(row=2, column=0, sticky=tk.W)
        self.blink_rate_var = tk.StringVar(value="0.0 /min")
        ttk.Label(self.metrics_frame, textvariable=self.blink_rate_var).grid(row=2, column=1, sticky=tk.W)
        
        # Stress level
        ttk.Label(self.metrics_frame, text="Stress Level:").grid(row=3, column=0, sticky=tk.W)
        self.stress_level_var = tk.StringVar(value="Low")
        self.stress_level_label = ttk.Label(self.metrics_frame, textvariable=self.stress_level_var)
        self.stress_level_label.grid(row=3, column=1, sticky=tk.W)
        
        # Stress score
        ttk.Label(self.metrics_frame, text="Stress Score:").grid(row=4, column=0, sticky=tk.W)
        self.stress_score_var = tk.StringVar(value="0.0")
        ttk.Label(self.metrics_frame, textvariable=self.stress_score_var).grid(row=4, column=1, sticky=tk.W)
        
        # Action units (facial expressions)
        ttk.Label(self.metrics_frame, text="Action Units:").grid(row=5, column=0, sticky=tk.W, pady=(10, 0))
        self.au_frame = ttk.Frame(self.metrics_frame)
        self.au_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Create AU progress bars
        self.au_vars = {}
        self.au_progressbars = {}
        au_names = ['AU12 (Smile)', 'AU15 (Frown)', 'AU4 (Furrow)', 'Jaw Clench']
        
        for i, au_name in enumerate(au_names):
            ttk.Label(self.au_frame, text=au_name).grid(row=i, column=0, sticky=tk.W)
            self.au_vars[au_name] = tk.DoubleVar()
            progress = ttk.Progressbar(self.au_frame, variable=self.au_vars[au_name], maximum=100)
            progress.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
            self.au_progressbars[au_name] = progress
        
        self.au_frame.columnconfigure(1, weight=1)
    
    def video_loop(self):
        """Main video processing loop."""
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process frame
                self.process_frame(frame)
                
                # Display frame
                self.display_frame(frame)
                
                # Update metrics display
                self.update_metrics_display()
                
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"Video loop error: {str(e)}")
                break
    
    def process_frame(self, frame):
        """Process a single frame for analysis."""
        # Detect faces
        face_result = self.face_detector.detect_faces(frame)
        
        if face_result['faces_detected']:
            landmarks = face_result['landmarks']
            
            # Update face detection status
            self.current_metrics['face_detected'] = True
            
            # Eye tracking and blink detection
            eye_landmarks = self.face_detector.get_eye_landmarks(landmarks)
            eye_result = self.eye_tracker.process_eyes(eye_landmarks)
            
            # Expression analysis
            expression_result = self.expression_analyzer.analyze_expression(landmarks)
            
            # Update current metrics
            self.current_metrics.update({
                'blink_rate': eye_result.get('stress_metrics', {}).get('blink_rate', 0.0),
                'expression': expression_result.get('primary_expression', 'neutral'),
                'stress_score': expression_result.get('stress_score', 0.0),
                'stress_level': expression_result.get('stress_level', 'low'),
                'action_units': expression_result.get('action_units', {})
            })
            
            # Draw landmarks and info on frame
            frame = self.face_detector.draw_landmarks(frame, landmarks)
            frame = self.eye_tracker.draw_eye_tracking_info(frame, eye_landmarks, eye_result)
            
        else:
            self.current_metrics['face_detected'] = False
    
    def display_frame(self, frame):
        """Display the processed frame in the GUI."""
        try:
            # Resize frame for display
            display_frame = cv2.resize(frame, (640, 480))
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_frame)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update video label
            if self.video_label:
                self.video_label.configure(image=photo)
                self.video_label.image = photo  # Keep a reference
                
        except Exception as e:
            print(f"Display frame error: {str(e)}")
    
    def update_metrics_display(self):
        """Update the metrics display panel."""
        try:
            if not self.root:
                return
                
            # Update face detection status
            face_status = "Face Detected" if self.current_metrics['face_detected'] else "No Face"
            self.face_status_var.set(face_status)
            
            # Update expression
            self.expression_var.set(self.current_metrics.get('expression', 'neutral'))
            
            # Update blink rate
            blink_rate = self.current_metrics.get('blink_rate', 0.0)
            self.blink_rate_var.set(f"{blink_rate:.1f} /min")
            
            # Update stress level and score
            stress_level = self.current_metrics.get('stress_level', 'low')
            stress_score = self.current_metrics.get('stress_score', 0.0)
            
            self.stress_level_var.set(stress_level.title())
            self.stress_score_var.set(f"{stress_score:.2f}")
            
            # Color code stress level
            if stress_level == 'high':
                self.stress_level_label.configure(foreground='red')
            elif stress_level == 'medium':
                self.stress_level_label.configure(foreground='orange')
            else:
                self.stress_level_label.configure(foreground='green')
            
            # Update action units
            action_units = self.current_metrics.get('action_units', {})
            au_mapping = {
                'AU12 (Smile)': action_units.get('AU12', 0.0),
                'AU15 (Frown)': action_units.get('AU15', 0.0),
                'AU4 (Furrow)': action_units.get('AU4', 0.0),
                'Jaw Clench': action_units.get('JAW_CLENCH', 0.0)
            }
            
            for au_name, value in au_mapping.items():
                if au_name in self.au_vars:
                    self.au_vars[au_name].set(value * 100)  # Convert to percentage
            
            # Update status
            if self.current_metrics['face_detected']:
                self.status_var.set(f"Analyzing - {stress_level.title()} Stress")
            else:
                self.status_var.set("Ready - No face detected")
                
        except Exception as e:
            print(f"Update metrics error: {str(e)}")
    
    def reset_metrics(self):
        """Reset all tracking metrics."""
        try:
            self.eye_tracker.reset_metrics()
            # Reset expression analyzer if it has a reset method
            if hasattr(self.expression_analyzer, 'reset_metrics'):
                self.expression_analyzer.reset_metrics()
            print("Metrics reset")
        except Exception as e:
            print(f"Reset error: {str(e)}")
    
    def calibrate(self):
        """Start calibration process."""
        try:
            # Placeholder for calibration logic
            threshold = self.eye_tracker.calibrate_threshold()
            self.eye_tracker.ear_threshold = threshold
            print(f"Calibration completed. New threshold: {threshold:.3f}")
        except Exception as e:
            print(f"Calibration error: {str(e)}")
    
    def on_closing(self):
        """Handle window closing event."""
        self.is_running = False
        if self.root:
            self.root.destroy()
    
    def cleanup(self):
        """Clean up resources."""
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
