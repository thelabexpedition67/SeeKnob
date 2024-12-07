import os
import urwid
from debug_logger import Debug

debug = Debug()  # Initialize Debug logger

class SelectableText(urwid.Text):
    def selectable(self):
        return True
    def keypress(self, size, key):
        return key

class FolderBrowser:
    def __init__(self, start_dir, ext_filters, show_hidden, on_file_selected, on_exit):
        self.current_dir = start_dir
        self.ext_filters = [e.lower() for e in ext_filters]  # Normalize extensions to lowercase
        self.show_hidden = show_hidden
        self.on_file_selected = on_file_selected
        self.on_exit = on_exit

        self.file_list = []
        self.header = urwid.Text("File Browser (Esc to exit, Enter to select)", align='center')
        self.footer = urwid.Text("", align='left')
        self.list_walker = urwid.SimpleFocusListWalker([])
        self.listbox = urwid.ListBox(self.list_walker)
        self.main_view = urwid.Frame(header=self.header, body=self.listbox, footer=self.footer, focus_part='body')

        self.update_file_list()

    def update_file_list(self):
        """Refresh the file list based on filters and visibility settings."""
        try:
            items = os.listdir(self.current_dir)
            self.file_list = [".."]  # Always include parent directory

            for item in sorted(items):
                if not self.show_hidden and item.startswith("."):
                    continue  # Skip hidden files if show_hidden is False

                full_path = os.path.join(self.current_dir, item)
                if os.path.isfile(full_path):
                    _, ext = os.path.splitext(item)
                    if ext.lower()[1:] not in self.ext_filters:  # Filter extensions
                        continue
                self.file_list.append(item)

            self.list_walker.clear()

            for item in self.file_list:
                full_path = os.path.join(self.current_dir, item)
                if os.path.isdir(full_path):
                    display_text = ("folder", f"[DIR] {item}")
                else:
                    display_text = f"      {item}"

                text_widget = SelectableText(display_text)  # Use SelectableText
                widget = urwid.AttrMap(text_widget, None, 'focus')  # Allow focus styling
                self.list_walker.append(widget)

            self.footer.set_text(f"Current Directory: {self.current_dir}")
        except Exception as e:
            self.footer.set_text(f"Error: {e}")


    def update_file_list_old_working(self):
        try:
            self.file_list = [".."] + [f for f in sorted(os.listdir(self.current_dir)) if not f.startswith(".")]
            self.list_walker.clear()

            for item in self.file_list:
                full_path = os.path.join(self.current_dir, item)
                if os.path.isdir(full_path):
                    display_text = ("folder", f"[DIR] {item}")
                else:
                    display_text = f"      {item}"
                text_widget = SelectableText(display_text)
                widget = urwid.AttrMap(text_widget, None, 'focus')
                self.list_walker.append(widget)

            self.footer.set_text(f"Current Directory: {self.current_dir}")
        except Exception as e:
            self.footer.set_text(f"Error: {e}")           

    def keypress(self, size, key):
        """Handle special keys and leave others unhandled."""
        if key in ('q', 'esc'):
            # Exit without selecting a file
            self.on_exit()
            return None
        if key == 'enter':
            focus_index = self.listbox.focus_position
            selected_item = self.file_list[focus_index]
            path = os.path.join(self.current_dir, selected_item)

            if os.path.isdir(path):
                self.current_dir = path
                self.update_file_list()
                self.listbox.focus_position = 0
            else:
                self.on_file_selected(path)
            return None

        # For arrows and other keys not handled above, return the key so that
        # it can be handled by the underlying widget (ListBox for navigation).
        return key

    def widget(self):
        return FolderBrowserIntercept(self)

class FolderBrowserIntercept(urwid.WidgetWrap):
    """
    Intercept keypresses and allow FolderBrowser a first chance to handle them.
    If FolderBrowser doesn't handle them, pass them to the underlying widget.
    """
    def __init__(self, fb):
        super().__init__(fb.main_view)
        self.fb = fb

    def keypress(self, size, key):
        # Let FolderBrowser handle q/enter if it wants
        res = self.fb.keypress(size, key)

        if res is None:
            # Key was handled by FolderBrowser
            return None
        else:
            # Key not handled by FolderBrowser, let the underlying widget handle it
            return super().keypress(size, res)
