# SeeKnob - A Knob-Based Media Controller

SeeKnob is a powerful and precise media control tool that transforms your rotary knob and dedicated buttons into a seamless video navigation system.

SeeKnob works only on Linux (at the moment) and allows you to control video playback effortlessly, set marker points, and fine-tune seek precision. Whether you're a media enthusiast, developer, or tinkerer, SeeKnob offers unmatched control over your media.

---

## Features

- **File Browser**: Browse your filesystem and select video files.
- **Knob Navigation**: Use a rotary knob for precise seeking forward/backward.
- **Dynamic Seek Step**: Increase or decrease seek step size with buttons.
- **Marker Points**: Set marker points and replay them instantly.
- **Customizable Controls**: Configure knob, buttons, and key mappings.
- **MPV Integration**: Seamlessly control video playback using MPV.
- **Cross-Monitor Fullscreen**: Choose which screen MPV launches on.
- **Lightweight and Fast**: Runs smoothly even on non-GUI systems.

---

## Installation

### Prerequisites
- Python 3.x
- MPV Media Player (Required)
- evdev library (for reading knob and button inputs)
- udev rule configuration (for managing devices in Linux)

### Install MPV

Follow these steps to install MPV based on your operating system:

- **Debian/Ubuntu**:
  ```bash
  sudo apt update
  sudo apt install mpv
  ```
- **Red Hat/CentOS/Fedora**:
  ```bash
  sudo dnf install mpv
  ```
- **Arch Linux**:
  ```bash
  sudo pacman -S mpv
  ```

### Installation

1. **Clone the Repository**:
  ```bash
  git clone https://github.com/thelabexpedition67/SeeKnob.git
  cd SeeKnob
  ```
2. **Create a Virtual Environment (Recommended)**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
3. **Install Dependencies**:
  ```bash
  pip install -r requirements.txt
  ```
4. **Set permissions**:
  ```bash
  chmod +x run.sh
  ```
## Configuration

SeeKnob is customizable via a `config.json` file. Below is an example:

```json
{
    "devices": {
      "knob_device": "/dev/input/by-id/usb-8808_6613-if02-event-kbd",
      "buttons_device": "/dev/input/by-id/usb-8808_6613-event-kbd"
    },
    "default_seek_step": 0.5,
    "key_mappings": {
      "seek_forward": "KEY_VOLUMEUP",
      "seek_backward": "KEY_VOLUMEDOWN",
      "toggle_pause": "KEY_PLAYPAUSE",
      "decrease_seek_step": "KEY_1",
      "increase_seek_step": "KEY_2",
      "set_marker": "KEY_3",
      "play_marker": "KEY_4"
    },
    "filem_ext_filters": "AVI,avi,mp4",
    "filem_show_hidden": "False",
    "filem_start_path": "/",
    "mpv_full_screen": "True",
    "mpv_fs_screen": "0",
    "mpv_socket": "/tmp/mpv-socket"
}
```

### Key Configuration Options:

- **devices**: Paths for your knob and button devices (use `/dev/input/by-id/` for stability).
- **default_seek_step**: Initial seek step size in seconds.
- **key_mappings**: Map physical keys to actions like seeking and toggling pause.
- **filem_ext_filters**: Allowed video file extensions.
- **mpv_full_screen**: Launch MPV in fullscreen.
- **mpv_fs_screen**: Specify the monitor index for fullscreen playback.

---

## Blocking System from Managing USB Devices

If your knob or buttons are being managed by the system (e.g., adjusting volume), create a udev rule to block the default behavior.

1. **Identify the USB Device**:
   ```bash
   lsusb
   ```

2. **Find the Device Path**:
   ```bash
   ls -l /dev/input/by-id/
   ```

3. **Create a udev Rule**:
   ```bash
   sudo nano /etc/udev/rules.d/99-block-usb.rules
   ```

   Add the following line, replacing `VENDOR_ID` and `PRODUCT_ID` with your device IDs:
   ```
   ACTION=="add|change", ATTRS{idVendor}=="VENDOR_ID", ATTRS{idProduct}=="PRODUCT_ID", ENV{ID_INPUT}="", ENV{ID_INPUT_KEY}=""
   ```

4. **Reload the Rules**:
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

5. **Verify**: Ensure the system no longer manages the device.

---

## Usage

1. **Run the Application**:
   ```bash
   source venv/bin/activate
   python3 main.py
   ```
   or
   ```bash
   ./run.sh
   ```
2. Use the **Menu** to:
   - Select files from the filesystem.
   - Access Help and About pages.
   - Quit the application.

3. **Controls**:
   - Use the knob to seek forward/backward.
   - Buttons for increasing/decreasing seek step and managing marker points.
   - To exit from the video player, just press 'q'

---

## License

This project is licensed under the MIT License.

---