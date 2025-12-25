from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QSlider, QWidget
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon
import subprocess
import re
from plugin_manager import BasePlugin, PluginSize

class Plugin(BasePlugin):
    plugin_name = "Volume"
    plugin_title = "Volume Control"
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
        """)
        
        # Create single layout that stays alive
        self.content_layout = QVBoxLayout(self.main_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.mousePressEvent = self.on_icon_click
        self.icon_label.wheelEvent = self.on_icon_scroll
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.on_slider_change)
        self.slider.sliderReleased.connect(self.apply_volume)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #404040;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -4px 0;
            }
        """)
        
        self.volume_label = QLabel("50%")
        self.volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volume_label.setStyleSheet("color: white; font-size: 14px;")
        
        # Wrapper for horizontal layout
        self.h_widget = QWidget()
        self.h_layout = QHBoxLayout(self.h_widget)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.main_widget)
        
        self.current_size = PluginSize.NORMAL
        self.current_volume = 50
        self.is_muted = False
        
        # Get initial system volume and mute status
        self.get_initial_state()
        
        # Timer to check for external volume changes
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_volume_changes)
        self.update_timer.start(1000)  # Check every second
        
        self.update_display()
    
    def __del__(self):
        # Clean up timer when plugin is destroyed
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
    
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
        
        icon = QIcon.fromTheme("audio-volume-muted" if self.is_muted else "audio-volume-high")
        if icon.isNull():
            icon = QIcon.fromTheme("audio-card")
        
        if self.current_size == PluginSize.SMALL:
            # Only icon (32x32)
            pixmap = icon.pixmap(QSize(32, 32))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            
        elif self.current_size == PluginSize.MEDIUM:
            # Icon (24x24) and slider vertically
            pixmap = icon.pixmap(QSize(24, 24))
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
            # Icon (48x48) on top, slider middle, percentage bottom
            pixmap = icon.pixmap(QSize(48, 48))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.slider)
            self.content_layout.addWidget(self.volume_label)
            
        else:  # NORMAL
            # Default: icon and slider
            pixmap = icon.pixmap(QSize(32, 32))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.slider)
    
    def on_slider_change(self, value):
        self.current_volume = value
        self.volume_label.setText(f"{value}%")
    
    def apply_volume(self):
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{self.current_volume}%"])
    
    def get_initial_state(self):
        try:
            # Get volume
            out = subprocess.check_output(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], text=True)
            m = re.search(r'(\d+)%', out)
            if m:
                self.current_volume = int(m.group(1))
                self.slider.setValue(self.current_volume)
                self.volume_label.setText(f"{self.current_volume}%")
            
            # Get mute status
            out = subprocess.check_output(["pactl", "get-sink-mute", "@DEFAULT_SINK@"], text=True)
            self.is_muted = "yes" in out.lower()
        except:
            pass
    
    def check_volume_changes(self):
        try:
            # Get current system volume
            out = subprocess.check_output(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], text=True)
            m = re.search(r'(\d+)%', out)
            if m:
                sys_volume = int(m.group(1))
                if sys_volume != self.current_volume:
                    self.current_volume = sys_volume
                    self.slider.blockSignals(True)
                    self.slider.setValue(sys_volume)
                    self.slider.blockSignals(False)
                    self.volume_label.setText(f"{sys_volume}%")
            
            # Get mute status
            out = subprocess.check_output(["pactl", "get-sink-mute", "@DEFAULT_SINK@"], text=True)
            sys_muted = "yes" in out.lower()
            if sys_muted != self.is_muted:
                self.is_muted = sys_muted
                self.update_display()
        except:
            pass
    
    def on_icon_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Toggle mute
            self.is_muted = not self.is_muted
            self.update_display()
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
        elif event.button() == Qt.MouseButton.RightButton:
            # Open sound settings
            subprocess.Popen(["ycsound", "-t"])
    
    def on_icon_scroll(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            new_vol = min(100, self.current_volume + 5)
        else:
            new_vol = max(0, self.current_volume - 5)
        
        self.current_volume = new_vol
        self.slider.blockSignals(True)
        self.slider.setValue(new_vol)
        self.slider.blockSignals(False)
        self.volume_label.setText(f"{new_vol}%")
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{new_vol}%"])