from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import subprocess
from plugin_manager import BasePlugin

class Plugin(BasePlugin):
    plugin_name = "Settings"
    plugin_title = "Control Center"
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
        
        self.text = QLabel("Control Center")
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setStyleSheet("color: white; font-size: 14px; background: transparent;")
        btn_layout.addWidget(self.text)
        
        self.btn.clicked.connect(lambda: subprocess.run(["ycc", "-t"]))
        self.btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn.customContextMenuRequested.connect(self.show_btn_context_menu)
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
    
    def show_btn_context_menu(self, position):
        # Find the main window (ControlCenter)
        parent = self.parent()
        while parent and not hasattr(parent, 'show_plugin_context_menu'):
            parent = parent.parent()
        if parent:
            parent.show_plugin_context_menu(position, self)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = min(self.width(), self.height()) // 2
        self.icon.setPixmap(QIcon.fromTheme("tools").pixmap(QSize(size, size)))