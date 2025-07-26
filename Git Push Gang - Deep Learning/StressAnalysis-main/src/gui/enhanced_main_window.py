"""
Enhanced GUI Module for Stress Detection Application
Includes charts, gauges, historical data visualization, and export functionality.
Phase 4 implementation with advanced UI features.
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import json
import csv
from datetime import datetime
from collections import deque
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTk as FigureCanvasTkinter
from matplotlib.figure import Figure
import matplotlib.animation as animation
from src.core.facial_expression_analyzer import FacialExpressionAnalyzer

class EnhancedStressDetectionGUI:
    """
    Enhanced real-time stress detection GUI with advanced visualization and data export.
    Phase 4 implementation with charts, gauges, and historical analysis.
    """
    
    def __init__(self, face_detector, eye_tracker, stress_analyzer, config):
        """
        Initialize the enhanced GUI.

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
        self.chart_frame = None
        
        # Data storage for historical analysis
        self.max_history_points = 300  # 10 minutes at 30 FPS
        self.stress_history = deque(maxlen=self.max_history_points)
        self.blink_history = deque(maxlen=self.max_history_points)
        self.expression_history = deque(maxlen=self.max_history_points)
        self.timestamps = deque(maxlen=self.max_history_points)
        
        # Session data for export
        self.session_start_time = datetime.now()
        self.session_data = []
        
        # Current analysis data
        self.current_metrics = {
            'face_detected': False,
            'blink_rate': 0.0,
            'expression': 'neutral',
            'stress_score': 0.0,
            'stress_level': 'low',
            'timestamp': 0
        }
        
        # Chart components
        self.figure = None
        self.canvas = None
        self.stress_ax = None
        self.blink_ax = None
        
        # Gauge components (stress level gauge)
        self.stress_gauge_var = None
        self.stress_gauge = None
        
    def run(self):
        """Start the enhanced GUI application."""
        try:
            # Initialize video capture
            self.cap = cv2.VideoCapture(self.config.get('camera_id', 0))
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return
            
            # Create enhanced GUI window
            self.create_enhanced_gui()
            
            # Start video processing thread
            self.is_running = True
            video_thread = threading.Thread(target=self.video_loop, daemon=True)
            video_thread.start()
            
            # Start data recording thread
            data_thread = threading.Thread(target=self.data_recording_loop, daemon=True)
            data_thread.start()
            
            # Start chart update animation
            self.start_chart_animation()
            
            # Start GUI main loop
            self.root.mainloop()
            
        except Exception as e:
            print(f"Enhanced GUI Error: {str(e)}")
        finally:
            self.cleanup()
    
    def create_enhanced_gui(self):
        """Create the enhanced GUI window with advanced features."""
        self.root = tk.Tk()
        self.root.title("Enhanced Stress Detection System - Phase 4")
        self.root.geometry("1400x900")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Live Analysis
        self.live_tab = ttk.Frame(notebook)
        notebook.add(self.live_tab, text="Live Analysis")
        self.create_live_analysis_tab()
        
        # Tab 2: Historical Charts
        self.history_tab = ttk.Frame(notebook)
        notebook.add(self.history_tab, text="Historical Analysis")
        self.create_historical_charts_tab()
        
        # Tab 3: Data Export & Settings
        self.export_tab = ttk.Frame(notebook)
        notebook.add(self.export_tab, text="Data Export & Settings")
        self.create_export_settings_tab()
        
    def create_live_analysis_tab(self):
        """Create the live analysis tab with video and real-time metrics."""
        main_frame = ttk.Frame(self.live_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Video and basic metrics
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Video display
        video_frame = ttk.LabelFrame(left_frame, text="Live Video Feed", padding="5")
        video_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.video_label = ttk.Label(video_frame)
        self.video_label.pack()
        
        # Basic metrics display
        self.metrics_frame = ttk.LabelFrame(left_frame, text="Real-time Metrics", padding="10")
        self.metrics_frame.pack(fill=tk.X, pady=(0, 10))
        self.create_basic_metrics_display()
        
        # Control buttons
        control_frame = ttk.LabelFrame(left_frame, text="Controls", padding="10")
        control_frame.pack(fill=tk.X)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack()
        
        ttk.Button(button_frame, text="Reset Metrics", command=self.reset_metrics).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Calibrate", command=self.calibrate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Start Recording", command=self.start_recording).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop Recording", command=self.stop_recording).pack(side=tk.LEFT, padx=5)
        
        # Right side: Advanced metrics and gauges
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Stress Level Gauge
        gauge_frame = ttk.LabelFrame(right_frame, text="Stress Level Gauge", padding="10")
        gauge_frame.pack(fill=tk.X, pady=(0, 10))
        self.create_stress_gauge(gauge_frame)
        
        # Action Units Progress Bars
        au_frame = ttk.LabelFrame(right_frame, text="Facial Action Units", padding="10")
        au_frame.pack(fill=tk.X, pady=(0, 10))
        self.create_action_units_display(au_frame)
        
        # Mini real-time chart
        mini_chart_frame = ttk.LabelFrame(right_frame, text="Real-time Trend (30s)", padding="5")
        mini_chart_frame.pack(fill=tk.BOTH, expand=True)
        self.create_mini_chart(mini_chart_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
    def create_basic_metrics_display(self):
        """Create basic metrics display."""
        # Face detection status
        ttk.Label(self.metrics_frame, text="Face Detection:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.face_status_var = tk.StringVar(value="No Face")
        self.face_status_label = ttk.Label(self.metrics_frame, textvariable=self.face_status_var)
        self.face_status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Expression
        ttk.Label(self.metrics_frame, text="Primary Expression:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.expression_var = tk.StringVar(value="neutral")
        ttk.Label(self.metrics_frame, textvariable=self.expression_var).grid(row=1, column=1, sticky=tk.W)
        
        # Blink rate
        ttk.Label(self.metrics_frame, text="Blink Rate:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.blink_rate_var = tk.StringVar(value="0.0 /min")
        ttk.Label(self.metrics_frame, textvariable=self.blink_rate_var).grid(row=2, column=1, sticky=tk.W)
        
        # Stress score
        ttk.Label(self.metrics_frame, text="Stress Score:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        self.stress_score_var = tk.StringVar(value="0.00")
        ttk.Label(self.metrics_frame, textvariable=self.stress_score_var).grid(row=3, column=1, sticky=tk.W)
        
        # Session duration
        ttk.Label(self.metrics_frame, text="Session Duration:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
        self.session_duration_var = tk.StringVar(value="00:00:00")
        ttk.Label(self.metrics_frame, textvariable=self.session_duration_var).grid(row=4, column=1, sticky=tk.W)
        
    def create_stress_gauge(self, parent):
        """Create a visual stress level gauge."""
        # Stress level gauge using progressbar with color coding
        ttk.Label(parent, text="Current Stress Level:").pack()
        
        gauge_frame = ttk.Frame(parent)
        gauge_frame.pack(pady=10)
        
        # Initialize stress gauge variable
        self.stress_gauge_var = tk.DoubleVar()
        
        self.stress_gauge = ttk.Progressbar(
            gauge_frame, 
            variable=self.stress_gauge_var, 
            maximum=100, 
            length=300,
            mode='determinate'
        )
        self.stress_gauge.pack()
        
        # Stress level text
        self.stress_level_var = tk.StringVar(value="Low")
        self.stress_level_label = ttk.Label(gauge_frame, textvariable=self.stress_level_var, font=("Arial", 14, "bold"))
        self.stress_level_label.pack(pady=5)
        
        # Gauge labels
        labels_frame = ttk.Frame(gauge_frame)
        labels_frame.pack(pady=5)
        
        ttk.Label(labels_frame, text="Low", foreground="green").pack(side=tk.LEFT)
        ttk.Label(labels_frame, text="Moderate", foreground="orange").pack(side=tk.LEFT, padx=50)
        ttk.Label(labels_frame, text="High", foreground="red").pack(side=tk.RIGHT)
        
    def create_action_units_display(self, parent):
        """Create action units progress bars display."""
        self.au_vars = {}
        self.au_progressbars = {}
        
        au_data = [
            ('AU12 (Smile)', 'green'),
            ('AU15 (Frown)', 'red'),
            ('AU4 (Furrow)', 'orange'),
            ('Jaw Clench', 'red')
        ]
        
        for i, (au_name, color) in enumerate(au_data):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=au_name, width=15).pack(side=tk.LEFT)
            
            self.au_vars[au_name] = tk.DoubleVar()
            progress = ttk.Progressbar(
                frame, 
                variable=self.au_vars[au_name], 
                maximum=100,
                length=200
            )
            progress.pack(side=tk.LEFT, padx=10)
            
            # Value label
            value_label = ttk.Label(frame, text="0%")
            value_label.pack(side=tk.RIGHT)
            self.au_progressbars[au_name] = (progress, value_label)
    
    def create_mini_chart(self, parent):
        """Create a mini real-time chart."""
        # Create matplotlib figure for mini chart
        self.mini_figure = Figure(figsize=(6, 3), dpi=80)
        self.mini_ax = self.mini_figure.add_subplot(111)
        
        self.mini_canvas = FigureCanvasTkinter(self.mini_figure, parent)
        self.mini_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize empty plot
        self.mini_ax.set_title("Stress Level Trend (Last 30 seconds)")
        self.mini_ax.set_ylabel("Stress Score")
        self.mini_ax.set_ylim(0, 1)
        self.mini_ax.grid(True, alpha=0.3)
        
    def create_historical_charts_tab(self):
        """Create the historical analysis tab with detailed charts."""
        chart_frame = ttk.Frame(self.history_tab, padding="10")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control panel for chart options
        control_panel = ttk.LabelFrame(chart_frame, text="Chart Controls", padding="10")
        control_panel.pack(fill=tk.X, pady=(0, 10))
        
        # Time range selection
        ttk.Label(control_panel, text="Time Range:").pack(side=tk.LEFT)
        self.time_range_var = tk.StringVar(value="Last 5 minutes")
        time_range_combo = ttk.Combobox(control_panel, textvariable=self.time_range_var, 
                                       values=["Last 1 minute", "Last 5 minutes", "Last 10 minutes", "Full Session"])
        time_range_combo.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(control_panel, text="Refresh Charts", command=self.refresh_charts).pack(side=tk.LEFT, padx=10)
        
        # Charts area
        self.chart_frame = ttk.Frame(chart_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create main historical charts
        self.figure = Figure(figsize=(12, 8), dpi=80)
        
        # Stress score over time
        self.stress_ax = self.figure.add_subplot(3, 1, 1)
        self.stress_ax.set_title("Stress Level Over Time")
        self.stress_ax.set_ylabel("Stress Score")
        self.stress_ax.grid(True, alpha=0.3)
        
        # Blink rate over time  
        self.blink_ax = self.figure.add_subplot(3, 1, 2)
        self.blink_ax.set_title("Blink Rate Over Time")
        self.blink_ax.set_ylabel("Blinks/min")
        self.blink_ax.grid(True, alpha=0.3)
        
        # Expression distribution
        self.expression_ax = self.figure.add_subplot(3, 1, 3)
        self.expression_ax.set_title("Expression Distribution")
        self.expression_ax.set_ylabel("Frequency")
        self.expression_ax.grid(True, alpha=0.3)
        
        self.canvas = FigureCanvasTkinter(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_export_settings_tab(self):
        """Create the data export and settings tab."""
        main_frame = ttk.Frame(self.export_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Data Export Section
        export_frame = ttk.LabelFrame(main_frame, text="Data Export", padding="10")
        export_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Export options
        ttk.Label(export_frame, text="Export current session data:").pack(anchor=tk.W)
        
        export_buttons = ttk.Frame(export_frame)
        export_buttons.pack(pady=10)
        
        ttk.Button(export_buttons, text="Export as CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_buttons, text="Export as JSON", command=self.export_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_buttons, text="Export Charts as PNG", command=self.export_charts).pack(side=tk.LEFT, padx=5)
        
        # Session Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Session Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.stats_text = tk.Text(stats_frame, height=15, wrap=tk.WORD)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Update stats button
        ttk.Button(stats_frame, text="Update Statistics", command=self.update_session_stats).pack(pady=5)
        
        # Settings Section
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X)
        
        # Auto-export settings
        self.auto_export_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Auto-export data every 10 minutes", 
                       variable=self.auto_export_var).pack(anchor=tk.W)
        
        # Data retention settings
        ttk.Label(settings_frame, text="Data retention (minutes):").pack(anchor=tk.W, pady=(10, 0))
        self.retention_var = tk.StringVar(value="10")
        retention_spin = ttk.Spinbox(settings_frame, from_=1, to=60, textvariable=self.retention_var, width=10)
        retention_spin.pack(anchor=tk.W, pady=5)
        
    def start_chart_animation(self):
        """Start the chart animation for real-time updates."""
        def update_mini_chart():
            if not self.is_running:
                return
                
            try:
                # Update mini chart with recent data
                if len(self.stress_history) > 0:
                    recent_data = list(self.stress_history)[-30:]  # Last 30 points
                    recent_times = list(self.timestamps)[-30:]
                    
                    if len(recent_times) > 0:
                        # Convert timestamps to seconds from start
                        start_time = recent_times[0]
                        x_data = [(t - start_time) for t in recent_times]
                        
                        self.mini_ax.clear()
                        self.mini_ax.plot(x_data, recent_data, 'b-', linewidth=2)
                        self.mini_ax.set_title("Stress Level Trend (Last 30 seconds)")
                        self.mini_ax.set_ylabel("Stress Score")
                        self.mini_ax.set_ylim(0, 1)
                        self.mini_ax.grid(True, alpha=0.3)
                        
                        # Color background based on current stress level
                        current_stress = recent_data[-1] if recent_data else 0
                        if current_stress > 0.6:
                            self.mini_ax.set_facecolor('#ffe6e6')  # Light red
                        elif current_stress > 0.3:
                            self.mini_ax.set_facecolor('#fff2e6')  # Light orange
                        else:
                            self.mini_ax.set_facecolor('#e6ffe6')  # Light green
                        
                        self.mini_canvas.draw()
            except Exception as e:
                print(f"Mini chart update error: {e}")
            
            # Schedule next update
            if self.is_running:
                self.root.after(1000, update_mini_chart)  # Update every second
        
        # Start the animation
        self.root.after(1000, update_mini_chart)
    
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
    
    def data_recording_loop(self):
        """Data recording loop for session data collection."""
        while self.is_running:
            try:
                if self.current_metrics['face_detected']:
                    # Record current metrics with timestamp
                    data_point = {
                        'timestamp': time.time(),
                        'datetime': datetime.now().isoformat(),
                        'stress_score': self.current_metrics['stress_score'],
                        'stress_level': self.current_metrics['stress_level'],
                        'blink_rate': self.current_metrics['blink_rate'],
                        'expression': self.current_metrics['expression'],
                        'action_units': self.current_metrics.get('action_units', {})
                    }
                    
                    self.session_data.append(data_point)
                    
                    # Update historical data for charts
                    self.stress_history.append(self.current_metrics['stress_score'])
                    self.blink_history.append(self.current_metrics['blink_rate'])
                    self.expression_history.append(self.current_metrics['expression'])
                    self.timestamps.append(time.time())
                
                time.sleep(1)  # Record every second
                
            except Exception as e:
                print(f"Data recording error: {str(e)}")
                time.sleep(1)
    
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
                'action_units': expression_result.get('action_units', {}),
                'timestamp': time.time()
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
        """Update the enhanced metrics display."""
        try:
            if not self.root:
                return
            
            # Update face detection status
            face_status = "Face Detected" if self.current_metrics['face_detected'] else "No Face"
            self.face_status_var.set(face_status)
            
            if self.current_metrics['face_detected']:
                self.face_status_label.configure(foreground='green')
            else:
                self.face_status_label.configure(foreground='red')
            
            # Update expression
            self.expression_var.set(self.current_metrics.get('expression', 'neutral').title())
            
            # Update blink rate
            blink_rate = self.current_metrics.get('blink_rate', 0.0)
            self.blink_rate_var.set(f"{blink_rate:.1f} /min")
            
            # Update stress score and gauge
            stress_score = self.current_metrics.get('stress_score', 0.0)
            stress_level = self.current_metrics.get('stress_level', 'low')
            
            self.stress_score_var.set(f"{stress_score:.3f}")
            self.stress_level_var.set(stress_level.title())
            self.stress_gauge_var.set(stress_score * 100)  # Convert to percentage
            
            # Color code stress level
            if stress_level in ['high', 'very_high']:
                self.stress_level_label.configure(foreground='red')
            elif stress_level == 'moderate':
                self.stress_level_label.configure(foreground='orange')
            else:
                self.stress_level_label.configure(foreground='green')
            
            # Update session duration
            duration = datetime.now() - self.session_start_time
            duration_str = str(duration).split('.')[0]  # Remove microseconds
            self.session_duration_var.set(duration_str)
            
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
                    if au_name in self.au_progressbars:
                        progress, label = self.au_progressbars[au_name]
                        label.configure(text=f"{value*100:.1f}%")
            
            # Update status
            if self.current_metrics['face_detected']:
                self.status_var.set(f"Analyzing - {stress_level.title()} Stress - {len(self.session_data)} data points")
            else:
                self.status_var.set("Ready - No face detected")
                
        except Exception as e:
            print(f"Update metrics error: {str(e)}")
    
    def refresh_charts(self):
        """Refresh the historical charts with current data."""
        try:
            if not self.canvas or not self.figure:
                return
            
            # Get time range
            time_range = self.time_range_var.get()
            
            # Filter data based on time range
            current_time = time.time()
            if time_range == "Last 1 minute":
                cutoff_time = current_time - 60
            elif time_range == "Last 5 minutes":
                cutoff_time = current_time - 300
            elif time_range == "Last 10 minutes":
                cutoff_time = current_time - 600
            else:  # Full Session
                cutoff_time = 0
            
            # Filter data
            filtered_indices = [i for i, t in enumerate(self.timestamps) if t >= cutoff_time]
            
            if not filtered_indices:
                return
            
            filtered_times = [self.timestamps[i] for i in filtered_indices]
            filtered_stress = [self.stress_history[i] for i in filtered_indices]
            filtered_blink = [self.blink_history[i] for i in filtered_indices]
            filtered_expressions = [self.expression_history[i] for i in filtered_indices]
            
            # Convert timestamps to minutes from start
            if filtered_times:
                start_time = filtered_times[0]
                x_data = [(t - start_time) / 60 for t in filtered_times]  # Convert to minutes
                
                # Clear and update stress chart
                self.stress_ax.clear()
                self.stress_ax.plot(x_data, filtered_stress, 'b-', linewidth=2)
                self.stress_ax.set_title("Stress Level Over Time")
                self.stress_ax.set_ylabel("Stress Score")
                self.stress_ax.set_xlabel("Time (minutes)")
                self.stress_ax.grid(True, alpha=0.3)
                self.stress_ax.set_ylim(0, 1)
                
                # Clear and update blink rate chart
                self.blink_ax.clear()
                self.blink_ax.plot(x_data, filtered_blink, 'g-', linewidth=2)
                self.blink_ax.set_title("Blink Rate Over Time")
                self.blink_ax.set_ylabel("Blinks/min")
                self.blink_ax.set_xlabel("Time (minutes)")
                self.blink_ax.grid(True, alpha=0.3)
                
                # Clear and update expression distribution
                self.expression_ax.clear()
                if filtered_expressions:
                    from collections import Counter
                    expression_counts = Counter(filtered_expressions)
                    expressions = list(expression_counts.keys())
                    counts = list(expression_counts.values())
                    
                    colors = ['green' if exp == 'neutral' else 'red' if exp == 'angry' 
                             else 'blue' if exp == 'sad' else 'orange' for exp in expressions]
                    
                    bars = self.expression_ax.bar(expressions, counts, color=colors, alpha=0.7)
                    self.expression_ax.set_title("Expression Distribution")
                    self.expression_ax.set_ylabel("Frequency")
                    self.expression_ax.tick_params(axis='x', rotation=45)
                
                # Adjust layout and redraw
                self.figure.tight_layout()
                self.canvas.draw()
            
        except Exception as e:
            print(f"Chart refresh error: {str(e)}")
    
    def export_csv(self):
        """Export session data to CSV file."""
        try:
            if not self.session_data:
                messagebox.showwarning("No Data", "No session data to export.")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Session Data as CSV"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['datetime', 'timestamp', 'stress_score', 'stress_level', 
                                'blink_rate', 'expression', 'AU12', 'AU15', 'AU4', 'jaw_clench']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for data_point in self.session_data:
                        row = {
                            'datetime': data_point['datetime'],
                            'timestamp': data_point['timestamp'],
                            'stress_score': data_point['stress_score'],
                            'stress_level': data_point['stress_level'],
                            'blink_rate': data_point['blink_rate'],
                            'expression': data_point['expression'],
                            'AU12': data_point['action_units'].get('AU12', 0),
                            'AU15': data_point['action_units'].get('AU15', 0),
                            'AU4': data_point['action_units'].get('AU4', 0),
                            'jaw_clench': data_point['action_units'].get('JAW_CLENCH', 0)
                        }
                        writer.writerow(row)
                
                messagebox.showinfo("Export Successful", f"Data exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {str(e)}")
    
    def export_json(self):
        """Export session data to JSON file."""
        try:
            if not self.session_data:
                messagebox.showwarning("No Data", "No session data to export.")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Session Data as JSON"
            )
            
            if filename:
                export_data = {
                    'session_info': {
                        'start_time': self.session_start_time.isoformat(),
                        'export_time': datetime.now().isoformat(),
                        'total_data_points': len(self.session_data)
                    },
                    'data': self.session_data
                }
                
                with open(filename, 'w', encoding='utf-8') as jsonfile:
                    json.dump(export_data, jsonfile, indent=2)
                
                messagebox.showinfo("Export Successful", f"Data exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export JSON: {str(e)}")
    
    def export_charts(self):
        """Export current charts as PNG file."""
        try:
            if not self.figure:
                messagebox.showwarning("No Charts", "No charts to export.")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Export Charts as PNG"
            )
            
            if filename:
                self.refresh_charts()  # Make sure charts are up to date
                self.figure.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Export Successful", f"Charts exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export charts: {str(e)}")
    
    def update_session_stats(self):
        """Update the session statistics display."""
        try:
            if not self.session_data:
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(tk.END, "No session data available.")
                return
            
            # Calculate statistics
            stress_scores = [d['stress_score'] for d in self.session_data]
            blink_rates = [d['blink_rate'] for d in self.session_data]
            expressions = [d['expression'] for d in self.session_data]
            
            # Expression counts
            from collections import Counter
            expression_counts = Counter(expressions)
            
            # Stress level analysis
            stress_levels = [d['stress_level'] for d in self.session_data]
            stress_level_counts = Counter(stress_levels)
            
            # Create statistics text
            stats_text = f"""
SESSION STATISTICS
{'='*50}

Session Duration: {datetime.now() - self.session_start_time}
Total Data Points: {len(self.session_data)}
Data Collection Rate: {len(self.session_data) / max(1, (datetime.now() - self.session_start_time).total_seconds()) * 60:.1f} points/minute

STRESS ANALYSIS:
{'-'*30}
Average Stress Score: {np.mean(stress_scores):.3f}
Maximum Stress Score: {max(stress_scores):.3f}
Minimum Stress Score: {min(stress_scores):.3f}
Standard Deviation: {np.std(stress_scores):.3f}

Stress Level Distribution:
"""
            
            for level, count in stress_level_counts.most_common():
                percentage = (count / len(stress_levels)) * 100
                stats_text += f"  {level.title()}: {count} ({percentage:.1f}%)\n"
            
            stats_text += f"""

BLINK ANALYSIS:
{'-'*30}
Average Blink Rate: {np.mean(blink_rates):.1f} blinks/min
Maximum Blink Rate: {max(blink_rates):.1f} blinks/min
Minimum Blink Rate: {min(blink_rates):.1f} blinks/min

EXPRESSION ANALYSIS:
{'-'*30}
Most Common Expression: {expression_counts.most_common(1)[0][0].title()}

Expression Distribution:
"""
            
            for expression, count in expression_counts.most_common():
                percentage = (count / len(expressions)) * 100
                stats_text += f"  {expression.title()}: {count} ({percentage:.1f}%)\n"
            
            # High stress periods
            high_stress_periods = sum(1 for score in stress_scores if score > 0.6)
            stats_text += f"""

HIGH STRESS ANALYSIS:
{'-'*30}
High Stress Periods (>0.6): {high_stress_periods} ({(high_stress_periods/len(stress_scores)*100):.1f}%)
Time in High Stress: {high_stress_periods} seconds

RECOMMENDATIONS:
{'-'*30}
"""
            
            avg_stress = np.mean(stress_scores)
            if avg_stress > 0.6:
                stats_text += "• High average stress detected. Consider taking regular breaks.\n"
                stats_text += "• Practice deep breathing exercises.\n"
                stats_text += "• Consider adjusting your work environment.\n"
            elif avg_stress > 0.3:
                stats_text += "• Moderate stress levels detected.\n"
                stats_text += "• Monitor stress throughout the day.\n"
                stats_text += "• Take short breaks when stress increases.\n"
            else:
                stats_text += "• Good stress management observed.\n"
                stats_text += "• Continue current practices.\n"
            
            # Update the text widget
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, stats_text)
            
        except Exception as e:
            print(f"Statistics update error: {str(e)}")
    
    def start_recording(self):
        """Start data recording (placeholder - already recording)."""
        messagebox.showinfo("Recording", "Data recording is already active.")
    
    def stop_recording(self):
        """Stop data recording and export data."""
        if self.session_data:
            result = messagebox.askyesno("Stop Recording", 
                                       f"Stop recording and export {len(self.session_data)} data points?")
            if result:
                self.export_csv()
        else:
            messagebox.showinfo("No Data", "No data recorded in this session.")
    
    def reset_metrics(self):
        """Reset all tracking metrics."""
        try:
            self.eye_tracker.reset_metrics()
            if hasattr(self.expression_analyzer, 'reset_history'):
                self.expression_analyzer.reset_history()
            
            # Clear historical data
            self.stress_history.clear()
            self.blink_history.clear()
            self.expression_history.clear()
            self.timestamps.clear()
            self.session_data.clear()
            
            # Reset session start time
            self.session_start_time = datetime.now()
            
            # Clear charts
            if self.figure:
                for ax in [self.stress_ax, self.blink_ax, self.expression_ax]:
                    ax.clear()
                    ax.grid(True, alpha=0.3)
                self.canvas.draw()
            
            messagebox.showinfo("Reset Complete", "All metrics and data have been reset.")
            
        except Exception as e:
            print(f"Reset error: {str(e)}")
    
    def calibrate(self):
        """Start calibration process."""
        try:
            threshold = self.eye_tracker.calibrate_threshold()
            self.eye_tracker.ear_threshold = threshold
            messagebox.showinfo("Calibration Complete", 
                              f"Calibration completed.\nNew EAR threshold: {threshold:.3f}")
        except Exception as e:
            messagebox.showerror("Calibration Error", f"Calibration failed: {str(e)}")
    
    def on_closing(self):
        """Handle window closing event."""
        if self.session_data:
            result = messagebox.askyesnocancel("Save Data", 
                                             f"Save session data ({len(self.session_data)} points) before closing?")
            if result is True:  # Yes
                self.export_json()
            elif result is None:  # Cancel
                return  # Don't close
        
        self.is_running = False
        if self.root:
            self.root.destroy()
    
    def cleanup(self):
        """Clean up resources."""
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
