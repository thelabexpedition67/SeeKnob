import urwid
from debug_logger import Debug

debug = Debug()  # Initialize Debug logger

class AboutPage(urwid.WidgetWrap):
    def __init__(self, on_exit_callback):
        """
        About Page with information about the application.
        :param on_exit_callback: Function to call when exiting back to the menu.
        """
        self.on_exit_callback = on_exit_callback

        # Header text
        header = urwid.Text("About SeeKnob", align='center')
        header = urwid.AttrMap(header, 'header')

        # Body content
        about_text = (
            "=== SeeKnob ===\n"
            "The Ultimate Knob-Based Media Controller\n\n"
            "Developed by TheLabExpedition67\n\n"
            "SeeKnob transforms your rotary knob into a precise media control tool,\n"
            "making video navigation seamless and efficient.\n\n"
            "Features:\n"
            "  - Browse your filesystem to select video files effortlessly.\n"
            "  - Control video playback using your knob and dedicated buttons.\n"
            "  - Set and replay marker points with pinpoint accuracy.\n"
            "  - Adjust seek step size dynamically for ultimate precision.\n\n"
            "With SeeKnob, you're in complete control of your media.\n\n"
            "Press 'Esc' or 'q' to return to the main menu."
        )

        body = urwid.Text(about_text, align='left')

        # Footer
        footer = urwid.Text("Press 'Esc' or 'q' to go back.", align='center')
        footer = urwid.AttrMap(footer, 'footer')

        # Layout
        content = urwid.Pile([
            ('pack', header),
            ('weight', 1, urwid.Filler(body, valign='top')),
            ('pack', footer)
        ])
        main_view = urwid.LineBox(content, title="About")

        # Wrap the widget
        super().__init__(main_view)

    def selectable(self):
        # Make this widget selectable so it can receive focus and keypresses
        return True

    def keypress(self, size, key):
        """Handle keypresses for navigation."""
        if key in ('esc', 'q'):
            debug.log("Esc or Q pressed. Returning to main menu.")
            self.on_exit_callback()  # Return to the main menu
            return None  # Key handled, stop processing

        # Ignore other keys
        return None
