import subprocess
import threading
import asyncio

from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon

from plugin_manager import BasePlugin

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

        self.btn = QPushButton()
        self.btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout_btn = QVBoxLayout(self.btn)
        layout_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_btn.addWidget(self.icon)

        self.text = QLabel("Network")
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setStyleSheet("color: white; font-size: 14px;")
        layout_btn.addWidget(self.text)

        self.btn.clicked.connect(self.toggle_network)

        self.btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60,60,60,180);
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(80,80,80,200);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.btn)

        self.update_status()
        self.setup_dbus_monitoring()

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
            self.text.setText("Enable")
            print("Disabled")  
        elif self.active_type is None:
            self.text.setText("No network")
            print("No Network")
        else:
            self.text.setText("Disable")
            print("Enabled")
            
        self.update_icon()

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

    # ---------------- ICON ----------------

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_icon()

    def update_icon(self):
        size = min(self.width(), self.height()) // 2
        icon = self.select_icon()
        self.icon.setPixmap(icon.pixmap(QSize(size, size)))

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
