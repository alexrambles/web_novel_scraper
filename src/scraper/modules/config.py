from typing import Dict, Any
import json
import os
from pathlib import Path

class Config:
    """Configuration manager for the scraper."""
    
    DEFAULT_CONFIG = {
        "output_dir": "books/",
        "log_level": "INFO",
        "request_timeout": 30,
        "retry_attempts": 3,
        "retry_delay": 5,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "download_delay": 2,  # Delay between requests in seconds
        "max_concurrent_downloads": 3,
        "supported_sites": [
            "novelupdates.com",
            "wuxiaworld.com",
            "royalroad.com"
        ]
    }
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(Path.home() / ".novel_scraper" / "config.json")
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default if not exists."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return {**self.DEFAULT_CONFIG, **json.load(f)}
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save current configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
        self.save_config()
