from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
import subprocess
from plugin_manager import BasePlugin

class WeatherWorker(QThread):
    weather_updated = pyqtSignal(str)
    
    def run(self):
        try:
            result = subprocess.run(["yweather", "-m"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.weather_updated.emit(result.stdout.strip())
            else:
                self.weather_updated.emit("N/A")
        except:
            self.weather_updated.emit("N/A")

class Plugin(BasePlugin):
    plugin_name = "Weather"
    plugin_title = "Weather Information"
    size_default = "Large"
    grid_span = (2, 4)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.btn = QPushButton("Loading...")
        self.btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.btn.clicked.connect(lambda: subprocess.Popen(["yweather", "-t"]))
        self.update_style()
        
        self.update_weather()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(300000)
        
        main = QVBoxLayout(self)
        main.setContentsMargins(2, 2, 2, 3)
        main.addWidget(self.btn)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_style()
    
    def update_style(self):
        font_size = max(12, min(self.width(), self.height()) // 4)
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(60, 60, 60, 180);
                border-radius: 10px;
                border: none;
                color: white;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: rgba(80, 80, 80, 200);
            }}
        """)
    
    def update_weather(self):
        self.worker = WeatherWorker()
        self.worker.weather_updated.connect(self.btn.setText)
        self.worker.start()