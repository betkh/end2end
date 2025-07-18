# Xcel Smart Meter Monitoring Stack

This repository provides a complete solution for monitoring Xcel Energy smart meters and integrating their data with MQTT, Home Assistant, and Grafana dashboards.

- **realMeter/**: Contains code to connect and interact with real smart meters over the Home Area Network (HAN), enabling secure data collection from approved meters.
- **simulatedMeter/**: Allows exploration of smart meter endpoints using the MeterAgentSimulator and Energy Launchpad, providing simulated data for development and testing.
- **xcel_itron2mqtt/**: An enhanced version of xcel_2iron2mqtt, featuring seamless integration with Grafana via Telegraf and InfluxDB for real-time visualization and historical analysis of energy data.

This stack supports both real and simulated meters, automatic Home Assistant sensor creation via MQTT discovery, and flexible
