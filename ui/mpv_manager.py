import subprocess
import socket
import json
import os
from debug_logger import Debug

debug = Debug()  # Initialize Debug logger

class MPVManager:
    def __init__(self, video_file, socket_path, xinit, full_screen, fs_screen):
        """
        MPV Manager to handle video playback.
        :param video_file: Path to the video file.
        :param socket_path: Path for the MPV IPC socket.
        :param xinit: Whether to use xinit for non-desktop environments.
        :param full_screen: Whether to launch MPV in fullscreen mode.
        """
        self.video_file = video_file
        self.socket_path = socket_path
        self.xinit = xinit
        self.full_screen = full_screen  # Initialize full_screen attribute
        self.fs_screen = fs_screen  # New parameter for screen selection
        self.process = None

    def start_mpv(self):
        """Start MPV with or without xinit."""
        if not self.video_file:
            debug.log("No video file selected.")
            return

        mpv_command = [
            "mpv",
            self.video_file,
            f"--input-ipc-server={self.socket_path}"
        ]

        if self.full_screen:
            mpv_command.append("--fs")  # Launch in fullscreen mode
            mpv_command.append(f"--fs-screen={self.fs_screen}")  # Specify fullscreen monitor

        # Add high-resolution seek for smoother seeking
        mpv_command.append("--hr-seek=yes")  # Enable frame-accurate seeking
        mpv_command.append("--hr-seek-demuxer-offset=0")  # Start decoding as close as possible
        mpv_command.append("--hwdec=auto")  # Enable hardware acceleration

        debug.log(f"Launching MPV: {' '.join(mpv_command)}")

        try:
            # Redirect stdout and stderr to prevent terminal interference
            if self.xinit:
                full_command = ["xinit", "--"] + mpv_command
                debug.log(f"Starting MPV with xinit: {' '.join(full_command)}")
                self.process = subprocess.Popen(
                    full_command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                self.process = subprocess.Popen(
                    mpv_command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

        except Exception as e:
            debug.log_exception(e)

    def send_command(self, command):
        """Send a JSON command to MPV via the IPC socket."""
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(self.socket_path)
                client.sendall((json.dumps(command) + "\n").encode("utf-8"))
        except Exception as e:
            debug.log_exception(e)

    def show_message(self, message, duration=2000):
        """Show a message on MPV."""
        self.send_command({"command": ["show_text", message, duration]})

    def seek(self, amount):
        """Seek in the video."""
        self.send_command({"command": ["seek", amount, "relative"]})

    def toggle_pause(self):
        """Toggle play/pause."""
        self.send_command({"command": ["cycle", "pause"]})

    def get_current_time(self):
        """Get the current playback position."""
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(self.socket_path)
                client.sendall((json.dumps({"command": ["get_property", "time-pos"]}) + "\n").encode("utf-8"))
                response = client.recv(1024).decode("utf-8")
                data = json.loads(response)
                return data.get("data", 0)
        except Exception as e:
            debug.log_exception(e)
            return 0
