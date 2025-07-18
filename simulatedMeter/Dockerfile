# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies using pipenv
RUN pipenv install --system --deploy

# Copy application files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV METER_MODE=simulation
ENV HOST_IP=localhost
ENV MQTT_SERVER=mqtt
ENV MQTT_PORT=1883
ENV MQTT_METER_TOPIC_PREFIX=xcel_itron_5

# Expose port if needed (for debugging)
EXPOSE 8082

# Set the entrypoint
ENTRYPOINT ["python", "entrypoint.py"] 