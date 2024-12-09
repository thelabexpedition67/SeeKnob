import urwid
from debug_logger import Debug

debug = Debug()  # Initialize Debug logger

class MenuItem(urwid.Button):
    """Custom Menu Item with a callback."""
    def __init__(self, label, on_press_callback):
        super().__init__(label, on_press=on_press_callback)

def menu_button(label, on_press_callback):
    """Helper to create MenuItem."""
    return urwid.AttrMap(MenuItem(label, on_press_callback), None, focus_map='focus')

class Menu(urwid.WidgetWrap):
    def __init__(self, on_select_file, on_help, on_about, on_quit, mpv_manager):
        self.on_select_file = on_select_file
        self.on_help = on_help
        self.on_about = on_about
        self.on_quit = on_quit
        self.mpv_manager = mpv_manager

        menu_items = [
            menu_button("Select File From Filesystem", lambda _: self.on_select_file()),
            menu_button("Help", lambda _: self.on_help()),
            menu_button("About", lambda _: self.on_about()),
            menu_button("Quit", lambda _: self.on_quit())
        ]

        self.list_walker = urwid.SimpleFocusListWalker(menu_items)
        menu_listbox = urwid.ListBox(self.list_walker)
        footer_text = urwid.Text("SeekKnob - TheLabExpedition67", align='right')
        main_frame = urwid.Frame(menu_listbox, footer=footer_text)
        menu_box = urwid.LineBox(main_frame, title="Main Menu")

        super().__init__(menu_box)

    def keypress(self, size, key):
        if key in ('q', 'Q'):
            if self.mpv_manager.is_running():
                self.mpv_manager.quit_mpv()
                debug.log("MPV closed via 'q'.")
            else:
                debug.log("MPV is not running.")
            return None  # Key handled
        return super().keypress(size, key)