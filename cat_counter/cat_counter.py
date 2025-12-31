import os
import cv2
import json
import base64
import time
import paho.mqtt.client as mqtt
from inference_sdk import InferenceHTTPClient


INTERVAL = 300  # Update every 5 minutes
last_image_time = 0 
last_cat_count = -1 #Avoiding multiple MQTT messages if there is no change

mqtt_client = mqtt.Client()
mqtt_client.connect("mosquitto", 1883, 60)
cap = cv2.VideoCapture(0)

#They key is stored seperately
ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY")
CLIENT = InferenceHTTPClient(api_url="http://roboflow-inference:9001", api_key=ROBOFLOW_API_KEY)

# print("Initialization complete")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # Using yolov8n
    result = CLIENT.infer(frame, model_id="yolov8n-640")
    predictions = result.get("predictions", [])
    
    # Count the number of cats in the predictions
    cat_count = len([p for p in predictions if p['class'] == 'cat'])

    current_time = time.time()
    should_send_mqtt = False
    image_payload = None

    # Send an image in case the count of cats changes
    if cat_count != last_cat_count:
        should_send_mqtt = True
        last_cat_count = cat_count

    if cat_count > 0 and (current_time - last_image_time >= INTERVAL):
       # Resize and encode the image for MQTT payload--Not the most efficient or the best way to do it
        resized_frame = cv2.resize(frame, (640, 360))
        _, buffer = cv2.imencode('.jpg', resized_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        image_payload = base64.b64encode(buffer).decode('utf-8')
        
        last_image_time = current_time
        should_send_mqtt = True 

    # Publish message
    if should_send_mqtt:
        payload = {
            "count": cat_count,  
            "image": image_payload,
            "last_capture": time.ctime(last_image_time) if last_image_time > 0 else "Waiting..."
        }
        # Added message retention
        mqtt_client.publish("jetson/inference/cats", json.dumps(payload), retain=True)

cap.release()