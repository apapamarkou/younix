from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QSize
from PyQt6.QtGui import QIcon
import subprocess
import json
from plugin_manager import BasePlugin, PluginSize

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
        
        self.text_label = QLabel("")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet("background: transparent; color: white;")
        
        # Wrapper for horizontal layout
        self.h_widget = QWidget()
        self.h_widget.setStyleSheet("background: transparent;")
        self.h_layout = QHBoxLayout(self.h_widget)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.main_widget)
        
        self.current_size = PluginSize.NORMAL
        self.update_text = ""
        
        self.update_updates()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_updates)
        self.timer.start(600000)
    
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
        
        icon = QIcon.fromTheme("update-none")
        if icon.isNull():
            icon = QIcon.fromTheme("system-software-update")
        
        if self.current_size == PluginSize.SMALL:
            # Only icon
            pixmap = icon.pixmap(QSize(32, 32))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            
        elif self.current_size == PluginSize.NORMAL:
            # Icon and text vertically
            pixmap = icon.pixmap(QSize(32, 32))
            self.icon_label.setPixmap(pixmap)
            self.text_label.setStyleSheet("background: transparent; color: white; font-size: 10px;")
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.text_label)
            
        elif self.current_size == PluginSize.MEDIUM:
            pixmap = icon.pixmap(QSize(32, 32))
            self.icon_label.setPixmap(pixmap)
            self.text_label.setStyleSheet("background: transparent; color: white; font-size: 14px;")
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.text_label)
            
        elif self.current_size == PluginSize.LARGE:
            # Icon left and text right bigger horizontally
            pixmap = icon.pixmap(QSize(48, 48))
            self.icon_label.setPixmap(pixmap)
            self.text_label.setStyleSheet("background: transparent; color: white; font-size: 12px;")
            self.h_layout.addWidget(self.icon_label)
            self.h_layout.addWidget(self.text_label)
            self.content_layout.addWidget(self.h_widget)
            
        elif self.current_size == PluginSize.HUGE:
            # Icon and text vertically bigger
            pixmap = icon.pixmap(QSize(64, 64))
            self.icon_label.setPixmap(pixmap)
            self.text_label.setStyleSheet("background: transparent; color: white; font-size: 14px;")
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.text_label)
    
    def on_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            subprocess.Popen(["ysystemupdate", "-t"])
    
    def update_updates(self):
        self.worker = UpdatesWorker()
        self.worker.updates_updated.connect(self.set_update_text)
        self.worker.start()
    
    def set_update_text(self, text):
        if text:
            self.update_text = f"{text} new updates"
        else:
            self.update_text = "Up to date."
        self.text_label.setText(self.update_text)
        self.update_display()