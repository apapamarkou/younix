from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QSize
from PyQt6.QtGui import QIcon
import subprocess
import json
from plugin_manager import BasePlugin

class UpdatesWorker(QThread):
    updates_updated = pyqtSignal(str)
    
    def run(self):
        try:
            result = subprocess.run(["ysystemupdate", "-m"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                data = json.loads(result.stdout.strip())
                text = data.get("text", "").strip()
                self.updates_updated.emit(text if text else "")
            else:
                self.updates_updated.emit("")
        except:
            self.updates_updated.emit("")

class Plugin(BasePlugin):
    plugin_name = "Updates"
    plugin_title = "System Updates"
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
        
        self.info = QLabel("")
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info.setStyleSheet("color: white; font-size: 14px; background: transparent;")
        btn_layout.addWidget(self.info)
        
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
        
        self.update_updates()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_updates)
        self.timer.start(600000)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = min(self.width(), self.height()) // 2
        self.icon.setPixmap(QIcon.fromTheme("update-none").pixmap(QSize(size, size)))
    
    def update_updates(self):
        self.worker = UpdatesWorker()
        self.worker.updates_updated.connect(self.set_update_text)
        self.worker.start()
    
    def set_update_text(self, text):
        if text:
            self.info.setText(f"{text} new updates")
        else:
            self.info.setText("Up to date.")