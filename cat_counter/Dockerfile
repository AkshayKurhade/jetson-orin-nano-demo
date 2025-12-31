FROM python:3.10-slim

# Install modern system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight client SDKs
RUN pip install --no-cache-dir \
    inference-sdk \
    opencv-python-headless \
    paho-mqtt

WORKDIR /app
COPY cat_counter.py .

CMD ["python", "cat_counter.py"]