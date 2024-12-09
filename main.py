import os
import sys
import urwid
import threading
import signal

from ui.menu import Menu
from ui.folder_browser import FolderBrowser
from ui.mpv_manager import MPVManager
from ui.about_page import AboutPage  # Import the AboutPage class
from input.input_handler import InputHandler
from config.loader import load_config
from ui.help_page import HelpPage  # Import the HelpPage class
from debug_logger import Debug

stop_event = threading.Event()
debug = Debug()  # Initialize Debug logger

def main():
    config = load_config("config.json")
    mpv_manager = MPVManager(
        video_file=None,
        socket_path=config["mpv_socket"],
        full_screen=config["mpv_full_screen"].lower() == "true",
        fs_screen=int(config.get("mpv_fs_screen", "0"))  # Convert screen index to integer
    )

    input_handler = InputHandler(mpv_manager, stop_event, config)
    knob_thread = threading.Thread(target=input_handler.handle_knob_events)
    button_thread = threading.Thread(target=input_handler.handle_button_events)
    knob_thread.start()
    button_thread.start()

    def switch_to_menu():
        # Remove any print statements if possible
        background = urwid.SolidFill(' ')
        combined = urwid.Overlay(
            menu,
            background,
            align='center', width=('relative', 100),
            valign='middle', height=('relative', 100)
        )
        loop.widget = combined
        loop.screen.clear()    # Force clear
        loop.draw_screen()     # Force redraw


    # Callbacks for menu actions
    def on_select_file():
        # Switch to folder browser
        browser_view = folder_browser.widget()
        loop.widget = browser_view

    def on_help():
        # Example: Just show a message (or create a help screen)
        # For simplicity, we print something and return to the menu
        debug.log("Help selected")
        # In a real scenario, you might update loop.widget to another screen.

    def on_about():
        about_page = AboutPage(on_exit_callback=switch_to_menu)
        loop.widget = about_page

    def on_quit():
        """Handle quitting the application."""
        # Check if MPV is running and close it first
        mpv_manager.quit_mpv()
        # Stop input handling threads
        stop_event.set()
        knob_thread.join()
        button_thread.join()
        debug.log("Goodbye!")
        raise urwid.ExitMainLoop()

    def on_file_selected(selected_file):
        """Handle file selection: start MPV and return to the menu."""
        loop.widget = menu  # Return to the menu
        if selected_file:
            mpv_manager.video_file = selected_file
            mpv_manager.start_mpv()
            if mpv_manager.process:
                mpv_manager.process.wait()  # Wait for MPV to exit

            # Force terminal cleanup and redraw
            loop.screen.clear()
            loop.draw_screen()

    def on_browser_exit():
        # Return to menu without selecting a file
        loop.widget = menu

    def on_help():
        """Show the Help page."""
        help_page = HelpPage(on_exit_callback=switch_to_menu)
        loop.widget = help_page  # Switch to the Help Page

    # Initialize menu and folder browser
    menu = Menu(on_select_file, on_help, on_about, on_quit, mpv_manager=mpv_manager)
    folder_browser = FolderBrowser(
        start_dir=config["filem_start_path"],
        ext_filters=config["filem_ext_filters"].split(","),
        show_hidden=config["filem_show_hidden"] == "True",
        on_file_selected=lambda path: (setattr(mpv_manager, "video_file", path), mpv_manager.start_mpv(), switch_to_menu()),
        on_exit=switch_to_menu
    )

    palette = [
        ('folder', 'light green', 'black'),
        ('focus', 'standout', 'black'),
        ('header', 'white,bold', 'dark blue'),
        ('footer', 'yellow', 'black')
    ]

    # Run a single main loop
    global loop
    loop = urwid.MainLoop(menu, palette=palette)
    loop.run()

if __name__ == "__main__":
    main()
