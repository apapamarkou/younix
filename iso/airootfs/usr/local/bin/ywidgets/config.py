import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "ywidgets"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data = self.load()
    
    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {
            "window": {"width": 400, "height": 600},
            "grid": {"columns": 4, "rows": 20},
            "plugins": {
                "enabled": ["Volume", "Brightness", "Network", "Nightlight", "Weather", "Settings", "Bluetooth", "Updates"],
                "positions": {
                    "Volume": {"row": 0, "col": 0},
                    "Brightness": {"row": 0, "col": 2},
                    "Network": {"row": 2, "col": 0},
                    "Nightlight": {"row": 2, "col": 2},
                    "Weather": {"row": 4, "col": 0},
                    "Settings": {"row": 6, "col": 0},
                    "Bluetooth": {"row": 6, "col": 2},
                    "Updates": {"row": 8, "col": 0}
                },
                "sizes": {}
            }
        }
    
    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_window_size(self):
        return self.data["window"]["width"], self.data["window"]["height"]
    
    def set_window_size(self, width, height):
        self.data["window"]["width"] = width
        self.data["window"]["height"] = height
        self.save()
    
    def get_enabled_plugins(self):
        return self.data.get("plugins", {}).get("enabled", [])
    
    def set_enabled_plugins(self, plugins):
        if "plugins" not in self.data:
            self.data["plugins"] = {"enabled": [], "positions": {}, "sizes": {}}
        self.data["plugins"]["enabled"] = plugins
        self.save()
    
    def get_plugin_position(self, plugin_name):
        return self.data.get("plugins", {}).get("positions", {}).get(plugin_name, {"row": 0, "col": 0})
    
    def set_plugin_position(self, plugin_name, row, col):
        if "plugins" not in self.data:
            self.data["plugins"] = {"enabled": [], "positions": {}, "sizes": {}}
        self.data["plugins"]["positions"][plugin_name] = {"row": row, "col": col}
        self.save()
    
    def get_plugin_size(self, plugin_name):
        return self.data.get("plugins", {}).get("sizes", {}).get(plugin_name, "Default")
    
    def set_plugin_size(self, plugin_name, size):
        if "plugins" not in self.data:
            self.data["plugins"] = {"enabled": [], "positions": {}, "sizes": {}}
        self.data["plugins"]["sizes"][plugin_name] = size
        self.save()
    
    def get_grid_config(self):
        return self.data.get("grid", {"columns": 4, "rows": 20})
    
    def get_enabled_plugins_list(self):
        return self.data.get("plugins", {}).get("enabled", [])
    
    def get_all_plugin_positions(self):
        return self.data.get("plugins", {}).get("positions", {})