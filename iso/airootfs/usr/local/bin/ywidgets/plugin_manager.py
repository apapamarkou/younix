from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
import importlib
import pkgutil
import plugins

class BasePlugin(QWidget):
    plugin_name = "Unnamed"
    plugin_title = "Unnamed Plugin"
    size_default = "Normal"
    grid_span = (2, 2)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
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
    instances = []
    for _, name, _ in pkgutil.iter_modules(plugins.__path__):
        module = importlib.import_module(f"plugins.{name}")
        if hasattr(module, "Plugin"):
            instances.append(module.Plugin(parent))
    return instances

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
        "Large": (2, 4),
        "Huge": (4, 4)
    }
    return sizes.get(size, (2, 2))