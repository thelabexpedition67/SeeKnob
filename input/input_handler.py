import evdev
from evdev import InputDevice, categorize, ecodes
import select  # Fix missing import
from debug_logger import Debug

debug = Debug()  # Initialize Debug logger

class InputHandler:
    def __init__(self, mpv_manager, stop_event, config):
        self.mpv_manager = mpv_manager
        self.knob_device_path = config["devices"]["knob_device"]
        self.buttons_device_path = config["devices"]["buttons_device"]
        self.seek_step = config["default_seek_step"]
        self.marker_point = 0
        self.stop_event = stop_event
        self.keys = config["key_mappings"]

    def handle_device_events(self, device_path, handler_name, event_callback):
        """Generalized handler for input devices."""
        try:
            device = InputDevice(device_path)
            debug.log(f"Listening to {handler_name} events: {device.path}")
            while not self.stop_event.is_set():
                r, _, _ = select.select([device.fd], [], [], 0.1)  # Non-blocking
                if r:
                    for event in device.read():
                        if self.stop_event.is_set():
                            break
                        event_callback(event)
        except Exception as e:
            debug.log_exception(e)

    def handle_knob_events(self):
        """Handle knob input events."""
        def process_event(event):
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == 1:
                    if key_event.keycode == self.keys["seek_forward"]:
                        self.mpv_manager.seek(self.seek_step)
                        debug.log(f"Seek forward {self.seek_step:.2f} seconds.")
                    elif key_event.keycode == self.keys["seek_backward"]:
                        self.mpv_manager.seek(-self.seek_step)
                        debug.log(f"Seek backward {self.seek_step:.2f} seconds.")
                    elif key_event.keycode == self.keys["toggle_pause"]:
                        self.mpv_manager.toggle_pause()
                        debug.log("Play/Pause toggled.")

        self.handle_device_events(self.knob_device_path, "KNOB", process_event)

    def handle_button_events(self):
        """Handle button input events."""
        def process_event(event):
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == 1:
                    if key_event.keycode == self.keys["decrease_seek_step"]:
                        self.seek_step = max(0.1, round(self.seek_step - 0.1, 2))
                        self.mpv_manager.show_message(f"Seek Step: {self.seek_step:.2f}s", 3000)
                    elif key_event.keycode == self.keys["increase_seek_step"]:
                        self.seek_step = round(self.seek_step + 0.1, 2)
                        self.mpv_manager.show_message(f"Seek Step: {self.seek_step:.2f}s", 3000)
                    elif key_event.keycode == self.keys["set_marker"]:
                        self.marker_point = self.mpv_manager.get_current_time()
                        self.mpv_manager.show_message(f"Marker Set: {self.marker_point:.2f}s", 3000)
                    elif key_event.keycode == self.keys["play_marker"]:
                        if self.marker_point > 0:
                            self.mpv_manager.send_command({"command": ["seek", self.marker_point, "absolute"]})
                            #self.mpv_manager.show_message(f"Playing from Marker: {self.marker_point:.2f}s", 3000)

        self.handle_device_events(self.buttons_device_path, "BUTTON", process_event)
