# Dockerized Meter Simulator

This project has been dockerized to run in two modes:
- **SIMULATION MODE**: Connects to an external meter simulator
- **REAL METER MODE**: Connects to actual smart meters

The container publishes data to your existing MQTT infrastructure.

## Quick Start

### 1. Setup Environment Variables

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` with your specific values, especially for real meter mode.

### 2. Running the Application

#### Simulation Mode

To run in simulation mode (connects to external simulator):

```bash
# Start meter simulator in simulation mode
docker-compose --profile simulation up -d

# View logs
docker-compose logs -f meter_simulator
```

#### Real Meter Mode

To run in real meter mode (connects to actual smart meters):

```bash
# Make sure you have certificates in realMeter/certs/
# and METER_IP is set in your .env file

# Start meter simulator in real meter mode
docker-compose --profile real_meter up -d

# View logs
docker-compose logs -f meter_real
```

### 3. Integration with Your Infrastructure

This container is designed to work with your existing infrastructure:

- **MQTT**: Connects to your existing Mosquitto container (`mqtt:1883`)
- **Data Flow**: Publishes to topic `xcel_itron5/sFDI/Power_Demand/state`
- **Your Telegraf**: Will pick up the data and forward to InfluxDB
- **Your Grafana**: Can visualize the data from InfluxDB

## Environment Variables

### Required for Real Meter Mode:
- `METER_IP`: IP address of your smart meter
- `METER_PORT`: Port of your smart meter (default: 443)

### MQTT Configuration:
- `MQTT_SERVER`: MQTT broker hostname (default: mqtt - your existing container)
- `MQTT_PORT`: MQTT broker port (default: 1883)
- `MQTT_METER_TOPIC_PREFIX`: MQTT topic prefix (default: xcel_itron_5)

## Certificate Setup for Real Meter Mode

For real meter mode, you need to place your certificates in `realMeter/certs/`:

```bash
realMeter/certs/
├── .cert.pem    # Your certificate file
└── .key.pem     # Your private key file
```

## Troubleshooting

### Check Container Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs meter_simulator
docker-compose logs meter_real
```

### Restart Services
```bash
# Restart specific service
docker-compose restart meter_simulator

# Restart all services
docker-compose restart
```

### Clean Up
```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v
```

## Development

### Building the Image
```bash
docker-compose build meter_simulator
```

### Running with Custom Parameters
```bash
# Run with specific meter reading ID
docker-compose run --rm meter_simulator 2
```

## Data Flow

1. **Meter Simulator** → Reads data from simulator/real meter
2. **Meter Simulator** → Publishes to MQTT topic `xcel_itron5/sFDI/Power_Demand/state`
3. **Your Telegraf** → Subscribes to MQTT topics and forwards to InfluxDB
4. **Your Grafana** → Queries InfluxDB for visualization

## Network Configuration

The container expects to connect to your existing MQTT broker at `mqtt:1883`. Make sure:

1. Your MQTT container is named `mqtt` or update the `MQTT_SERVER` environment variable
2. Both containers are on the same Docker network
3. The MQTT broker allows connections from this container 