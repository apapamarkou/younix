from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
import subprocess
from plugin_manager import BasePlugin

class Plugin(BasePlugin):
    plugin_name = "Bluetooth"
    plugin_title = "Bluetooth Manager"
    size_default = "Normal"
    grid_span = (2, 2)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.btn = QPushButton()
        self.btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(self.btn)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.setStyleSheet("background: transparent;")
        
        self.text = QLabel("Activating...")
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setStyleSheet("color: white; font-size: 14px; background: transparent;")
        
        # Show disabled icon initially
        size = 32
        self.icon.setPixmap(QIcon.fromTheme("bluetooth-disabled").pixmap(QSize(size, size)))
        
        layout.addWidget(self.icon)
        layout.addWidget(self.text)
        
        self.btn.clicked.connect(self.toggle_bluetooth)
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
        
        # Lazy load status after a short delay
        QTimer.singleShot(3000, self.check_bluetooth_async)
        
        main = QVBoxLayout(self)
        main.setContentsMargins(2, 2, 2, 2)
        main.addWidget(self.btn)

    def toggle_bluetooth(self):
        self.text.setText("Bluetooth")
        subprocess.Popen(["blueman-manager"])
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = min(self.width(), self.height()) - 24
        self.icon.setPixmap(QIcon.fromTheme("bluetooth-disabled").pixmap(QSize(size, size)))
    
    def check_bluetooth_async(self):
        # Just show static bluetooth text and icon
        self.text.setText("Bluetooth")
        size = min(self.width(), self.height()) // 2
        self.icon.setPixmap(QIcon.fromTheme("bluetooth-disabled").pixmap(QSize(size, size)))