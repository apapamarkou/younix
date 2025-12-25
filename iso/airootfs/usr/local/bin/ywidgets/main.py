#!/usr/bin/env python3
import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QMenu, QSizePolicy, QScrollArea
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint, QPointF
from PyQt6.QtGui import QIcon, QPainter, QPen, QColor, QMouseEvent
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from plugin_manager import load_plugins, get_size_span, PluginSize, clear_plugin_cache
from config import Config

class OverlayWidget(QWidget):
    def __init__(self, control_center, parent=None):
        super().__init__(parent)
        self.control_center = control_center
        self.setMouseTracking(True)
        self.dragging = False
        self.drag_plugin_name = None
        self.hide()  # Hidden by default
        
    def show_overlay(self):
        self.setGeometry(self.parent().rect())
        self.show()
        self.raise_()
    
    def hide_overlay(self):
        self.hide()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Direct position on grid widget
            grid_pos = event.pos()
            
            # Find plugin under cursor
            plugin_name = self.control_center.get_plugin_under_cursor(grid_pos)
            if plugin_name:
                self.dragging = True
                self.drag_plugin_name = plugin_name
                self.control_center.start_drag_preview(plugin_name)
                event.accept()
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            # Direct position on grid widget
            grid_pos = event.pos()
            
            # Use grid widget parameters for consistent positioning
            cell_size = self.control_center.grid_widget.cell_size
            spacing = self.control_center.grid_widget.spacing
            
            new_col = max(0, grid_pos.x() // (cell_size + spacing))
            new_row = max(0, grid_pos.y() // (cell_size + spacing))
                
            self.control_center.update_drag_highlight(new_row, new_col)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            if self.drag_plugin_name:
                self.control_center.end_drag_preview(self.drag_plugin_name)
                self.drag_plugin_name = None
            event.accept()

class DraggablePlugin(QWidget):
    def __init__(self, plugin, control_center):
        super().__init__()
        self.plugin = plugin
        self.control_center = control_center
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(plugin)
        self.setLayout(layout)
        
        # Connect plugin update signals to repaint
        if hasattr(plugin, 'update'):
            original_update = plugin.update
            def update_with_repaint():
                original_update()
                self.update()
            plugin.update = update_with_repaint
        
        # Set initial edit mode state
        self.refresh_edit_mode()
    
    def refresh_edit_mode(self):
        if self.control_center.edit_mode:
            # Make plugin more transparent in edit mode
            self.plugin.setWindowOpacity(0.7)
        else:
            # Make plugin transparent in edit off mode
            self.plugin.setWindowOpacity(0.8)

    
class GridWidget(QWidget):
    def __init__(self, max_col, max_row, cell_size=48, spacing=2):
        super().__init__()
        self.max_col = max_col
        self.max_row = max_row
        self.cell_size = cell_size
        self.spacing = spacing
        self.highlight_row = -1
        self.highlight_col = -1
        
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )
    
    def set_highlight(self, row, col):
        self.highlight_row = row
        self.highlight_col = col
        self.update()
    
    def clear_highlight(self):
        self.highlight_row = -1
        self.highlight_col = -1
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Draw highlight with span during drag
        if self.highlight_row >= 0 and self.highlight_col >= 0:
            # Get span from parent control center if available
            try:
                parent = self.parent()
                while parent and not hasattr(parent, 'drag_rspan'):
                    parent = parent.parent()
                if parent:
                    rspan = getattr(parent, 'drag_rspan', 1)
                    cspan = getattr(parent, 'drag_cspan', 1)
                else:
                    rspan = cspan = 1
            except:
                rspan = cspan = 1
            
            painter.fillRect(
                self.highlight_col * (self.cell_size + self.spacing),
                self.highlight_row * (self.cell_size + self.spacing),
                cspan * self.cell_size + (cspan - 1) * self.spacing,
                rspan * self.cell_size + (rspan - 1) * self.spacing,
                QColor(255, 255, 0, 100)
            )

class ControlCenter(QWidget):
    def __init__(self):
        super().__init__()
        self.edit_mode = False   # Νέα κατάσταση
        self.config = Config()
        
        # Load plugins once and cache them
        self.plugins = load_plugins(self)
        
        self.init_ui()

    def get_plugin_under_cursor(self, pos):
        """Find which plugin is under the cursor position"""
        # Use grid widget parameters for consistent positioning
        cell_size = self.grid_widget.cell_size
        spacing = self.grid_widget.spacing
        
        # Simple grid calculation - each cell is at position col * (cell_size + spacing)
        col = pos.x() // (cell_size + spacing)
        row = pos.y() // (cell_size + spacing)
        
        # Find plugin at this grid position (check all cells of multi-cell widgets)
        all_positions = self.config.get_all_plugin_positions()
        enabled_plugins = self.config.get_enabled_plugins_list()
        
        for plugin_name, plugin_pos in all_positions.items():
            if plugin_name not in enabled_plugins:
                continue
                
            # Get plugin span
            size = self.config.get_plugin_size(plugin_name)
            if size != "Default":
                rspan, cspan = get_size_span(size)
            else:
                # Get default span from plugin
                for plugin in self.plugins:
                    if getattr(plugin, "plugin_name", "") == plugin_name:
                        rspan, cspan = getattr(plugin, "grid_span", (2, 2))
                        break
                else:
                    rspan, cspan = (2, 2)
            
            # Check if cursor is within plugin's area
            if (plugin_pos["row"] <= row < plugin_pos["row"] + rspan and 
                plugin_pos["col"] <= col < plugin_pos["col"] + cspan):
                return plugin_name
        return None
    
    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        print(f"Edit mode: {self.edit_mode}")
        
        # Recreate overlay if it doesn't exist or was deleted
        if not hasattr(self, 'overlay') or not self.overlay:
            self.overlay = OverlayWidget(self, self.grid_widget)
        
        try:
            if self.edit_mode:
                self.overlay.show_overlay()
            else:
                self.overlay.hide_overlay()
        except RuntimeError:
            # Overlay was deleted, recreate it
            self.overlay = OverlayWidget(self, self.grid_widget)
            if self.edit_mode:
                self.overlay.show_overlay()
                
        if hasattr(self, 'plugin_widgets'):
            for wrapper in self.plugin_widgets.values():
                wrapper.refresh_edit_mode()
                
        # Trigger grid repaint to show/hide grid lines
        if hasattr(self, 'grid_widget'):
            self.grid_widget.update()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("YoUNiXButtons")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(15)
        
        # Load plugins in grid
        grid = QGridLayout()
        grid.setSpacing(2)
        grid.setContentsMargins(0, 0, 0, 0)
        
        self.setup_grid_layout(grid)
        
        # Calculate grid size based on active plugins
        max_col, max_row = self.calculate_grid_bounds()
        cell_size = 48
        spacing = 2
        
        # Create grid widget without scroll area
        self.grid_widget = GridWidget(max_col, max_row, cell_size, spacing)
        self.grid_widget.setContentsMargins(0, 0, 0, 0)
        self.grid_widget.setLayout(grid)
        
        grid_width = (max_col + 1) * (cell_size + spacing) - spacing
        grid_height = (max_row + 1) * (cell_size + spacing) - spacing
        self.grid_widget.setFixedSize(grid_width, grid_height)
        
        # Create overlay for edit mode
        self.overlay = OverlayWidget(self, self.grid_widget)
        
        layout.addWidget(self.grid_widget)
        
        # Power control panel - align right
        power_layout = QHBoxLayout()
        power_layout.addStretch()  # Push buttons to the right
        power_layout.setSpacing(5)
        
        lock_btn = self.create_power_button("system-suspend")
        lock_btn.clicked.connect(lambda: subprocess.Popen(["loginctl", "lock-session"]))
        power_layout.addWidget(lock_btn)
        
        logout_btn = self.create_power_button("system-log-out")
        logout_btn.clicked.connect(lambda: subprocess.Popen(["loginctl", "terminate-user", os.getenv("USER")]))
        power_layout.addWidget(logout_btn)
        
        restart_btn = self.create_power_button("view-refresh")
        restart_btn.clicked.connect(lambda: subprocess.Popen(["systemctl", "reboot"]))
        power_layout.addWidget(restart_btn)
        
        shutdown_btn = self.create_power_button("system-shutdown")
        shutdown_btn.clicked.connect(lambda: subprocess.Popen(["systemctl", "poweroff"]))
        power_layout.addWidget(shutdown_btn)
        
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon.fromTheme("document-edit"))
        edit_btn.setIconSize(QSize(24, 24))
        edit_btn.setCheckable(True)
        edit_btn.setFixedSize(50, 50)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 60, 180);
                border-radius: 8px;
                border: none;
                font-size: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 0, 200);
                color: black;
            }
        """)
        edit_btn.clicked.connect(self.toggle_edit_mode)
        power_layout.addWidget(edit_btn)
        
        layout.addLayout(power_layout)
        self.setLayout(layout)
        
        # Calculate and set window size based on grid + power buttons
        grid_width = (max_col + 1) * (cell_size + spacing) - spacing
        grid_height = (max_row + 1) * (cell_size + spacing) - spacing
        power_height = 50 + 15  # button height + spacing
        window_width = max(grid_width, 250) + 4  # margins
        window_height = grid_height + power_height + 4  # margins
        self.resize(window_width, window_height)
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 255);
                border-radius: 15px;
            }
            QMenu {
                background-color: rgba(60, 60, 60, 200);
                color: white;
                border: 1px solid rgba(80, 80, 80, 255);
            }
            QMenu::item:selected {
                background-color: rgba(80, 80, 80, 200);
                color: white;
            }
        """)
        
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, 60)
        
        # Store initial position
        self.initial_pos = self.pos()
        
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self.check_focus)
        self.focus_timer.start(500)
        
        # Setup socket server for daemon communication FIRST
        self.server = QLocalServer()
        self.server.newConnection.connect(self.handle_client)
        
        if not self.server.listen("ywidgets_daemon"):
            # Remove existing server if it exists
            QLocalServer.removeServer("ywidgets_daemon")
            if not self.server.listen("ywidgets_daemon"):
                print("Failed to start daemon server")
                QApplication.quit()
                return
        
        self.setFocus()
        self.activateWindow()
        
        # Store plugins for reference
        self.plugin_widgets = {}
        self.drag_plugin_name = None
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def create_power_button(self, icon_name):
        btn = QPushButton()
        btn.setIcon(QIcon.fromTheme(icon_name))
        btn.setIconSize(QSize(36, 36))
        btn.setFixedSize(50, 50)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 60, 180);
                border-radius: 8px;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
        """)
        return btn
    
    def check_focus(self):
        if not self.isActiveWindow():
            self.hide()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Don't save window size since it's calculated from grid
    
    def calculate_grid_bounds(self):
        # Get enabled plugins and their positions
        enabled_plugins = self.config.get_enabled_plugins_list()
        all_positions = self.config.get_all_plugin_positions()
        
        max_col = 0
        max_row = 0
        
        for plugin_name in enabled_plugins:
            if plugin_name in all_positions:
                pos = all_positions[plugin_name]
                # Get plugin size to calculate span
                saved_size = self.config.get_plugin_size(plugin_name)
                if saved_size != "Default":
                    rspan, cspan = get_size_span(saved_size)
                else:
                    # Default span from plugin class
                    for plugin in self.plugins:
                        if getattr(plugin, "plugin_name", "") == plugin_name:
                            rspan, cspan = getattr(plugin, "grid_span", (2, 2))
                            break
                    else:
                        rspan, cspan = (2, 2)
                
                max_col = max(max_col, pos["col"] + cspan - 1)
                max_row = max(max_row, pos["row"] + rspan - 1)
        
        return max_col, max_row
    
    def show_context_menu(self, position):
        if not self.edit_mode:
            return
            
        # Check if right-click is on a plugin
        grid_pos = position
        plugin_name = self.get_plugin_under_cursor(grid_pos)
        
        menu = QMenu(self)
        
        if plugin_name:
            # Plugin-specific menu
            plugin_title = plugin_name
            for plugin in self.plugins:
                if getattr(plugin, "plugin_name", "") == plugin_name:
                    plugin_title = getattr(plugin, "plugin_title", plugin_name)
                    break
            
            remove_action = menu.addAction(f"Remove {plugin_title}")
            remove_action.triggered.connect(lambda: self.remove_plugin(plugin_name))
            
            # Size submenu
            size_menu = menu.addMenu("Size")
            size_menu.addAction("Default").triggered.connect(lambda: self.change_plugin_size(plugin_name, "Default"))
            size_menu.addAction("Small").triggered.connect(lambda: self.change_plugin_size(plugin_name, "Small"))
            size_menu.addAction("Normal").triggered.connect(lambda: self.change_plugin_size(plugin_name, "Normal"))
            size_menu.addAction("Medium").triggered.connect(lambda: self.change_plugin_size(plugin_name, "Medium"))
            size_menu.addAction("Large").triggered.connect(lambda: self.change_plugin_size(plugin_name, "Large"))
            size_menu.addAction("Huge").triggered.connect(lambda: self.change_plugin_size(plugin_name, "Huge"))
        else:
            # General menu for adding plugins
            add_menu = menu.addMenu("Add plugin")
            
            # Get available plugins that aren't already enabled
            from plugin_manager import get_available_plugins
            available = get_available_plugins()
            enabled = self.config.get_enabled_plugins_list()
            
            for plugin_info in available:
                if plugin_info["name"] not in enabled:
                    action = add_menu.addAction(plugin_info["title"])
                    action.triggered.connect(lambda checked, name=plugin_info["name"]: self.add_plugin(name))
        
        menu.exec(self.mapToGlobal(position))
    
    def add_plugin(self, plugin_name):
        # Find next empty position
        enabled = self.config.get_enabled_plugins_list()
        positions = self.config.get_all_plugin_positions()
        
        # Find next available row
        used_rows = [pos["row"] for pos in positions.values()]
        next_row = max(used_rows) + 2 if used_rows else 0
        
        # Add to enabled list and set position
        enabled.append(plugin_name)
        self.config.set_enabled_plugins(enabled)
        self.config.set_plugin_position(plugin_name, next_row, 0)
        
        # Recreate layout
        self.recreate_layout()
    

    def move_plugin(self, plugin_name, direction):
        pos = self.config.get_plugin_position(plugin_name)
        current_row, current_col = pos["row"], pos["col"]
        
        # Calculate new position
        if direction == "left":
            new_row, new_col = current_row, current_col - 1
        elif direction == "right":
            new_row, new_col = current_row, current_col + 1
        elif direction == "up":
            new_row, new_col = current_row - 1, current_col
        elif direction == "down":
            new_row, new_col = current_row + 1, current_col
        
        # Check bounds
        if new_col < 0 or new_row < 0:
            return
        
        # Find plugin at target position
        all_positions = self.config.get_all_plugin_positions()
        target_plugin = None
        
        for other_name, other_pos in all_positions.items():
            if other_name != plugin_name and other_pos["row"] == new_row and other_pos["col"] == new_col:
                target_plugin = other_name
                break
        
        # Move or swap positions
        if target_plugin:
            # Swap positions
            self.config.set_plugin_position(target_plugin, current_row, current_col)
        
        self.config.set_plugin_position(plugin_name, new_row, new_col)
        self.recreate_layout()
    
    def change_plugin_size(self, plugin_name, size):
        # Save the new size
        self.config.set_plugin_size(plugin_name, size)
        
        # Recreate the UI with new size
        self.recreate_layout()
    
    def recreate_layout(self):
        self._in_recreate = True
        
        # 1. Temporarily hide overlay to prevent geometry conflicts during resize
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.hide()
        
        layout = self.layout()
        
        # 2. Create new grid layout
        new_grid = QGridLayout()
        new_grid.setSpacing(2)
        new_grid.setContentsMargins(0, 0, 0, 0)
        
        self.setup_grid_layout(new_grid)
        
        # 3. Calculate new dimensions
        max_col, max_row = self.calculate_grid_bounds()
        cell_size = self.grid_widget.cell_size 
        spacing = self.grid_widget.spacing
        
        new_grid_widget = GridWidget(max_col, max_row, cell_size, spacing)
        new_grid_widget.setContentsMargins(0, 0, 0, 0)
        new_grid_widget.setLayout(new_grid)
        
        grid_width = (max_col + 1) * (cell_size + spacing) - spacing
        grid_height = (max_row + 1) * (cell_size + spacing) - spacing
        new_grid_widget.setFixedSize(grid_width, grid_height)
        
        # 4. Replace widget
        old_grid_widget = self.grid_widget
        layout.replaceWidget(old_grid_widget, new_grid_widget)
        self.grid_widget = new_grid_widget
        
        # 5. Clean up old widget
        old_grid_widget.setParent(None)
        self.layout().update()  # Ensure layout acknowledges removal immediately
        old_grid_widget.deleteLater()
        
        # 6. FORCE WINDOW SHRINK
        # Reset constraints first - this is the key to allowing the window to get smaller
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)
        
        power_height = 50 + 15 
        window_width = max(grid_width, 250) + 4
        window_height = grid_height + power_height + 4
        
        # Force Qt to forget the previous size expectations
        self.layout().activate() 
        
        # Apply the exact size and lock it
        self.setFixedSize(window_width, window_height)
        
        # Optional: Ensure the window stays within screen bounds after shrinking
        self.adjustSize()
        
        # 7. Update Overlay and reposition
        try:
            if hasattr(self, 'overlay') and self.overlay:
                self.overlay.setParent(self.grid_widget)
                if self.edit_mode:
                    self.overlay.show_overlay()
            else:
                self.overlay = OverlayWidget(self, self.grid_widget)
                if self.edit_mode:
                    self.overlay.show_overlay()
        except RuntimeError:
            self.overlay = OverlayWidget(self, self.grid_widget)
            if self.edit_mode:
                self.overlay.show_overlay()
            
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, 60)
        
        self._in_recreate = False
        QTimer.singleShot(50, self.force_hyprland_move)
    
    def force_hyprland_move(self):
        try:
            # Note: We use 'exact' to bypass any relative positioning
            subprocess.Popen([
                "hyprctl", "dispatch", "movewindowpixel", 
                "exact 10 45,title:^YoUNiXButtons$"
            ])
        except Exception as e:
            print(f"Failed to move window: {e}")
            
    def setup_grid_layout(self, grid):
        # Set fixed 48x48 base cell size
        cell_size = 48
        spacing = grid.spacing()  # Use grid's spacing instead of hardcoding
        
        # Set uniform column and row sizes
        max_col, max_row = self.calculate_grid_bounds()
        for col in range(max_col + 1):
            grid.setColumnMinimumWidth(col, cell_size)
            grid.setColumnStretch(col, 0)
        for row in range(max_row + 1):
            grid.setRowMinimumHeight(row, cell_size)
            grid.setRowStretch(row, 0) 
        
        # Get enabled plugins and positions from config
        enabled_plugins = self.config.get_enabled_plugins_list()
        all_positions = self.config.get_all_plugin_positions()
        
        # Convert positions to tuple format
        positions = {}
        for plugin_name, pos_data in all_positions.items():
            if plugin_name in enabled_plugins:
                positions[plugin_name] = (pos_data["row"], pos_data["col"])
                
        self.plugin_widgets = {}
        
        for plugin in self.plugins:
            plugin_name = getattr(plugin, "plugin_name", "Unknown")
            if plugin_name in positions:
                row, col = positions[plugin_name]
                # Check for saved size override
                saved_size = self.config.get_plugin_size(plugin_name)
                if saved_size != "Default":
                    rspan, cspan = get_size_span(saved_size)
                else:
                    rspan, cspan = getattr(plugin, "grid_span", (2, 2))
                
                # Set size policy to prevent expansion
                plugin.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                
                # Enforce exact size to match grid cells (for the inner plugin)
                plugin_width = cell_size * cspan + (cspan - 1) * spacing
                plugin_height = cell_size * rspan + (rspan - 1) * spacing
                plugin.setFixedSize(plugin_width, plugin_height)
                
                # Notify plugin of size change
                saved_size_str = self.config.get_plugin_size(plugin_name)
                size_enum = PluginSize(saved_size_str) if saved_size_str != "Default" else PluginSize.NORMAL
                if hasattr(plugin, 'on_size_changed'):
                    plugin.on_size_changed(size_enum)
                
                # Wrap the plugin with the draggable container
                draggable_wrapper = DraggablePlugin(plugin, self)
                # Ensure the wrapper takes the same fixed size
                draggable_wrapper.setFixedSize(plugin_width, plugin_height)
                
                # Add the wrapper to the grid
                grid.addWidget(draggable_wrapper, row, col, rspan, cspan)
                self.plugin_widgets[plugin_name] = draggable_wrapper
    
    def start_drag_preview(self, plugin_name):
        self.drag_plugin_name = plugin_name
        
        # Store span of dragged widget
        size = self.config.get_plugin_size(plugin_name)
        if size != "Default":
            self.drag_rspan, self.drag_cspan = get_size_span(size)
        else:
            for plugin in self.plugins:
                if getattr(plugin, "plugin_name", "") == plugin_name:
                    self.drag_rspan, self.drag_cspan = getattr(plugin, "grid_span", (1, 1))
                    break
            else:
                self.drag_rspan, self.drag_cspan = (1, 1)
    
    def update_drag_highlight(self, row, col):
        # Check if target area is free
        if not self._is_area_free(row, col, self.drag_rspan, self.drag_cspan, self.drag_plugin_name):
            self.grid_widget.clear_highlight()
            return
        
        # Only show highlight, don't expand grid during drag
        self.grid_widget.set_highlight(row, col)
    
    def _is_area_free(self, row, col, rspan, cspan, exclude_plugin):
        all_positions = self.config.get_all_plugin_positions()
        enabled_plugins = self.config.get_enabled_plugins_list()
        
        # Check each cell that the widget would occupy
        for r in range(row, row + rspan):
            for c in range(col, col + cspan):
                # Check if any other enabled plugin occupies this cell
                for plugin_name, pos in all_positions.items():
                    if plugin_name == exclude_plugin or plugin_name not in enabled_plugins:
                        continue
                    
                    # Get plugin span from config only
                    size = self.config.get_plugin_size(plugin_name)
                    if size != "Default":
                        p_rspan, p_cspan = get_size_span(size)
                    else:
                        p_rspan, p_cspan = (2, 2)  # Default span
                    
                    # Check if this cell overlaps with the plugin
                    if (pos["row"] <= r < pos["row"] + p_rspan and 
                        pos["col"] <= c < pos["col"] + p_cspan):
                        return False
        
        return True
    
    def _extend_grid_layout(self, new_max_row, new_max_col):
        grid = self.grid_widget.layout()
        cell_size = self.grid_widget.cell_size
        
        for col in range(self.grid_widget.max_col + 1, new_max_col + 1):
            grid.setColumnMinimumWidth(col, cell_size)
            grid.setColumnStretch(col, 0)
        
        for row in range(self.grid_widget.max_row + 1, new_max_row + 1):
            grid.setRowMinimumHeight(row, cell_size)
            grid.setRowStretch(row, 0)
    
    def _resize_grid_widget(self):
        gw = self.grid_widget
        w = (gw.max_col + 1) * gw.cell_size + gw.max_col * gw.spacing
        h = (gw.max_row + 1) * gw.cell_size + gw.max_row * gw.spacing
        gw.setFixedSize(w, h)
    
    def end_drag_preview(self, plugin_name):
        grid_widget = self.grid_widget
        
        # Store highlight position before clearing
        highlight_row = grid_widget.highlight_row
        highlight_col = grid_widget.highlight_col
        
        # Clear highlight first
        grid_widget.clear_highlight()
        self.drag_plugin_name = None
        
        if highlight_row >= 0 and highlight_col >= 0:
            current_pos = self.config.get_plugin_position(plugin_name)
            new_row, new_col = highlight_row, highlight_col
            
            if new_row != current_pos["row"] or new_col != current_pos["col"]:
                # Check for collision and swap
                all_positions = self.config.get_all_plugin_positions()
                target_plugin = None
                
                for other_name, other_pos in all_positions.items():
                    if other_name != plugin_name and other_pos["row"] == new_row and other_pos["col"] == new_col:
                        target_plugin = other_name
                        break
                
                if target_plugin:
                    self.config.set_plugin_position(target_plugin, current_pos["row"], current_pos["col"])
                
                self.config.set_plugin_position(plugin_name, new_row, new_col)
                
                # Recreate layout (this will handle grid expansion if needed)
                self.recreate_layout()
    
    def remove_plugin(self, plugin_name):
        enabled = self.config.get_enabled_plugins_list()
        if plugin_name in enabled:
            enabled.remove(plugin_name)
            self.config.set_enabled_plugins(enabled)
            self.recreate_layout()
    
    def handle_client(self):
        client = self.server.nextPendingConnection()
        if client:
            client.readyRead.connect(lambda: self.process_message(client))
    
    def process_message(self, client):
        data = client.readAll().data().decode()
        if data == "toggle":
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
        client.disconnectFromServer()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep daemon running when window closes
    
    # Check if daemon is already running
    test_socket = QLocalSocket()
    test_socket.connectToServer("ywidgets_daemon")
    if test_socket.waitForConnected(100):
        # Daemon already running, send toggle and exit
        test_socket.write(b"toggle")
        test_socket.waitForBytesWritten()
        test_socket.disconnectFromServer()
        sys.exit(0)
    
    widget = ControlCenter()
    widget.show()
    sys.exit(app.exec())