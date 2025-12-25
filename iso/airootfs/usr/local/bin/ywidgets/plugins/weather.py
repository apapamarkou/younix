from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QSize
from PyQt6.QtGui import QIcon
import subprocess
from plugin_manager import BasePlugin, PluginSize

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
        
        self.weather_label = QLabel("Loading...")
        self.weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weather_label.setStyleSheet("background: transparent; color: white;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.main_widget)
        
        self.current_size = PluginSize.NORMAL
        self.weather_text = "Loading..."
        
        self.update_weather()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(300000)
        
        self.update_display()
    
    def on_size_changed(self, size_class: PluginSize):
        self.current_size = size_class
        self.update_display()
    
    def update_display(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        icon = QIcon.fromTheme("weather-clouds")
        if icon.isNull():
            icon = QIcon.fromTheme("weather-clear")
        
        if self.current_size == PluginSize.SMALL:
            pixmap = icon.pixmap(QSize(32, 32))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            
        elif self.current_size == PluginSize.NORMAL:
            pixmap = icon.pixmap(QSize(64, 64))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            
        elif self.current_size == PluginSize.MEDIUM:
            self.weather_label.setStyleSheet("color: white; font-size: 18px; background: transparent;")
            self.weather_label.setText(self.weather_text)
            self.content_layout.addWidget(self.weather_label)
            
        elif self.current_size == PluginSize.LARGE:
            self.weather_label.setStyleSheet("color: white; font-size: 24px; background: transparent;")
            self.weather_label.setText(self.weather_text)
            self.content_layout.addWidget(self.weather_label)
            
        elif self.current_size == PluginSize.HUGE:
            pixmap = icon.pixmap(QSize(64, 64))
            self.icon_label.setPixmap(pixmap)
            self.weather_label.setStyleSheet("color: white; font-size: 28px; background: transparent;")
            self.weather_label.setText(self.weather_text)
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.weather_label)
        
        self.icon_label.setStyleSheet("background: transparent;")
    
    def on_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            subprocess.Popen(["yweather", "-t"])
    
    def update_weather(self):
        self.worker = WeatherWorker()
        self.worker.weather_updated.connect(self.on_weather_updated)
        self.worker.start()
    
    def on_weather_updated(self, weather):
        self.weather_text = weather
        self.update_display()