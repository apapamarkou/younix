from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import subprocess
from plugin_manager import BasePlugin

class Plugin(BasePlugin):
    plugin_name = "Nightlight"
    plugin_title = "Night Light"
    size_default = "Normal"
    grid_span = (2, 2)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.btn = QPushButton()
        
        layout = QVBoxLayout(self.btn)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setStyleSheet("background: transparent;")
        
        self.text = QLabel("Night")
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setStyleSheet("color: white; font-size: 14px; background: transparent;")
        
        layout.addWidget(self.icon)
        layout.addWidget(self.text)
        
        self.btn.clicked.connect(self.toggle_nightlight)
        self.btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 60, 180);
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
        """)
        
        self.update_status()
        
        main = QVBoxLayout(self)
        main.setContentsMargins(2, 2, 2, 2)
        main.addWidget(self.btn)
        
        self.btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
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
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = min(self.width(), self.height()) // 2
        self.update_icon_size(size)
    
    def update_icon_size(self, size):
        try:
            result = subprocess.run(["ycnightlight", "-c"], capture_output=True, text=True)
            if "enabled" in result.stdout.strip():
                icon = QIcon.fromTheme("weather-clear-night")
            else:
                icon = QIcon.fromTheme("weather-clear")
            
            if not icon.isNull():
                self.icon.setPixmap(icon.pixmap(QSize(size, size)))
        except:
            pass
    
    def update_status(self):
        try:
            result = subprocess.run(["ycnightlight", "-c"], capture_output=True, text=True)
            if "enabled" in result.stdout.strip():
                self.text.setText("Disable")
            else:
                self.text.setText("Enable")
            
            size = min(self.width(), self.height()) // 2
            self.update_icon_size(size)
        except:
            self.text.setText("Night")