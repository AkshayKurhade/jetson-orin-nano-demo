import cv2
import numpy as np
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import json
import time
import signal
import sys
import time
from pyModbusTCP.client import ModbusClient as ModbusBridge

# --- CONFIGURATION ---
PLC_IP = "10.2.1.19"  # Raspberry Pi IP
PLC_PORT = 502        # Standard Modbus Port
FAIL_COIL = 0         # Corresponds to %MX0.0

#Initialize Modbus Client
client_modbus = ModbusBridge(host=PLC_IP, port=PLC_PORT, auto_open=True)
# --- Configuration ---
BROKER = "mosquitto-broker"
TOPIC_STATS = "jetson/inference/stats"

# The EXACT pipeline you verified
GS_PIPELINE = (
    "v4l2src device=/dev/video0 ! "
    "video/x-raw, width=640, height=480, framerate=30/1 ! "
    "videoconvert ! "
    "appsink"
)

# MQTT Setup
client = mqtt.Client(CallbackAPIVersion.VERSION2)
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected to MQTT Broker with result code {rc}")
client.on_connect = on_connect

stats = {"pass_count": 0, "fail_count": 0}
cap = None

def graceful_shutdown(sig, frame):
    print("\n[INFO] Shutdown signal received. Cleaning up...")
    if cap and cap.isOpened():
        cap.release()
    client.loop_stop()
    client.disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

def classify_frame(frame):
    """Simple Color Classifier: Green=Pass, Red=Fail."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
    red_mask = cv2.inRange(hsv, (0, 70, 50), (10, 255, 255)) | cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))
    
    g_pix = cv2.countNonZero(green_mask)
    r_pix = cv2.countNonZero(red_mask)

    if g_pix > r_pix and g_pix > 10000: return "PASS"
    if r_pix > g_pix and r_pix > 10000: return "FAIL"
    return "IDLE"

def trigger_rejection():
    try:
        # Check if the attribute exists; if not, try the alternative 'write_coil'
        if hasattr(client_modbus, 'write_single_coil'):
            success = client_modbus.write_single_coil(0, True)
        elif hasattr(client, 'write_coil'):
            success = client_modbus.write_coil(0, True)
        else:
            #print(f"Available methods: {dir(client)}")
            return

        # if success:
        #     print("Rejection signal sent to PLC.")
        # else:
        #     print("PLC rejected the write request.")
            
    except Exception as e:
        print(f"Modbus communication error: {e}")


try:
    client.connect(BROKER, 1883, 60)
    client.loop_start()
    
    print(f"Initializing GStreamer pipeline on /dev/video0...")
    cap = cv2.VideoCapture(GS_PIPELINE, cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        print("Could not open video stream. Ensure no other apps are using /dev/video0.")
        sys.exit(1)

    print("Inference Server Running. Monitoring for Green/Red objects...")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: 
            print("Failed to grab frame.")
            break

        result = classify_frame(frame)
        
        if result != "IDLE":
            if result == "PASS": stats["pass_count"] += 1
            else: 
                
                stats["fail_count"] += 1
                #print("triggering")
                trigger_rejection()
            # Publish result to MQTT
            payload = {
                "status": result,
                "counts": stats,
                "timestamp": time.time()
            }
            client.publish(TOPIC_STATS, json.dumps(payload))
            print(f"RESULT: {result} | P: {stats['pass_count']} F: {stats['fail_count']}")

        time.sleep(0.5) 
except Exception as e:
    print(f"[FATAL ERROR] {e}")
finally:
    graceful_shutdown(None, None)