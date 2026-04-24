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
