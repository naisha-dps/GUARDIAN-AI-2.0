import cv2
import time
import os
import sys
from ultralytics import YOLO

# --- CONFIGURATION ---
# Target Animals (COCO ID): 15=Cat, 16=Dog, 17=Horse, 18=Sheep, 19=Cow, 20=Elephant, 21=Bear
TARGET_CLASSES = [15, 16, 17, 18, 19, 20, 21, 22]

# Hardware Pins (BCM Mode)
LED_PIN = 17      # Physical Pin 11
BUZZER_PIN = 27   # Physical Pin 13

# Audio Settings - UPDATED FOR YOUR FILE NAME
SOUND_FILE = "alert.wav.wav"  # <--- CHANGED HERE
sound_cooldown = 0
COOLDOWN_TIME = 3.0  # Seconds to wait between screams

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
    print("⚠️ Laptop Mode: Simulating Hardware (No real LED/Buzzer)")

def trigger_alert(enable, animal_name="Target"):
    """Handles LED, Buzzer, and Sound simultaneously"""
    global sound_cooldown

    if enable:
        # 1. VISUAL & HAPTIC: Turn on LED and Buzzer
        if ON_RASPBERRY_PI:
            GPIO.output(LED_PIN, GPIO.HIGH)
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
        
        # 2. AUDIO: Play sound
        # We check cooldown so we don't crash the audio driver
        if time.time() - sound_cooldown > COOLDOWN_TIME:
            print(f"🚨 ALARM TRIGGERED! Detected: {animal_name}")
            
            if ON_RASPBERRY_PI:
                # 'aplay' is the built-in command line audio player for Pi
                # The '&' symbol runs it in background so video doesn't freeze
                os.system(f"aplay -q {SOUND_FILE} &")
            else:
                # For Windows testing
                try:
                    import winsound
                    winsound.PlaySound(SOUND_FILE, winsound.SND_ASYNC)
                except:
                    print(f"❌ Error: Could not find {SOUND_FILE}")
            
            sound_cooldown = time.time()
            
    else:
        # Turn everything OFF
        if ON_RASPBERRY_PI:
            GPIO.output(LED_PIN, GPIO.LOW)
            GPIO.output(BUZZER_PIN, GPIO.LOW)

# --- AI MODEL STARTUP ---
print("⏳ Loading YOLOv8 Model...")
model = YOLO('yolov8n.pt')

print("📷 Opening Camera...")
cap = cv2.VideoCapture(0)
cap.set(3, 640) # Width
cap.set(4, 480) # Height

if not cap.isOpened():
    print("❌ Error: Camera not found!")
    sys.exit()

print(f"🚀 SYSTEM ARMED. Audio File: {SOUND_FILE}")

# --- MAIN LOOP ---
while True:
    ret, frame = cap.read()
    if not ret: break

    # Run Detection
    results = model(frame, stream=True, verbose=False, conf=0.5)
    
    threat_detected = False
    animal_name = ""

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if cls in TARGET_CLASSES:
                threat_detected = True
                animal_name = model.names[cls].upper()
                
                # Draw Red Box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(frame, f"THREAT: {animal_name}", (x1, y1-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Trigger or Reset Alarm
    if threat_detected:
        trigger_alert(True, animal_name)
    else:
        trigger_alert(False)

    # Show Feed
    cv2.imshow("Guardian AI View", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
if ON_RASPBERRY_PI:
    GPIO.cleanup()