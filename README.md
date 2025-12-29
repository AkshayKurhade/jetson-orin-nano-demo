# Jetson Orin Nano Demo
This Project intends to showcase use of various technologies and tools on an edge device. There are better ways to do many of the things done in this project, some of the technologies(like Node-RED) may not be at all required but are included for demonstration and my understanding


---

##  Overview

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Data Producer** | Python 3.10 + `jtop` | Direct hardware sensor access (CPU/GPU/RAM). |
| **Local Logger** | Python `csv` module | Use a local rotating logger to have failsafe but still save space |
| **Messaging** | Mosquitto (MQTT) | Decoupled communication between services. |
| **Node-RED** | Node-RED | Data transformation, UI Gauges, and DB Bridge. |
| **Database** | InfluxDB  | High-performance time-series data storage. |
| **Visualization** | Grafana | Dashboard,connects via Nodered Flow to the MQTT server |


---

## Installation & Setup

### 1. Host System Preparation
Before running the containers, the `jetson-stats` service must be istalled and active on your host Jetson to provide hardware access.

```bash
# Update system and install jtop service
sudo apt update && sudo apt install -y python3-pip
sudo pip3 install -U jetson-stats

# Reboot to initialize the jtop service and permissions
sudo reboot
```
### 2. Setup
The `setup.sh` file details steps necessary to recreate the setup

### 3. Node-RED setup
TODO

### 4. Grafana Setup
TODO


## Access
### Dashboard Access
Once the stack is running, you can access the various interfaces via your browser using the Jetson's IP address:

Node-RED Dashboard (Legacy): http://<JETSON_IP>:1880/ui

Grafana Dashboards: http://<JETSON_IP>:3000 (Default: admin/admin)

MQTT Explorer: Connect to mqtt://<JETSON_IP>:1883 

## Known Issues
- Some browsers refuse to connect to the dashboard servers
- The Node-Red Dashboard uses a deprecated module `node-red-dashboard`, alternative is `@flowfuse/node-red-dashboard`