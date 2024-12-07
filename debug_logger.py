import os

class Debug:
    """A class for logging debug messages to a file."""
    def __init__(self, log_file="debug.log"):
        self.log_file = log_file
        # Reset the log file (clear content) on app startup
        with open(self.log_file, "w") as f:
            f.write("=== Debug Log Initialized ===\n")

    def log(self, message):
        """Write a message to the debug log."""
        with open(self.log_file, "a") as f:
            f.write(f"{message}\n")

    def log_exception(self, exception):
        """Log exceptions or errors."""
        with open(self.log_file, "a") as f:
            f.write(f"EXCEPTION: {exception}\n")