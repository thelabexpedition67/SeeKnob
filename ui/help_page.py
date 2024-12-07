import urwid
from debug_logger import Debug

debug = Debug()  # Initialize Debug logger

class HelpPage(urwid.WidgetWrap):
    def __init__(self, on_exit_callback):
        """
        Help Page with scrollable content about how to use the application.
        :param on_exit_callback: Function to call when exiting back to the menu.
        """
        self.on_exit_callback = on_exit_callback

        # Header
        header = urwid.Text("Help - How to Use SeeKnob", align='center')
        header = urwid.AttrMap(header, 'header')

        # Body content
        help_text = (
            "How to Use:\n\n"
            "1. Main Menu:\n"
            "   - 'Select File From Filesystem': Browse files and select a video to play.\n"
            "   - 'Help': Show this help screen.\n"
            "   - 'About': Information about the application.\n"
            "   - 'Quit': Exit the program cleanly.\n\n"
            "2. File Browser:\n"
            "   - Navigate: Use UP/DOWN arrows.\n"
            "   - Open Folder: Press ENTER on a folder.\n"
            "   - Select File: Press ENTER on a video file.\n"
            "   - Return to Menu: Press 'Esc' or 'q'.\n\n"
            "3. Video Playback:\n"
            "   - Use your knob to seek forward/backward in the video.\n"
            "   - Use buttons to set and replay marker points.\n"
            "   - Increase/Decrease seek step size.\n\n"
            "4. Installing MPV (Required Dependency):\n"
            "   This application requires MPV, a powerful media player, to function correctly.\n"
            "   Follow the instructions below to install MPV:\n\n"
            "   - **Debian/Ubuntu**:\n"
            "       $ sudo apt update\n"
            "       $ sudo apt install mpv\n\n"
            "   - **Red Hat/CentOS/Fedora**:\n"
            "       $ sudo dnf install mpv\n\n"
            "   - **Arch Linux**:\n"
            "       $ sudo pacman -S mpv\n\n"
            "   After installing MPV, you can verify it works by running:\n"
            "       $ mpv --version\n\n"
            "5. Device Configuration - Understanding 'by-id' Paths:\n"
            "   Linux systems provide stable device paths under '/dev/input/by-id/' for input devices.\n"
            "   These paths are persistent because they are based on hardware Vendor ID and Product ID.\n\n"
            "   Example Device Paths:\n"
            "   lrwxrwxrwx 1 root root 10 Dec  7 15:27 usb-8808_6613-if02-event-kbd -> ../event28\n"
            "   lrwxrwxrwx 1 root root 10 Dec  7 15:27 usb-8808_6613-event-kbd -> ../event26\n\n"
            "   - To find your devices:\n"
            "       Run the command:\n"
            "       $ ls -l /dev/input/by-id/\n\n"
            "6. Blocking System from Managing USB Device:\n"
            "   If the USB device (knob or buttons) is being controlled by the system (e.g., it adjusts\n"
            "   system volume by default), you need to block the system from managing it.\n\n"
            "   Steps:\n"
            "   - 1. Identify the USB device:\n"
            "       Run the following command to find the device path and IDs:\n"
            "       $ lsusb\n\n"
            "   - 2. Create a udev rule to ignore the device:\n"
            "       Add a new udev rule to block the system from managing the device.\n\n"
            "       $ sudo nano /etc/udev/rules.d/99-block-usb.rules\n\n"
            "       Add the following line, replacing VENDOR_ID and PRODUCT_ID with your device IDs:\n"
            "       ACTION==\"add|change\", ATTRS{idVendor}==\"VENDOR_ID\", ATTRS{idProduct}==\"PRODUCT_ID\", ENV{ID_INPUT}=\"\", ENV{ID_INPUT_KEY}=\"\"\n\n"
            "   - 3. Reload udev rules and unplug/replug the device:\n"
            "       $ sudo udevadm control --reload-rules\n"
            "       $ sudo udevadm trigger\n\n"
            "   - 4. Verify the Device:\n"
            "       Ensure the system no longer controls the device (e.g., it no longer adjusts volume).\n\n"
            "7. Configuration File (config.json):\n"
            "   The application is configurable through the 'config.json' file. Below is an example:\n\n"
            "   {\n"
            "       \"devices\": {\n"
            "           \"knob_device\": \"/dev/input/by-id/usb-8808_6613-if02-event-kbd\",\n"
            "           \"buttons_device\": \"/dev/input/by-id/usb-8808_6613-event-kbd\"\n"
            "       },\n"
            "       \"default_seek_step\": 0.5,\n"
            "       \"key_mappings\": {\n"
            "           \"seek_forward\": \"KEY_VOLUMEUP\",\n"
            "           \"seek_backward\": \"KEY_VOLUMEDOWN\",\n"
            "           \"toggle_pause\": \"KEY_PLAYPAUSE\",\n"
            "           \"decrease_seek_step\": \"KEY_1\",\n"
            "           \"increase_seek_step\": \"KEY_2\",\n"
            "           \"set_marker\": \"KEY_3\",\n"
            "           \"play_marker\": \"KEY_4\"\n"
            "       },\n"
            "       \"filem_ext_filters\": \"AVI,avi,mp4\",\n"
            "       \"filem_show_hidden\": \"False\",\n"
            "       \"filem_start_path\": \"/\",\n"
            "       \"mpv_xinit\": \"False\",\n"
            "       \"mpv_full_screen\": \"True\",\n"
            "       \"mpv_fs_screen\": \"0\",\n"
            "       \"mpv_socket\": \"/tmp/mpv-socket\"\n"
            "   }\n\n"
            "   - **devices**: Paths for knob and buttons input devices.\n"
            "   - **default_seek_step**: Initial seek step in seconds.\n"
            "   - **key_mappings**: Keycodes for actions like seeking and setting markers.\n"
            "   - **filem_ext_filters**: Allowed video file extensions.\n"
            "   - **filem_show_hidden**: Whether to show hidden files in the file browser.\n"
            "   - **filem_start_path**: Starting directory for the file browser.\n"
            "   - **mpv_xinit**: Set 'True' to run MPV in environments without a desktop.\n"
            "   - **mpv_full_screen**: Set 'True' to launch MPV in fullscreen.\n"
            "   - **mpv_fs_screen**: Specify the monitor for fullscreen playback (0 = primary).\n"
            "   - **mpv_socket**: Path for MPV's IPC socket.\n\n"
            "Press 'Esc' or 'q' to return to the main menu."
        )

        # Convert the help text into scrollable lines
        lines = [urwid.Text(line) for line in help_text.splitlines()]
        body = urwid.ListBox(urwid.SimpleFocusListWalker(lines))

        # Footer
        footer = urwid.Text("Press 'Esc' or 'q' to go back.", align='center')
        footer = urwid.AttrMap(footer, 'footer')

        # Layout
        content = urwid.Frame(header=header, body=body, footer=footer)

        # Wrap the widget
        super().__init__(urwid.LineBox(content, title="Help"))

    def selectable(self):
        # Make the widget selectable so it can receive keypress events
        return True

    def keypress(self, size, key):
        """Handle keypresses for navigation."""
        if key in ('esc', 'q'):
            debug.log("Esc or Q pressed. Returning to main menu.")
            self.on_exit_callback()
            return None  # Key handled
        return super().keypress(size, key)
