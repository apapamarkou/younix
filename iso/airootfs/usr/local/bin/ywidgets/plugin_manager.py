from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
import importlib
import pkgutil
import plugins
from enum import Enum

class PluginSize(Enum):
    SMALL = "Small"   # 1x1: Icon only
    NORMAL = "Normal" # 2x2: Icon + Label
    MEDIUM = "Medium" # 2x3: Icon + Date + Time
    LARGE = "Large"   # 2x4: Icon + Controls
    HUGE = "Huge"     # 4x4: Full detailed view

class BasePlugin(QWidget):
    plugin_name = "Unnamed"
    plugin_title = "Unnamed Plugin"
    size_default = "Normal"
    grid_span = (2, 2)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def on_size_changed(self, size_class: PluginSize):
        """Override this in your plugin to change UI layout."""
        pass
    
    def show_context_menu(self, position):
        # Find the main window (ControlCenter)
        parent = self.parent()
        while parent and not hasattr(parent, 'show_plugin_context_menu'):
            parent = parent.parent()
        if parent:
            parent.show_plugin_context_menu(position, self)
    
    def contextMenuEvent(self, event):
        self.show_context_menu(event.pos())
        event.accept()

def load_plugins(parent=None):
    # Cache plugins to prevent creating new instances on every call
    if not hasattr(load_plugins, '_cached_plugins') or load_plugins._cached_plugins is None:
        instances = []
        for _, name, _ in pkgutil.iter_modules(plugins.__path__):
            module = importlib.import_module(f"plugins.{name}")
            if hasattr(module, "Plugin"):
                instances.append(module.Plugin(parent))
        load_plugins._cached_plugins = instances
    return load_plugins._cached_plugins

def clear_plugin_cache():
    """Clear the plugin cache to force reload"""
    if hasattr(load_plugins, '_cached_plugins'):
        load_plugins._cached_plugins = None

def get_available_plugins():
    available = []
    for _, name, _ in pkgutil.iter_modules(plugins.__path__):
        module = importlib.import_module(f"plugins.{name}")
        if hasattr(module, "Plugin"):
            plugin_class = getattr(module, "Plugin")
            available.append({
                "name": getattr(plugin_class, "plugin_name", name),
                "title": getattr(plugin_class, "plugin_title", name),
                "module": name
            })
    return available

def get_size_span(size):
    sizes = {
        "Small": (1, 1),
        "Normal": (2, 2),
        "Medium": (2, 3),
        "Large": (2, 4),
        "Huge": (4, 4)
    }
    return sizes.get(size, (2, 2))