#!/bin/bash

# Setup script for real smart meter connection
# This script will:
# 1. Generate certificates and keys
# 2. Create .env file with proper configuration
# 3. Display the LFDI for Xcel registration

set -e

echo "=== Xcel Itron2MQTT Real Meter Setup ==="
echo

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: Please run this script from the xcel_itron2mqtt directory"
    exit 1
fi

# Step 1: Generate certificates and keys
echo "Step 1: Generating certificates and keys..."
if [ -f "scripts/generate_keys.sh" ]; then
    chmod +x scripts/generate_keys.sh
    ./scripts/generate_keys.sh
else
    echo "Error: generate_keys.sh script not found"
    exit 1
fi

# Step 2: Get the LFDI
echo
echo "Step 2: Getting LFDI for Xcel registration..."
LFDI=$(./scripts/generate_keys.sh -p | grep -E '^[A-F0-9]{40}$')
echo "Your LFDI is: $LFDI"
echo "Please register this LFDI with Xcel Energy "
echo

# Step 3: Create .env file
echo "Step 3: Creating .env file..."
if [ -f ".env" ]; then
    echo "Warning: .env file already exists. Creating backup..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Create .env file from template
cp env.template .env

echo
echo "Step 4: Configuration Instructions"
echo "=================================="
echo "1. Your LFDI is: $LFDI"
echo "   - Register this with Xcel Energy"
echo "   - Wait for approval (may take 24-48 hours)"
echo
echo "2. Once approved, update your .env file with:"
echo "   - METER_IP: Your smart meter's IP address"
echo "   - METER_PORT: Usually 8081 (default)"
echo "   - CERT_PATH: /opt/xcel_itron2mqtt/certs/.cert.pem (for Docker)"
echo "   - KEY_PATH: /opt/xcel_itron2mqtt/certs/.key.pem (for Docker)"
echo
echo "3. To run with real meter:"
echo "   docker-compose --profile real_meter up -d"
echo
echo "4. To run with simulated meter (current setup):"
echo "   docker-compose up -d"
echo
echo "Setup complete! Your certificates are in the certs/ directory."
echo "Remember to keep your certificates secure and never commit them to version control." 