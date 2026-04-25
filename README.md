# Project Documentation: Arducam 64MP Timelapse Monitor

This project is an updated version of Ryan Gill's solution for resin 3D printer timelapses. This particular project describes a high-resolution timelapse capture system for the **Arducam 64MP Hawkeye** sensor, managed via **PM2** for 24/7 uptime.

---

## 1. System Overview
The system uses a Raspberry Pi coupled with the Arducam 64MP sensor. It captures full-resolution ($9152 \times 6944$) images when a signal is received, automatically organizing files into time-stamped subdirectories if a 5-minute capture interval is exceeded.



---

## 2. Prerequisites & Driver Installation
Because the Arducam 64MP Hawkeye uses a custom "Pivariety" driver rather than standard upstream kernel support, you must perform these setup steps. **Note:** Major system updates (`sudo apt upgrade`) may overwrite these drivers.

### A. Driver Installation
1.  **Download:** `wget -O install_pivariety_pkgs.sh https://github.com/ArduCAM/Arducam-Pivariety-V4L2-Driver/releases/download/install_script/install_pivariety_pkgs.sh`
2.  **Make Executable:** `chmod +x install_pivariety_pkgs.sh`
3.  **Install:** `sudo ./install_pivariety_pkgs.sh -p 64mp_pi_hawk_eye_kernel_driver`

### B. System Configuration
1.  **Edit Config:** `sudo nano /boot/firmware/config.txt`
2.  **Add Overlay:** Append `dtoverlay=arducam-64mp` to the end of the file.
3.  **Reboot:** `sudo reboot` to initialize the hardware.

### C. Sensor Tuning (IPA) Database
If you receive "no static properties available," the system cannot find the sensor profile. Ensure `arducam_64mp.json` exists in `/usr/share/libcamera/ipa/raspberrypi/`. If it is missing, download it directly:
```bash
sudo wget -O /usr/share/libcamera/ipa/raspberrypi/arducam_64mp.json https://raw.githubusercontent.com/ArduCAM/Arducam-Pivariety-V4L2-Driver/master/v4l2_config/arducam_64mp.json
```



---

## 3. Script: `timelapse.py`

```python
from gpiozero import Button
from signal import pause
import time
import subprocess
import os

# Config
BASE_PATH = "YOUR/PATH/HERE"
last_capture_time = 0
current_subfolder = ""

def get_new_folder():
	folder_name = time.strftime("%Y-%m-%d_%H-%M-%S")
	path = os.path.join(BASE_PATH, folder_name)
	os.makedirs(path, exist_ok=True)
	return path

def capture():
	global last_capture_time, current_subfolder
	now = time.time() * 1000

	if (now - last_capture_time) > 300000 or not current_subfolder:
		print("Pause detected or first capture. Creating new folder...")
		current_subfolder = get_new_folder()

	last_capture_time = now
	image_path = os.path.join(current_subfolder, f'image_{int(round(now))}.jpg')

	print (f"Focusing and capturing to {image_path}...")

cmd = [
		"rpicam-still",
		"-t", "2000",
		"--width", "9152",
		"--height", "6944",
		"--autofocus-on-capture",
		"--camera", "0",
		"--nopreview",
		"-o", image_path
	]

	try:
		subprocess.run(cmd, check=True)
		print(f'Image captured: {current_time}')

	except subprocess.CalledProcessError as e:
		print(f"Failed to cpature image: {e}")

button = Button(14)
button.when_pressed = capture
print("64MP Timelapse Monitor Running. Awaiting Signal...")
pause()
```

---

## 4. PM2 Process Management
PM2 ensures the script runs in the background and restarts automatically.

* **Install:** `sudo npm install pm2 -g`
* **Start:** `pm2 start ~/scripts/timelapse.py --interpreter python3 --name "timelapse-monitor"`
* **Startup/Save:** `pm2 save && pm2 startup`


