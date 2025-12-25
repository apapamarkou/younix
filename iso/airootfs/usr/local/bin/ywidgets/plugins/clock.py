from PyQt6.QtWidgets import QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon
from datetime import datetime
import subprocess
from plugin_manager import BasePlugin, PluginSize

class Plugin(BasePlugin):
    plugin_name = "Clock"
    plugin_title = "Digital Clock"
    size_default = "Normal"
    grid_span = (2, 2)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            color: white;
            background-color: rgba(60, 60, 60, 180);
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
        """)
        self.time_label.mousePressEvent = self.on_click
        
        # Add hover effect
        self.time_label.enterEvent = lambda e: self.time_label.setStyleSheet("""
            color: white;
            background-color: rgba(80, 80, 80, 200);
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
        """)
        self.time_label.leaveEvent = lambda e: self.time_label.setStyleSheet("""
            color: white;
            background-color: rgba(60, 60, 60, 180);
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.time_label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        
        self.current_size = PluginSize.NORMAL
        self.update_time()
    
    def on_size_changed(self, size_class: PluginSize):
        self.current_size = size_class
        self.update_time()
    
    def update_time(self):
        now = datetime.now()
        
        if self.current_size == PluginSize.SMALL:
            icon = QIcon.fromTheme("view-calendar")
            pixmap = icon.pixmap(QSize(32, 32))
            self.time_label.setPixmap(pixmap)
            self.time_label.setText("")
        elif self.current_size == PluginSize.NORMAL:
            self.time_label.clear()
            date_text = now.strftime("%d %b %y")
            time_text = now.strftime("%H:%M:%S")
            text = f'<span style="color: gray;">{date_text}</span><br><span style="color: white;">{time_text}</span>'
            self.time_label.setText(text)
        elif self.current_size == PluginSize.MEDIUM:
            self.time_label.clear()
            date_text = now.strftime("%a %d %b %y")
            time_text = now.strftime("%H:%M:%S")
            text = f'<span style="color: grey;">{date_text}</span><br><span style="color: white;">{time_text}</span>'
            self.time_label.setText(text)
        elif self.current_size == PluginSize.LARGE:
            self.time_label.clear()
            date_line1 = now.strftime("%A %d")
            date_line2 = now.strftime("%B %Y")
            time_text = now.strftime("%H:%M:%S")
            text = f'<span style="color: grey;">{date_line1}</span><br><span style="color: grey;">{date_line2}</span><br><span style="color: white;">{time_text}</span>'
            self.time_label.setText(text)
        elif self.current_size == PluginSize.HUGE:
            self.time_label.clear()
            icon = QIcon.fromTheme("view-calendar")
            pixmap = icon.pixmap(QSize(48, 48))
            date_line1 = now.strftime("%A %d")
            date_line2 = now.strftime("%B %Y")
            time_text = now.strftime("%H:%M:%S")
            icon_html = f'<img src="data:image/png;base64,{self.pixmap_to_base64(pixmap)}" width="24" height="24"><br>'
            text = f'{icon_html}<span style="color: grey;">{date_line1}</span><br><span style="color: grey;">{date_line2}</span><br><span style="color: white;">{time_text}</span>'
            self.time_label.setText(text)
        else:  
            self.time_label.clear()
            text = now.strftime("%H:%M:%S")
            self.time_label.setText(text)
    
    def on_click(self, event):
        subprocess.Popen(["ycalendar"])
    
    def pixmap_to_base64(self, pixmap):
        from PyQt6.QtCore import QBuffer, QIODevice
        import base64
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        return base64.b64encode(buffer.data()).decode()