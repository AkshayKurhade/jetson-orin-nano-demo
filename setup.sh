#!/bin/bash

echo "Starting Jetson Orin Nano Monitor Setup..."

# 1. Create Directory Structure
echo "Creating directories..."
mkdir -p monitor/logs
mkdir -p mosquitto/config
mkdir -p node-red-data
mkdir -p influxdb-data
mkdir -p grafana-data


# 2. Fix Permissions for Node-RED (UID 1000)
echo "Setting folder permissions for Node-RED..."
sudo chown -R 1000:1000 ./node-red-data
# Ensure logs directory is writable by the container
sudo chmod -R 777 ./monitor/logs

# 3. Create Systemd Service File
echo "Generating systemd service..."
WORKING_DIR=$(pwd)
SERVICE_FILE="/etc/systemd/system/jetson-demo.service"

sudo bash -c "cat <<EOT > $SERVICE_FILE
[Unit]
Description=Jetson Orin Nano Demo Stack
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$WORKING_DIR
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
StandardOutput=journal

[Install]
WantedBy=multi-user.target
EOT"

sudo systemctl daemon-reload
echo "Service created at $SERVICE_FILE"

# 4. Build and Launch
echo " Building and launching Docker containers..."
docker compose up -d --build

# 5. Wait for InfluxDB to settle before creating the DB, without it the setup crashes
echo "Waiting for InfluxDB to initialize..."
sleep 15
docker exec -it jetson-db influx -execute "CREATE DATABASE jetson_stats"

echo "------------------------------------------------"
echo "SETUP COMPLETE!"
echo "Node-RED: http://$(hostname -I | awk '{print $1}'):1880"
echo "Grafana:  http://$(hostname -I | awk '{print $1}'):3000"
echo "MQTT:     $(hostname -I | awk '{print $1}'):1883"
echo "------------------------------------------------"
echo "To enable auto-start on boot, run:"
echo "sudo systemctl enable jetson-demo.service"