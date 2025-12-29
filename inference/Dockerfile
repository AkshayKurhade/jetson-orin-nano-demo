# Use the core NVIDIA L4T base for JetPack 6.x
FROM nvcr.io/nvidia/l4t-base:r36.2.0

# Set non-interactive for apt
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install Python and GStreamer 'Good' plugins (contains v4l2src)
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-opencv \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-base \
    libgstreamer1.0-0 \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Use the system's hardware-optimized OpenCV (don't pip install it)
RUN pip3 install --no-cache-dir paho-mqtt

COPY inference_server.py .

# 3. Clear GStreamer cache to fix "file too short" errors
RUN rm -rf ~/.cache/gstreamer-1.0

CMD ["python3", "inference_server.py"]