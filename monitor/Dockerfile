FROM python:3.10-slim
RUN pip install --no-cache-dir jetson-stats paho-mqtt
WORKDIR /app
COPY health_monitor.py .
CMD ["python", "-u", "health_monitor.py"]