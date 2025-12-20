from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import subprocess
from plugin_manager import BasePlugin

class Plugin(BasePlugin):
    plugin_name = "Brightness"
    plugin_title = "Brightness Control"
    size_default = "Normal"
    grid_span = (2, 2)

    def __init__(self, parent=None):
        super().__init__(parent)

        
        self.btn = QPushButton()
        self.btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        btn_layout = QVBoxLayout(self.btn)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setStyleSheet("background: transparent;")
        btn_layout.addWidget(self.icon)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(10, 100)
        self.slider.setValue(80)
        self.slider.valueChanged.connect(self.set_brightness)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #404040;
                height: 10px;
                border-radius: 1px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 15px;
                height: 15px;
                border-radius: 4px;
                margin: -2px 0;
            }
        """)
        btn_layout.addWidget(self.slider)
        
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
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.btn)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = min(self.width(), self.height()) // 2
        self.icon.setPixmap(QIcon.fromTheme("brightness-high").pixmap(QSize(size, size)))
    
    def set_brightness(self, value):
        subprocess.run(["brightnessctl", "set", f"{value}%"])