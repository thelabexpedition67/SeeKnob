import os
import urwid
from debug_logger import Debug

debug = Debug()  # Initialize Debug logger

class VideoPlayingPage(urwid.WidgetWrap):
    def __init__(self, mpv_manager, on_exit_callback):
        """
        Page displayed when a video is being played.
        :param mpv_manager: Instance of MPVManager to control MPV.
        :param on_exit_callback: Function to return to the main menu.
        """
        self.mpv_manager = mpv_manager
        self.on_exit_callback = on_exit_callback

        # Extract the file name from the full path
        file_name = os.path.basename(self.mpv_manager.video_file)

        # Page content
        header = urwid.Text("Video Playback", align='center')
        body = urwid.Text(
            f"{file_name}\n\nThe video is currently playing in the MPV player.\n\n"
            "Press 'esc' or 'q' to stop the video and return to the main menu.",
            align='center'
        )
        footer = urwid.Text("SeeKnob - TheLabExpedition67", align='center')

        # Combine layout
        content = urwid.Pile([
            ('pack', urwid.AttrMap(header, 'header')),
            ('weight', 1, urwid.Filler(body, valign='middle')),
            ('pack', urwid.AttrMap(footer, 'footer'))
        ])

        # Wrap content in a LineBox and make it selectable
        wrapped_content = urwid.LineBox(content, title="Playing Video")
        self._selectable = True  # Enable focus

        # Use WidgetWrap
        super().__init__(wrapped_content)

    def selectable(self):
        """Make the widget selectable to handle input."""
        return True

    def keypress(self, size, key):
        """
        Handle 'q' or 'esc' keypress to stop MPV and return to the menu.
        """
        debug.log(f"Key pressed: {key}")  # Log the pressed key
        if key in ('esc', 'q'):
            if self.mpv_manager.is_running():
                self.mpv_manager.quit_mpv()
                debug.log("MPV stopped via 'q' or 'esc' on VideoPlayingPage.")
            else:
                debug.log("MPV was not running.")
            self.on_exit_callback()  # Return to the menu
            return None  # Key handled
        return super().keypress(size, key)
