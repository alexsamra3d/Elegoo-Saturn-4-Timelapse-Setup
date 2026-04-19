# Elegoo-Saturn-4-Timelapse-Setup
A lightweight timelapse setup for the Elegoo Saturn 4 using a Raspberry Pi 4B, Arducam Hawkeye 64MP camera module, and a phototransistor module.

# Project Documentation: Arducam 64MP Timelapse Monitor

This project provides a phototransistor triggered timelapse capture system using the **Arducam 64MP Hawkeye** sensor, managed via **PM2** for 24/7 reliability on Raspberry Pi.

---

## 1. System Overview
The system uses a Raspberry Pi (running Raspberry Pi OS) coupled with the Arducam 64MP sensor. It captures full-resolution ($9152 \times 6944$) images when a digital signal is received from the phototransistor. To ensure organized storage, the system automatically creates time-stamped subdirectories if the interval between captures exceeds 5 minutes.



---

## 2. Script: `timelapse.py`
The script uses `gpiozero` for hardware interaction and `subprocess` to call the `rpicam-still` utility.

```python
import time
import os
import subprocess
from gpiozero import Button
from signal import pause

# --- Configuration ---
BASE_PATH = "/home/alex/pictures"
last_capture_time = 0
current_subfolder = ""

def get_new_folder():
    """Generates a folder name based on the current date."""
    folder_name = time.strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(BASE_PATH, folder_name)
    os.makedirs(path, exist_ok=True)
    return path

def capture():
    global last_capture_time, current_subfolder
    now = time.time() * 1000
    
    # Create new folder if > 5 minutes (300,000 ms) since last capture
    if (now - last_capture_time) > 300000 or not current_subfolder:
        current_subfolder = get_new_folder()
    
    last_capture_time = now
    image_path = os.path.join(current_subfolder, f'image_{int(now)}.jpg')

    cmd = [
        "rpicam-still",
        "-t", "2000",
        "--width", "9152",
        "--height", "6944",
        "--autofocus-on-capture",
        "--nopreview",
        "-o", image_path
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to capture: {e}")

button = Button(14)
button.when_pressed = capture
pause()
```

---

## 3. PM2 Process Management
PM2 ensures the script restarts automatically on reboot and stays running in the background.

### Installation
```bash
sudo npm install pm2 -g
```

### Deployment Commands
* **Start:** `pm2 start ~/scripts/timelapse.py --interpreter python3 --name "timelapse-monitor"`
* **Save configuration (on boot):** `pm2 save && pm2 startup`
* **Check Logs:** `pm2 logs timelapse-monitor`
* **Restart:** `pm2 restart timelapse-monitor`

---

## 4. Maintenance & Troubleshooting

### Updating Drivers
Because the Arducam Hawkeye uses a custom kernel driver, system updates may break the camera connection. If `rpicam-still --list-cameras` returns "No cameras available," re-run the driver installer:
```bash
# Navigate to your installer script folder
sudo ./install_pivariety_pkgs.sh -p 64mp_pi_hawk_eye_kernel_driver
```

### File Permission Management
If you encounter "Permission denied" errors, ensure your user owns the destination directory:
```bash
sudo chown -R $USER:$USER /home/alex/pictures
chmod 775 /home/alex/pictures
```

### Hardware Verification
* **Ribbon Cable:** Ensure the camera cable is seated firmly with the blue/black pull-tab facing the correct orientation.
* **Kernel Module:** Verify the driver is loaded using `lsmod | grep arducam`.

---

## 5. Storage Optimization
The 64MP sensor produces very large files (~20MB+). It is recommended to implement a cron job to move older images to an external drive or cloud storage to prevent SD card overflow:
```bash
# Example command to move files older than 30 days
find /home/alex/pictures -type f -mtime +30 -exec mv {} /mnt/usb/archive/ \;
```

---

How would you like to handle long-term storage backups for these 64MP files, or would you like to explore setting up a remote dashboard to monitor the status of the camera?
