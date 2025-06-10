# MCO Protocol Hackathon - Docker Container with Real MCP Server
FROM node:18-slim

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create Python symlink
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install MCO Protocol globally
RUN npm install -g @paradiselabs/mco-protocol

# Set up working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt ./
RUN pip3 install --break-system-packages -r requirements.txt

# Copy application files
COPY . .

# Create workflow directory and copy MCO files
RUN mkdir -p /app/workflow
COPY workflow/ /app/workflow/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MCO_CONFIG_DIR=/app/workflow

# Expose Gradio port
EXPOSE 7860

# Start the application
CMD ["python", "app.py"]