import os
import sys
import urwid
import threading
import signal

from ui.menu import Menu
from ui.folder_browser import FolderBrowser
from ui.mpv_manager import MPVManager
from ui.about_page import AboutPage
from input.input_handler import InputHandler
from config.loader import load_config
from ui.help_page import HelpPage
from ui.video_playing_page import VideoPlayingPage
from debug_logger import Debug

stop_event = threading.Event()
debug = Debug()  # Initialize Debug logger

def main():
    config = load_config("config.json")
    mpv_manager = MPVManager(
        video_file=None,
        socket_path=config["mpv_socket"],
        full_screen=config["mpv_full_screen"].lower() == "true",
        fs_screen=int(config.get("mpv_fs_screen", "0"))
    )

    # Define callbacks for the menu and other screens
    def switch_to_menu():
        """Return to the main menu."""
        loop.widget = menu
        loop.screen.clear()
        loop.draw_screen()

    def on_select_file():
        """Switch to the folder browser."""
        browser_view = folder_browser.widget()
        loop.widget = browser_view

    def on_about():
        """Show the About page."""
        about_page = AboutPage(on_exit_callback=switch_to_menu)
        loop.widget = about_page

    def on_quit():
        """Handle quitting the application."""
        mpv_manager.quit_mpv()  # Quit MPV if running
        stop_event.set()  # Stop input threads
        debug.log("Goodbye!")
        raise urwid.ExitMainLoop()

    def on_help():
        """Show the Help page."""
        help_page = HelpPage(on_exit_callback=switch_to_menu)
        loop.widget = help_page

    def on_file_selected(selected_file):
        """
        Callback when a video file is selected.
        Displays the VideoPlayingPage and starts MPV playback.
        """
        if selected_file:
            mpv_manager.video_file = selected_file
            mpv_manager.start_mpv()
            video_page = VideoPlayingPage(mpv_manager, on_exit_callback=switch_to_menu)
            loop.widget = video_page
            loop.screen.clear()
            loop.draw_screen()

    def on_browser_exit():
        """Return to the main menu when exiting the file browser."""
        loop.widget = menu

    # Initialize UI components
    menu = Menu(on_select_file, on_help, on_about, on_quit, mpv_manager=mpv_manager)
    folder_browser = FolderBrowser(
        start_dir=config["filem_start_path"],
        ext_filters=config["filem_ext_filters"].split(","),
        show_hidden=config["filem_show_hidden"] == "True",
        on_file_selected=on_file_selected,
        on_exit=switch_to_menu
    )

    palette = [
        ('folder', 'light green', 'black'),
        ('focus', 'standout', 'black'),
        ('header', 'white,bold', 'dark blue'),
        ('footer', 'yellow', 'black')
    ]

    # Initialize MainLoop
    global loop
    loop = urwid.MainLoop(menu, palette=palette)

    # Initialize and start the InputHandler
    input_handler = InputHandler(mpv_manager, stop_event, config, loop)
    input_handler.start()

    # Run the Urwid MainLoop
    loop.run()

if __name__ == "__main__":
    main()
