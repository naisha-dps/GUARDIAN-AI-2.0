cat << 'EOF' > ~/guardian_pi/guardian_onnx.py
import cv2
import numpy as np
import onnxruntime as ort
import os
import time
import subprocess
import lgpio  # Native Pi 5 Library

# --- CONFIGURATION ---
TARGET_CLASSES = [15, 16, 17, 18, 19, 20, 21]
CONFIDENCE_THRESHOLD = 0.5
MODEL_SIZE = 416

# Audio Settings (Matches your file exactly)
SOUND_FILE = "/home/guardianai/guardian_pi/alert.wav.wav"
SPEAKER_DEVICE = "bluez_output.41_42_9B_CD_D4_6C.1"
COOLDOWN_TIME = 5.0

CLASSES = {
    15: "CAT", 16: "DOG", 17: "HORSE", 18: "SHEEP",
    19: "COW", 20: "ELEPHANT", 21: "BEAR"
}

# --- HARDWARE SETUP (CHIP 4 for Pi 5) ---
chip_handle = None
ON_PI = False

try:
    print("🔌 Connecting to GPIO Chip 4 (Pi 5)...")
    chip_handle = lgpio.gpiochip_open(4)
    lgpio.gpio_claim_output(chip_handle, 17) # LED
    lgpio.gpio_claim_output(chip_handle, 27) # Buzzer
    ON_PI = True
    print("✅ Hardware Connected!")
except Exception as e:
    print(f"⚠️ Hardware Warning: {e}")

def set_hardware(state):
    """Turns LED and Buzzer ON/OFF"""
    if ON_PI and chip_handle is not None:
        val = 1 if state else 0
        lgpio.gpio_write(chip_handle, 17, val)
        lgpio.gpio_write(chip_handle, 27, val)

def play_alert():
    """Plays audio without freezing the video"""
    try:
        subprocess.Popen(["paplay", "--device", SPEAKER_DEVICE, SOUND_FILE])
    except Exception as e:
        print(f"⚠️ Audio Error: {e}")

# --- STARTUP TESTS ---
# 1. Hardware Reset
set_hardware(False)

# 2. Audio Test
print("🎵 Testing Audio (Listen for sound)...")
play_alert()
time.sleep(2)

# --- AI MODEL LOAD ---
print("⏳ Loading AI Model...")
model_path = "/home/guardianai/guardian_pi/yolov8n.onnx"
session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
input_name = session.get_inputs()[0].name
print("✅ Model Loaded!")

def preprocess(frame):
    img = cv2.resize(frame, (MODEL_SIZE, MODEL_SIZE))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).transpose((2, 0, 1))
    img = np.expand_dims(img, 0) / 255.0
    return img.astype(np.float32)

def postprocess(output, frame):
    output = output.transpose((0, 2, 1))
    boxes, scores, class_ids = [], [], []
    rows = output[0]
    h, w = frame.shape[:2]
    x_scale, y_scale = w/MODEL_SIZE, h/MODEL_SIZE

    for row in rows:
        if np.amax(row[4:]) >= CONFIDENCE_THRESHOLD:
            class_id = np.argmax(row[4:])
            if class_id in TARGET_CLASSES:
                x, y, w_box, h_box = row[:4]
                boxes.append([int((x-w_box/2)*x_scale), int((y-h_box/2)*y_scale), int(w_box*x_scale), int(h_box*y_scale)])
                scores.append(float(np.amax(row[4:])))
                class_ids.append(class_id)
   
    indices = cv2.dnn.NMSBoxes(boxes, scores, CONFIDENCE_THRESHOLD, 0.5)
    return [(boxes[i], class_ids[i]) for i in indices.flatten()] if len(indices) > 0 else []

last_alert_time = 0
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

print("🚀 GUARDIAN AI ARMED. Press 'q' to quit.")

try:
    while True:
        ret, frame = cap.read()
        if not ret: break

        outputs = session.run(None, {input_name: preprocess(frame)})[0]
        detections = postprocess(outputs, frame)
        threat = False
        animal_name = ""

        for (box, class_id) in detections:
            x, y, w, h = box
            animal_name = CLASSES.get(class_id, "Unknown")
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)
            cv2.putText(frame, f"THREAT: {animal_name}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            threat = True

        if threat:
            set_hardware(True)
            if time.time() - last_alert_time > COOLDOWN_TIME:
                print(f"🚨 ALARM TRIGGERED! {animal_name} detected!")
                play_alert()
                last_alert_time = time.time()
        else:
            set_hardware(False)

        cv2.imshow("Guardian AI", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

finally:
    cap.release()
    cv2.destroyAllWindows()
    if ON_PI:
        set_hardware(False)
        lgpio.gpiochip_close(chip_handle)
    print("System Shutdown.")
EOF
