# Use Ubuntu 18.04 as the base image
FROM ubuntu:18.04  

# Set environment variable to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive  

# Set the working directory inside the container
WORKDIR /app  

# Update package lists and install required dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    wget \
    python3 \
    python3-dev \
    python3-pip \
    python3-lxml \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*  

# Install Python dependencies
COPY requirements.txt .  
RUN pip3 install --no-cache-dir -r requirements.txt  

# Copy all bot files to the container
COPY . /app  

# Run the Diary Bot when the container starts
CMD ["python3", "diary.py"]
