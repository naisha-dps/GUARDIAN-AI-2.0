🛡️ Guardian AI: Animal Detection System
A real-time animal detection and alert system built for Raspberry Pi. This project uses YOLOv8 to identify specific animals (dogs, cats, bears, etc.) and triggers a hardware alarm (LED + Buzzer) and an audio siren when a threat is detected.

✨ Features
Real-time Detection: Uses Ultralytics YOLOv8 for high-speed object tracking.

Target Specificity: Only alerts on specific animal classes (COCO dataset).

Dual-Alert System: Simultaneous visual (LED), haptic (Buzzer), and audio (aplay) alerts.

Hardware Integrated: Built-in support for RPi.GPIO pins.

Auto-Correction: Environment variables included to prevent "Exit Code -4" crashes on ARM processors.

🛠️ Hardware Requirements
Raspberry Pi (4 or 5 recommended)

USB Camera or Raspberry Pi Camera Module

LED (Connected to GPIO 17)

Active Buzzer (Connected to GPIO 27)

Speaker (For audio alerts)


Shutterstock
🚀 Installation & Setup
1. Clone the Repository
Bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
2. Install System Dependencies
The modern Raspberry Pi OS requires specific graphics and math libraries:

Bash
sudo apt update
sudo apt install libgl1 libgomp1 -y
3. Install Python Packages
To avoid crashes on the Pi, you must install the CPU-optimized version of Torch:

Bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --break-system-packages
pip install ultralytics "numpy<2" --break-system-packages
🖥️ Usage
Ensure your audio file is named alert.wav.wav and is in the same folder as the script.

Run the main script:

Bash
python main.py
Press 'q' to stop the program and cleanup GPIO pins.

🔧 Troubleshooting (The "Exit Code -4" Fix)
If the program crashes with Process ended with exit code -4, ensure these lines are at the very top of your main.py:

Python
import os
os.environ["OPENBLAS_CORETYPE"] = "ARMV8"
os.environ["LD_PRELOAD"] = "/usr/lib/aarch64-linux-gnu/libgomp.so.1"
