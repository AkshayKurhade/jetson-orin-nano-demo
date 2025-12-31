import os
import time
import json
import logging
from logging.handlers import RotatingFileHandler
import paho.mqtt.client as mqtt
from jtop import jtop

# --- CONFIGURATION ---
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_TOPIC = "jetson/health/orin_nano"
LOG_FILE_PATH = "/app/logs/jetson_health.log"

# --- LOGGER SETUP ---
# Create logs directory if it doesn't exist (handled by Docker volume usually)
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=10*1024*1024, backupCount=3) # 10MB per file
logger = logging.getLogger("JetsonHealth")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def get_stats(jetson):
    stats = jetson.stats
    temps = jetson.temperature
    cpu_cores = stats.get('CPU', [])
    cpu_avg = sum(cpu_cores) / len(cpu_cores) if cpu_cores else 0
    #temps = stats.get('TEMP', {})
    # temps are no longer under stats.get
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "hardware": {
            "power_mode": jetson.nvpmodel.name if jetson.nvpmodel else "Unknown",
            #"temp_cpu": temps.get('CPU', 0),
            #"temp_gpu": temps.get('GPU', 0),
            "temp_cpu" : temps.get('cpu', {}).get('temp'),
            "temp_gpu" : temps.get('gpu', {}).get('temp'),
            "power_mw": stats.get('power', [{}])[0].get('cur', 0)
        },
        "load": {
            "cpu_avg": round(cpu_avg, 2),
            "gpu_util": stats.get('GPU', 0),
            "ram_util": round((stats.get('RAM', 0) / stats.get('tot RAM', 1)) * 100, 2)
        }
    }

if __name__ == "__main__":
    # Setup MQTT
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    
    try:
        print(f"Connecting to Broker: {MQTT_BROKER}...")
        client.connect(MQTT_BROKER, 1883, 60)
        client.loop_start()
        
        with jtop() as jetson:
            while jetson.ok():
                data = get_stats(jetson)
                payload = json.dumps(data)
                
                # Log to File (Rotating)
                logger.info(payload)
                
                #  Publish to MQTT
                client.publish(MQTT_TOPIC, payload)
                
                # Print to Console (for 'docker logs')
                print(f"Health Check: CPU {data['hardware']['temp_cpu']}°C | GPU {data['load']['gpu_util']}%")
                
                time.sleep(10)
    except Exception as e:
        print(f"System Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()