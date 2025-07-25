"""
Configuration Manager Module
Handles application configuration settings.
"""

class ConfigManager:
    """
    Manages application configuration.
    """
    
    def __init__(self):
        # Initialize configuration manager
        self.config = {
            'camera_id': 0,
            'window_width': 800,
            'window_height': 600,
            'fps': 30
        }
    
    def get(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value."""
        self.config[key] = value
