import subprocess
import threading
import asyncio

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon

from plugin_manager import BasePlugin, PluginSize

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType


class Plugin(BasePlugin):
    plugin_name = "Network"
    plugin_title = "Network Manager"
    size_default = "Normal"
    grid_span = (2, 2)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.network_enabled = False
        self.active_type = None  # wired / wireless / none

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
        
        self.text_label = QLabel("Network")
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
        
        self.update_status()
        self.setup_dbus_monitoring()
    
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
        
        icon = self.select_icon()
        
        if self.current_size == PluginSize.SMALL:
            # Only icon
            pixmap = icon.pixmap(QSize(32, 32))
            self.icon_label.setPixmap(pixmap)
            self.content_layout.addWidget(self.icon_label)
            
        elif self.current_size == PluginSize.NORMAL:
            # Icon and text vertically
            pixmap = icon.pixmap(QSize(44, 44))
            self.icon_label.setPixmap(pixmap)
            self.text_label.setStyleSheet("background: transparent; color: white; font-size: 12px;")
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.text_label)
            
        elif self.current_size == PluginSize.MEDIUM:
            # Icon left and text right horizontally
            pixmap = icon.pixmap(QSize(44, 44))
            self.icon_label.setPixmap(pixmap)
            self.text_label.setStyleSheet("background: transparent; color: white; font-size: 12px;")
            self.h_layout.addWidget(self.icon_label)
            self.h_layout.addWidget(self.text_label)
            self.content_layout.addWidget(self.h_widget)
            
        elif self.current_size == PluginSize.LARGE:
            # Icon left and text right bigger horizontally
            pixmap = icon.pixmap(QSize(64, 64))
            self.icon_label.setPixmap(pixmap)
            self.text_label.setStyleSheet("background: transparent; color: white; font-size: 12px;")
            self.h_layout.addWidget(self.icon_label)
            self.h_layout.addWidget(self.text_label)
            self.content_layout.addWidget(self.h_widget)
            
        elif self.current_size == PluginSize.HUGE:
            # Icon and text vertically bigger
            pixmap = icon.pixmap(QSize(64, 64))
            self.icon_label.setPixmap(pixmap)
            self.text_label.setStyleSheet("background: transparent; color: white; font-size: 12px;")
            self.content_layout.addWidget(self.icon_label)
            self.content_layout.addWidget(self.text_label)
    
    def on_click(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_network()

    # ---------------- NETWORK CONTROL ----------------

    def toggle_network(self):
        try:
            result = subprocess.run(
                ["nmcli", "networking"],
                capture_output=True, text=True
            )
            if "enabled" in result.stdout:
                subprocess.run(["nmcli", "networking", "off"])
            else:
                subprocess.run(["nmcli", "networking", "on"])
        except Exception:
            subprocess.Popen(["nmtui"])

    # ---------------- STATUS ----------------

    def update_status(self):
        self.network_enabled = self.is_network_enabled()
        self.active_type = self.get_active_connection_type()

        if not self.network_enabled:
            self.text_label.setText("Enable")
        elif self.active_type is None:
            self.text_label.setText("No network")
        else:
            self.text_label.setText("Disable")
            
        self.update_display()

    def is_network_enabled(self):
        try:
            r = subprocess.run(
                ["nmcli", "networking"],
                capture_output=True, text=True
            )
            return "enabled" in r.stdout
        except Exception:
            return False

    def get_active_connection_type(self):
        try:
            r = subprocess.run(
                ["nmcli", "-t", "-f", "TYPE", "connection", "show", "--active"],
                capture_output=True, text=True
            )
            out = r.stdout.strip()
            if not out:
                return None
            if "ethernet" in out:
                return "wired"
            if "wifi" in out:
                return "wireless"
            return None
        except Exception:
            return None

    def select_icon(self):
        if not self.network_enabled:
            return QIcon.fromTheme("network-offline")
        if self.active_type == "wired":
            return QIcon.fromTheme("network-wired-activated")
        if self.active_type == "wireless":
            return QIcon.fromTheme("network-wireless-connected")
        return QIcon.fromTheme("network-error")

    # ---------------- D-BUS ----------------

    def setup_dbus_monitoring(self):
        async def monitor():
            bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

            introspection = await bus.introspect(
                "org.freedesktop.NetworkManager",
                "/org/freedesktop/NetworkManager"
            )

            nm = bus.get_proxy_object(
                "org.freedesktop.NetworkManager",
                "/org/freedesktop/NetworkManager",
                introspection
            )


            props = nm.get_interface("org.freedesktop.DBus.Properties")

            def on_props_changed(interface, changed, invalidated):
                if interface == "org.freedesktop.NetworkManager":
                    QTimer.singleShot(0, self.update_status)

            props.on_properties_changed(on_props_changed)

            await asyncio.Future()  # keep alive

        threading.Thread(
            target=lambda: asyncio.run(monitor()),
            daemon=True
        ).start()
