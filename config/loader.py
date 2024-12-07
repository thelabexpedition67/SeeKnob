import json
import os

def load_config(config_path="config.json"):
    """Load the configuration file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as file:
        return json.load(file)