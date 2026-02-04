# 🛡️ Guardian AI 2.0

**Guardian AI** is an intelligent, real-time intrusion detection system designed for the **Raspberry Pi 5**. It uses computer vision (YOLOv8) to detect specific threats (like wild animals) and triggers physical deterrents immediately.

## 🚀 Features
* **Real-Time AI Detection:** Uses a YOLOv8 Nano model (ONNX format) for fast inference on the Raspberry Pi CPU.
* **Hardware Deterrents:** Automatically triggers a flashing LED and Piezo Buzzer upon detection.
* **Audio Warnings:** Plays loud alarm sounds via **Bluetooth Speaker** to scare off intruders.
* **Remote Monitoring:** Supports **VNC Viewer** for live video feed monitoring from laptops, phones, or tablets.
* **Pi 5 Optimized:** Specifically written to handle the new RP1 GPIO architecture (using `lgpio` and Chip 4).

---

## 🛠️ Hardware Requirements
* **Raspberry Pi 5** (4GB or 8GB RAM recommended)
* **Raspberry Pi Camera Module 3** (or standard USB Webcam)
* **Bluetooth Speaker** (for loud audio alerts)
* **Active Buzzer & LED** (connected to GPIO pins)
* **Breadboard & Jumper Wires**

### **Wiring Diagram (GPIO Chip 4)**
| Component | Pi 5 Pin (Physical) | GPIO Number (Code) |
| :--- | :--- | :--- |
| **LED** (+) | Pin 11 | GPIO 17 |
| **Buzzer** (+) | Pin 13 | GPIO 27 |
| **Ground** (-) | Pin 6 or 9 | GND |

---

## 📦 Installation

### **1. System Dependencies**
Ensure your Raspberry Pi is up to date and has the necessary audio/GPIO tools.
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-opencv python3-pip libopenblas-dev pulseaudio-utils bluetooth pi-bluetooth -y

2. Python Libraries
Install the required Python packages (best done in a virtual environment).

Bash
pip3 install opencv-python-headless onnxruntime numpy lgpio
3. Audio Setup (Bluetooth)
Pair your speaker using bluetoothctl.

Test the connection:

Bash
paplay --device bluez_output.XX_XX_XX_XX.1 /path/to/alert.wav
🏃 Usage
Running the System
Navigate to the project directory and run the main script:

Bash
python3 guardian_onnx.py
Remote Monitoring (VNC)
To view the live camera feed from another device:

Enable VNC on the Pi: sudo raspi-config > Interface Options > VNC.

Install RealVNC Viewer on your laptop or phone.

Connect using the Pi's IP address (find it using hostname -I).

⚙️ Configuration
You can customize the system by editing the guardian_onnx.py file:

TARGET_CLASSES: Change which objects trigger the alarm (e.g., Cat, Dog, Bear).

CONFIDENCE_THRESHOLD: Adjust sensitivity (Default: 0.5).

SOUND_FILE: Path to your .wav file.

COOLDOWN_TIME: How many seconds to wait between alarm blasts.

Python
# Example Configuration in code
TARGET_CLASSES = [15, 16, 17]  # COCO IDs for Cat, Dog, Horse
SOUND_FILE = "/home/guardianai/guardian_pi/alert.wav"
⚠️ Troubleshooting
1. "gpiochip_open failed"

Ensure you are using chip_handle = lgpio.gpiochip_open(4) for Raspberry Pi 5. Older Pis use Chip 0.

2. Audio not playing

Check Bluetooth connection: bluetoothctl info

Ensure PulseAudio is running: pulseaudio --start

Verify the filename matches exactly in the code.

3. VNC shows a black screen

If the camera preview doesn't appear, try running the script directly from the desktop terminal, not SSH.
