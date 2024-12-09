import evdev
from evdev import InputDevice, categorize, ecodes
import select
import os
import json
import hashlib
from debug_logger import Debug

debug = Debug()

class InputHandler:
    def __init__(self, mpv_manager, stop_event, config, loop):
        self.mpv_manager = mpv_manager
        self.devices = self.load_devices(config["devices"])
        self.seek_step = config["default_seek_step"]
        self.marker_points = {}  # For dynamic markers
        self.marker_persistence = config.get("marker_persistence", "False").lower() == "true"
        self.marker_storage_folder = config.get("marker_storage_folder", "./markers")
        self.stop_event = stop_event
        self.keys = self.parse_key_mappings(config["key_mappings"])
        self.loop = loop

        if not os.path.exists(self.marker_storage_folder):
            os.makedirs(self.marker_storage_folder)

    def load_devices(self, devices_config):
        devices = {}
        for name, path in devices_config.items():
            try:
                device = InputDevice(path)
                devices[name] = device
                debug.log(f"Loaded device '{name}' at '{path}'")
            except Exception as e:
                debug.log_exception(f"Failed to load device '{name}' at '{path}': {e}")
        return devices

    def parse_key_mappings(self, key_mappings):
        parsed_keys = {}
        for action, key in key_mappings.items():
            device_name, keycode = key.split(".")
            parsed_keys[action] = (device_name, keycode)
        return parsed_keys

    def handle_device_events(self, device_name, event_callback):
        device = self.devices.get(device_name)
        if not device:
            debug.log(f"Device '{device_name}' not loaded.")
            return
        try:
            debug.log(f"Listening to {device_name}: {device.path}")
            while not self.stop_event.is_set():
                r, _, _ = select.select([device.fd], [], [], 0.1)
                if r:
                    for event in device.read():
                        if self.stop_event.is_set():
                            break
                        event_callback(event, device_name)
        except Exception as e:
            debug.log_exception(e)

    def handle_knob_events(self):
        def process_event(event, device_name):
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == 1:
                    for action, (dev, keycode) in self.keys.items():
                        if device_name == dev and key_event.keycode == keycode:
                            if self.mpv_manager.is_running():
                                self.handle_mpv_controls(action)
                            else:
                                self.handle_navigation_controls(action)

        self.handle_device_events("knob_device", process_event)

    def handle_button_events(self):
        """Handle button input events."""
        def process_event(event, device_name):
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == 1:  # Key pressed
                    for action, (dev, keycode) in self.keys.items():
                        if device_name == dev and key_event.keycode == keycode:
                            if self.mpv_manager.is_running():
                                # Handle actions when MPV is running
                                if action == "decrease_seek_step":
                                    self.seek_step = max(0.1, round(self.seek_step - 0.1, 2))
                                    self.mpv_manager.show_message(f"Seek Step: {self.seek_step:.2f}s", 3000)
                                    debug.log(f"Decreased seek step to {self.seek_step:.2f} seconds.")
                                elif action == "increase_seek_step":
                                    self.seek_step = round(self.seek_step + 0.1, 2)
                                    self.mpv_manager.show_message(f"Seek Step: {self.seek_step:.2f}s", 3000)
                                    debug.log(f"Increased seek step to {self.seek_step:.2f} seconds.")
                                elif action.startswith("set_marker"):
                                    # Marker Set: Save the current time
                                    marker_key = action.split("_")[2]
                                    self.marker_points[marker_key] = self.mpv_manager.get_current_time()
                                    self.mpv_manager.show_message(f"Marker {marker_key} Set: {self.marker_points[marker_key]:.2f}s", 3000)
                                    debug.log(f"Set marker '{marker_key}' at {self.marker_points[marker_key]:.2f} seconds.")
                                    if self.marker_persistence:
                                        self.save_markers(self.mpv_manager.video_file)
                                elif action.startswith("play_marker"):
                                    # Marker Play: Seek to the saved marker
                                    marker_key = action.split("_")[2]
                                    if marker_key in self.marker_points:
                                        self.mpv_manager.send_command({"command": ["seek", self.marker_points[marker_key], "absolute"]})
                                        self.mpv_manager.show_message(f"Playing Marker {marker_key}: {self.marker_points[marker_key]:.2f}s", 3000)
                                        debug.log(f"Playing marker '{marker_key}' at {self.marker_points[marker_key]:.2f} seconds.")
                            else:
                                # Handle actions when MPV is NOT running
                                if action == "nav_quit":
                                    debug.log("Nav Quit triggered: Sending 'q' to Urwid")
                                    self.handle_navigation("q")
                                elif action == "nav_up":
                                    debug.log("Navigating Up")
                                    self.handle_navigation("up")
                                elif action == "nav_down":
                                    debug.log("Navigating Down")
                                    self.handle_navigation("down")
                                elif action == "nav_select":
                                    debug.log("Confirming Selection")
                                    self.handle_navigation("enter")

        self.handle_device_events("buttons_device", process_event)


    def handle_mpv_controls(self, action):
        """Handle MPV-specific controls when video is playing."""
        if action == "seek_forward":
            self.mpv_manager.seek(self.seek_step)
            debug.log(f"Seek forward {self.seek_step:.2f} seconds.")
        elif action == "seek_backward":
            self.mpv_manager.seek(-self.seek_step)
            debug.log(f"Seek backward {self.seek_step:.2f} seconds.")
        elif action == "toggle_pause":
            self.mpv_manager.toggle_pause()
            debug.log("Play/Pause toggled.")

    def handle_navigation_controls(self, action):
        """Handle navigation in the Urwid interface."""
        if action == "nav_up":
            self.handle_navigation("up")
        elif action == "nav_down":
            self.handle_navigation("down")
        elif action == "nav_select":
            self.handle_navigation("enter")
        elif action == "nav_quit":
            self.handle_navigation("q")

    def handle_navigation(self, key):
        """Inject navigation keys into the Urwid MainLoop."""
        try:
            debug.log(f"Sending navigation key to Urwid: {key}")
            # Check if the loop and widget are valid
            if self.loop and self.loop.widget:
                focus_widget = self.loop.widget
                if hasattr(focus_widget, "keypress"):
                    size = (100, 30)
                    focus_widget.keypress(size, key)
                    self.loop.draw_screen()
                else:
                    debug.log("Widget does not support keypress.")
            else:
                debug.log("Urwid loop or widget is not valid. Navigation skipped.")
        except Exception as e:
            debug.log_exception(e)

    def save_markers(self, video_file):
        if not self.marker_persistence or not video_file:
            return
        file_hash = self.calculate_file_hash(video_file)
        if not file_hash:
            return
        marker_file = os.path.join(self.marker_storage_folder, f"{file_hash}.marker")
        data = {"file_name": os.path.basename(video_file), "markers": self.marker_points}
        try:
            with open(marker_file, "w") as f:
                json.dump(data, f, indent=4)
                debug.log(f"Saved markers: {data}")
        except Exception as e:
            debug.log_exception(e)


    def load_markers(self, video_file):
        """
        Load markers for the given video file from the stored marker file.
        :param video_file: Path to the video file.
        """
        if not self.marker_persistence or not video_file:
            return

        file_hash = self.calculate_file_hash(video_file)
        if not file_hash:
            return

        marker_file = os.path.join(self.marker_storage_folder, f"{file_hash}.marker")
        if os.path.exists(marker_file):
            try:
                with open(marker_file, "r") as f:
                    data = json.load(f)
                    self.marker_points = data.get("markers", {})
                    debug.log(f"Loaded markers for '{video_file}': {self.marker_points}")
            except Exception as e:
                debug.log_exception(e)
        else:
            debug.log(f"No marker file found for '{video_file}'. Initializing empty markers.")
            self.marker_points = {}


    def calculate_file_hash(self, file_path):
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            debug.log_exception(e)
            return None

    def start(self):
        import threading
        threading.Thread(target=self.handle_knob_events, daemon=True).start()
        threading.Thread(target=self.handle_button_events, daemon=True).start()
