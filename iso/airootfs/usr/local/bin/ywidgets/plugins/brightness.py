from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import subprocess
from plugin_manager import BasePlugin, PluginSize

class Plugin(BasePlugin):
    plugin_name = "Brightness"
    plugin_title = "Brightness Control"
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
        
        self.content_layout = QVBoxLayout(self.main_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
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
        
        self.brightness_label = QLabel("80%")
        self.brightness_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brightness_label.setStyleSheet("color: white; font-size: 14px;")
        
        # Wrapper for horizontal layout
        self.h_widget = QWidget()
        self.h_widget.setStyleSheet("background: transparent;")
        self.h_layout = QHBoxLayout(self.h_widget)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.main_widget)
        
        self.current_size = PluginSize.NORMAL
        self.current_brightness = 80
        
        self.update_display()
    
    def on_size_changed(self, size_class: PluginSize):
        self.current_size = size_class
        self.update_display()
    
    def update_display(self):
        # Clear existing widgets from layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Clear horizontal layout too
        while self.h_layout.count():
            item = self.h_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        icon = QIcon.fromTheme("brightness-high")
        if icon.isNull():
            icon = QIcon.fromTheme("display-brightness")
        
        if self.current_size == PluginSize.SMALL:
            # Only icon (32x32)
            pixmap = icon.pixmap(QSize(32, 32))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            
        elif self.current_size == PluginSize.MEDIUM:
            # Icon (44x44) and slider vertically
            pixmap = icon.pixmap(QSize(44, 44))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.slider)
            
        elif self.current_size == PluginSize.LARGE:
            # Large icon (48x48) on left, slider on right horizontally
            pixmap = icon.pixmap(QSize(48, 48))
            self.icon_label.setPixmap(pixmap)
            self.h_layout.addWidget(self.icon_label)
            self.h_layout.addWidget(self.slider)
            self.content_layout.addWidget(self.h_widget)
            
        elif self.current_size == PluginSize.HUGE:
            # Icon (64x64) on top, slider middle, percentage bottom
            pixmap = icon.pixmap(QSize(64, 64))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.slider)
            self.content_layout.addWidget(self.brightness_label)
            
        else:  # NORMAL
            # Default: icon and slider
            pixmap = icon.pixmap(QSize(32, 32))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.slider)
                    
        self.icon_label.setStyleSheet("background: transparent;")
    
    def set_brightness(self, value):
        self.current_brightness = value
        self.brightness_label.setText(f"{value}%")
        subprocess.run(["brightnessctl", "set", f"{value}%"])