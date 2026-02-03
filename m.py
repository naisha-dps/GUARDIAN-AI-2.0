import os
import sys

# --- THE "EXIT CODE -4" FIXES ---
# These must be at the VERY top before any other imports
os.environ["OPENBLAS_CORETYPE"] = "ARMV8"
os.environ["LD_PRELOAD"] = "/usr/lib/aarch64-linux-gnu/libgomp.so.1"

import cv2
import time
from ultralytics import YOLO

# --- CONFIGURATION ---
TARGET_CLASSES = [15, 16, 17, 18, 19, 20, 21, 22]
LED_PIN = 17      
BUZZER_PIN = 27   
SOUND_FILE = "alert.wav.wav"  
sound_cooldown = 0
COOLDOWN_TIME = 3.0  

# --- HARDWARE SETUP ---
try:
    import RPi.GPIO as GPIO
    ON_RASPBERRY_PI = True
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    print("✅ Raspberry Pi Hardware Detected: GPIO Active")
except (ImportError, RuntimeError):
    ON_RASPBERRY_PI = False
    print("⚠️ Laptop Mode: Simulating Hardware")

def trigger_alert(enable, animal_name="Target"):
    global sound_cooldown
    if enable:
        if ON_RASPBERRY_PI:
            GPIO.output(LED_PIN, GPIO.HIGH)
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
        
        if time.time() - sound_cooldown > COOLDOWN_TIME:
            print(f"🚨 ALARM TRIGGERED! Detected: {animal_name}")
            if ON_RASPBERRY_PI:
                os.system(f"aplay -q {SOUND_FILE} &")
            sound_cooldown = time.time()
    else:
        if ON_RASPBERRY_PI:
            GPIO.output(LED_PIN, GPIO.LOW)
            GPIO.output(BUZZER_PIN, GPIO.LOW)

# --- AI MODEL STARTUP ---
print("⏳ Loading YOLOv8 Model...")
model = YOLO('yolov8n.pt')

print("📷 Opening Camera...")
# Try multiple camera indexes in case 0 is busy
for idx in [0, -1, 1]:
    cap = cv2.VideoCapture(idx)
    if cap.isOpened():
        print(f"✅ Camera found on index {idx}")
        break

cap.set(3, 640) 
cap.set(4, 480) 

if not cap.isOpened():
    print("❌ Error: Camera not found!")
    sys.exit()

print(f"🚀 SYSTEM ARMED. Audio File: {SOUND_FILE}")

# --- MAIN LOOP ---
try:
    while True:
        ret, frame = cap.read()
        if not ret: break

        results = model(frame, stream=True, verbose=False, conf=0.5)
        
        threat_detected = False
        animal_name = ""

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls in TARGET_CLASSES:
                    threat_detected = True
                    animal_name = model.names[cls].upper()
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.putText(frame, f"THREAT: {animal_name}", (x1, y1-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        trigger_alert(threat_detected, animal_name)
        cv2.imshow("Guardian AI View", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    if ON_RASPBERRY_PI:
        GPIO.cleanup()