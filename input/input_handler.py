import evdev
from evdev import InputDevice, categorize, ecodes
import select
from debug_logger import Debug

debug = Debug()

class InputHandler:
    def __init__(self, mpv_manager, stop_event, config, loop):
        self.mpv_manager = mpv_manager
        self.knob_device_path = config["devices"]["knob_device"]
        self.buttons_device_path = config["devices"]["buttons_device"]
        self.seek_step = config["default_seek_step"]
        self.marker_point = 0
        self.stop_event = stop_event
        self.keys = config["key_mappings"]
        self.loop = loop  # Pass Urwid MainLoop to send navigation keys

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
                if key_event.keystate == 1:  # Key pressed
                    if self.mpv_manager.is_running():
                        # MPV is running, use video controls
                        if key_event.keycode == self.keys["seek_forward"]:
                            self.mpv_manager.seek(self.seek_step)
                            debug.log(f"Seek forward {self.seek_step:.2f} seconds.")
                        elif key_event.keycode == self.keys["seek_backward"]:
                            self.mpv_manager.seek(-self.seek_step)
                            debug.log(f"Seek backward {self.seek_step:.2f} seconds.")
                        elif key_event.keycode == self.keys["toggle_pause"]:
                            self.mpv_manager.toggle_pause()
                            debug.log("Play/Pause toggled.")
                    else:
                        # MPV is not running, send navigation keys to Urwid MainLoop
                        if key_event.keycode == self.keys["nav_up"]:
                            debug.log("Navigating Up")
                            self.handle_navigation("up")
                        elif key_event.keycode == self.keys["nav_down"]:
                            debug.log("Navigating Down")
                            self.handle_navigation("down")
                        elif key_event.keycode == self.keys["nav_select"]:
                            debug.log("Confirming Selection")
                            self.handle_navigation("enter")

        self.handle_device_events(self.knob_device_path, "KNOB", process_event)

    def handle_navigation(self, key):
        """Inject navigation keys into the Urwid MainLoop."""
        try:
            debug.log(f"Sending navigation key to Urwid: {key}")
            focus_widget = self.loop.widget  # Get the currently focused widget
            if hasattr(focus_widget, "keypress"):
                size = (100, 30)  # Dummy size tuple: width=100, height=30
                focus_widget.keypress(size, key)  # Process the navigation key
                self.loop.draw_screen()  # Force the screen to update
            else:
                debug.log("Widget does not support keypress, falling back to process_input")
                self.loop.process_input([key])
                self.loop.draw_screen()  # Force screen redraw after input
        except Exception as e:
            debug.log_exception(e)



    def handle_button_events(self):
        """Handle button input events."""
        def process_event(event):
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == 1:  # Key pressed
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

        self.handle_device_events(self.buttons_device_path, "BUTTON", process_event)

    def start(self):
        """Start both knob and button threads."""
        import threading
        threading.Thread(target=self.handle_knob_events, daemon=True).start()
        threading.Thread(target=self.handle_button_events, daemon=True).start()