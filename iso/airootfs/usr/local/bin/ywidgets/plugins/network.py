from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon
import subprocess
from plugin_manager import BasePlugin

class Plugin(BasePlugin):
    plugin_name = "Network"
    plugin_title = "Network Manager"
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
        
        self.text = QLabel("Network")
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setStyleSheet("color: white; font-size: 14px; background: transparent;")
        btn_layout.addWidget(self.text)
        
        self.btn.clicked.connect(self.toggle_network)
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
        
        self.update_status()
    
    def toggle_network(self):
        try:
            result = subprocess.run(["nmcli", "networking"], capture_output=True, text=True)
            if "enabled" in result.stdout.strip():
                subprocess.run(["nmcli", "networking", "off"])
            else:
                subprocess.run(["nmcli", "networking", "on"])
            QTimer.singleShot(1000, self.update_status)
        except:
            subprocess.Popen(["nmtui"])
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = min(self.width(), self.height()) // 2
        self.update_icon_size(size)
    
    def update_icon_size(self, size):
        try:
            result = subprocess.run(["nmcli", "networking"], capture_output=True, text=True)
            if "enabled" not in result.stdout.strip():
                icon = QIcon.fromTheme("network-error")
                self.icon.setPixmap(icon.pixmap(QSize(size, size)))
                return
            
            # Check for active connections
            result = subprocess.run(["nmcli", "connection", "show", "--active"], capture_output=True, text=True)
            if not result.stdout.strip():
                icon = QIcon.fromTheme("network-error")
            else:
                # Check if wired or wireless
                if "ethernet" in result.stdout.lower():
                    icon = QIcon.fromTheme("network-wired-activated")
                else:
                    icon = QIcon.fromTheme("network-wireless-on")
            
            self.icon.setPixmap(icon.pixmap(QSize(size, size)))
        except:
            icon = QIcon.fromTheme("network-error")
            self.icon.setPixmap(icon.pixmap(QSize(size, size)))
    
    def update_status(self):
        try:
            result = subprocess.run(["nmcli", "networking"], capture_output=True, text=True)
            if "enabled" not in result.stdout.strip():
                self.text.setText("Enable")
                size = min(self.width(), self.height()) - 24 if self.width() > 0 else 32
                self.update_icon_size(size)
                return
            
            # Check for active connections
            result = subprocess.run(["nmcli", "connection", "show", "--active"], capture_output=True, text=True)
            if not result.stdout.strip():
                self.text.setText("No network.")
            else:
                self.text.setText("Disable")
            
            size = min(self.width(), self.height()) - 24 if self.width() > 0 else 32
            self.update_icon_size(size)
        except:
            self.text.setText("No network.")
            size = min(self.width(), self.height()) - 24 if self.width() > 0 else 32
            self.update_icon_size(size)