import urwid
from debug_logger import Debug

debug = Debug()  # Initialize Debug logger

class MenuItem(urwid.Button):
    """Custom Menu Item with a callback."""
    def __init__(self, label, on_press_callback):
        super().__init__(label, on_press=on_press_callback)

def menu_button(label, on_press_callback):
    """Helper to create MenuItem."""
    return MenuItem(label, on_press_callback)

class Menu:
    def __init__(self, on_select_file, on_help, on_about, on_quit):
        """
        Initialize the main menu.

        :param on_select_file: Callback for Select File option.
        :param on_help: Callback for Help option.
        :param on_about: Callback for About option.
        :param on_quit: Callback for Quit option.
        """
        self.on_select_file = on_select_file
        self.on_help = on_help
        self.on_about = on_about
        self.on_quit = on_quit

        # Menu buttons with callbacks
        select_file_btn = menu_button("Select File From Filesystem", lambda button: self.on_select_file())
        help_btn = menu_button("Help", lambda button: self.on_help())
        about_btn = menu_button("About", lambda button: self.on_about())
        quit_btn = menu_button("Quit", lambda button: self.on_quit())

        # List of menu items
        menu_items = [select_file_btn, help_btn, about_btn, quit_btn]

        # Menu layout
        self.list_walker = urwid.SimpleFocusListWalker(menu_items)
        menu_listbox = urwid.ListBox(self.list_walker)
        footer_text = urwid.Text("SeeKnob - TheLabExpedition67", align='right')
        self.view = urwid.LineBox(
            urwid.Frame(menu_listbox, footer=footer_text), title="Main Menu"
        )

    def widget(self):
        """Return the main menu widget."""
        return self.view