# MQTT Adapter for JT/T 808 Protocol

This adapter transforms JT/T 808 protocol messages from GPS tracking devices into MQTT messages.

## Files

- `mqtt_client.py`: MQTT client that handles connection and publishing to the broker
- `protocol_adapter.py`: JT/T 808 protocol parser and TCP server that accepts device connections
- `__init__.py`: Package exports

## Usage

See the main `MQTT_ADAPTER_GUIDE.md` file for detailed instructions on how to use the adapter.

## Key Features

- Automatic protocol parsing and message validation
- Conversion of binary JT/T 808 messages to JSON
- Support for device registration, authentication, and location reporting
- Pet-specific extensions for activity, health, and temperature data
