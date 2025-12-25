from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import subprocess
from plugin_manager import BasePlugin, PluginSize

class Plugin(BasePlugin):
    plugin_name = "Nightlight"
    plugin_title = "Night Light"
    size_default = "Normal"
    grid_span = (2, 2)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(60, 60, 60, 180);
                border-radius: 10px;
                color: white;
            }
            QWidget:hover {
                background-color: rgba(80, 80, 80, 200);
            }
        """)
        self.main_widget.mousePressEvent = self.on_click
        
        self.content_layout = QVBoxLayout(self.main_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent;")
        
        self.title_label = QLabel("NightLight")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("background: transparent; color: white; font-weight: bold;")
        
        self.status_label = QLabel("Enable")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("background: transparent; color: white;")
        
        # Wrapper for horizontal layout
        self.h_widget = QWidget()
        self.h_widget.setStyleSheet("background: transparent;")
        self.h_layout = QHBoxLayout(self.h_widget)
        
        # Wrapper for text (title + status)
        self.text_widget = QWidget()
        self.text_widget.setStyleSheet("background: transparent;")
        self.text_layout = QVBoxLayout(self.text_widget)
        self.text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.main_widget)
        
        self.current_size = PluginSize.NORMAL
        self.is_enabled = False
        
        self.update_status()
    
    def on_size_changed(self, size_class: PluginSize):
        self.current_size = size_class
        self.update_display()
    
    def update_display(self):
        # Clear existing widgets from layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Clear horizontal layout
        while self.h_layout.count():
            item = self.h_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Clear text layout
        while self.text_layout.count():
            item = self.text_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        icon = QIcon.fromTheme("weather-clear-night" if self.is_enabled else "weather-clear")
        if icon.isNull():
            icon = QIcon.fromTheme("night-light")
        
        if self.current_size == PluginSize.SMALL:
            # Only icon
            pixmap = icon.pixmap(QSize(32, 32))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            
        elif self.current_size == PluginSize.NORMAL:
            # "Nightlight" then Icon vertically
            self.title_label.setStyleSheet("background: transparent; color: white; font-weight: bold; font-size: 14px;")
            pixmap = icon.pixmap(QSize(32, 32))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.title_label)
            self.content_layout.addWidget(self.icon_label)
            
        elif self.current_size == PluginSize.MEDIUM:
            # Icon then text horizontally. Text: "NightLight" (bold) then "Enable/Disable" vertically
            pixmap = icon.pixmap(QSize(24, 24))
            self.icon_label.setPixmap(pixmap)
            self.title_label.setStyleSheet("background: transparent; color: white; font-weight: bold; font-size: 12px;")
            self.status_label.setStyleSheet("background: transparent; color: white; font-size: 11px;")
            self.text_layout.addWidget(self.title_label)
            self.text_layout.addWidget(self.status_label)
            self.h_layout.addWidget(self.icon_label)
            self.h_layout.addWidget(self.text_widget)
            self.content_layout.addWidget(self.h_widget)
            
        elif self.current_size == PluginSize.LARGE:
            # Icon then text horizontally. Text: "NightLight" (bold) then "Enable/Disable" vertically bigger than MEDIUM
            pixmap = icon.pixmap(QSize(48, 48))
            self.icon_label.setPixmap(pixmap)
            self.title_label.setStyleSheet("background: transparent; color: white; font-weight: bold; font-size: 14px;")
            self.status_label.setStyleSheet("background: transparent; color: white; font-size: 14px;")
            self.text_layout.addWidget(self.title_label)
            self.text_layout.addWidget(self.status_label)
            self.h_layout.addWidget(self.icon_label)
            self.h_layout.addWidget(self.text_widget)
            self.content_layout.addWidget(self.h_widget)
            
        elif self.current_size == PluginSize.HUGE:
            # "NightLight" then icon then "Enable/Disable" vertically
            self.title_label.setStyleSheet("background: transparent; color: white; font-weight: bold; font-size: 24px;")
            pixmap = icon.pixmap(QSize(64, 64))
            self.icon_label.setPixmap(pixmap)
            self.status_label.setStyleSheet("background: transparent; color: white; font-size: 20px;")
            self.content_layout.addWidget(self.title_label)
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.status_label)
    
    def on_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_nightlight()
    
    def toggle_nightlight(self):
        try:
            result = subprocess.run(["ycnightlight", "-c"], capture_output=True, text=True)
            if "enabled" in result.stdout.strip():
                subprocess.run(["ycnightlight", "-s", "off"])
            else:
                subprocess.run(["ycnightlight", "-s", "on"])
            self.update_status()
        except:
            pass
    
    def update_status(self):
        try:
            result = subprocess.run(["ycnightlight", "-c"], capture_output=True, text=True)
            self.is_enabled = "enabled" in result.stdout.strip()
            self.status_label.setText("Disable" if self.is_enabled else "Enable")
        except:
            self.is_enabled = False
            self.status_label.setText("Enable")
        
        self.update_display()