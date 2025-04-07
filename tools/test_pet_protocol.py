#!/usr/bin/env python3
"""
Test script for pet-specific JT808 protocol extensions

This script simulates a pet tracking device sending JT808 protocol messages with
pet-specific additional data fields.
"""

import os
import sys
import time
import socket
import struct
import binascii
import logging
import argparse
import random
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pet_protocol_tester')

# Constants
DEFAULT_SERVER_HOST = '127.0.0.1'
DEFAULT_SERVER_PORT = 8080
DEFAULT_DEVICE_ID = '123456'  # "Phone number" in JT808 protocol
DEFAULT_IMEI = '123456789012345'

def encode_jt808_message(msg_id, phone_number, body, seq_num=None):
    """
    Encode a JT808 protocol message

    Args:
        msg_id: Message ID (e.g., 0x0200 for location report)
        phone_number: Device identifier (max 6 bytes)
        body: Message body as bytes
        seq_num: Message sequence number (generated if None)

    Returns:
        Bytes object containing the encoded JT808 message
    """
    # Format phone number consistently
    if isinstance(phone_number, str):
        phone_bytes = phone_number.encode('ascii')
        # Ensure it's exactly 6 bytes (right-padded with zeros)
        if len(phone_bytes) < 6:
            phone_bytes = phone_bytes.ljust(6, b'\x00')
        elif len(phone_bytes) > 6:
            phone_bytes = phone_bytes[:6]
    else:
        phone_bytes = phone_number

    # Generate sequence number if not provided
    if seq_num is None:
        seq_num = random.randint(1, 65535)

    # Prepare header
    msg_attributes = len(body) & 0x1FFF  # Lower 13 bits for body length
    header = struct.pack('>HH6sH', msg_id, msg_attributes, phone_bytes, seq_num)

    # Calculate checksum (XOR of all bytes in header and body)
    checksum = 0
    for b in header + body:
        checksum ^= b

    # Assemble message with start/end markers
    message = bytearray([0x7e])  # Start marker
    message.extend(header)
    message.extend(body)
    message.append(checksum)
    message.append(0x7e)  # End marker

    # Apply escape rules: 0x7e -> 0x7d, 0x02 and 0x7d -> 0x7d, 0x01
    escaped_message = bytearray([0x7e])  # Keep start marker
    for b in message[1:-1]:  # Process everything except start/end markers
        if b == 0x7e:
            escaped_message.extend([0x7d, 0x02])
        elif b == 0x7d:
            escaped_message.extend([0x7d, 0x01])
        else:
            escaped_message.append(b)
    escaped_message.append(0x7e)  # Keep end marker

    return bytes(escaped_message)

def datetime_to_bcd(dt=None):
    """
    Convert datetime to BCD format used in JT808

    Args:
        dt: Datetime object to convert (uses current time if None)

    Returns:
        Bytes containing BCD-encoded time (YYMMDDhhmmss)
    """
    if dt is None:
        dt = datetime.now()

    # Format as string then convert to BCD
    time_str = dt.strftime('%y%m%d%H%M%S')
    bcd = bytes.fromhex(time_str)
    return bcd

def generate_location_message(phone_number, seq_num=None, include_pet_data=True):
    """
    Generate a location report message (0x0200) with pet-specific fields

    Args:
        phone_number: Device identifier
        seq_num: Message sequence number
        include_pet_data: Whether to include pet-specific additional data

    Returns:
        Encoded JT808 message
    """
    # Basic parameters - using random values for testing
    latitude = random.uniform(35.0, 42.0) * 1000000  # Convert to JT808 format (integer)
    longitude = random.uniform(-125.0, -115.0) * 1000000
    altitude = random.randint(0, 100)  # Meters
    speed = random.randint(0, 200)  # 0.1 km/h units
    direction = random.randint(0, 359)  # Degrees
    alarm = 0  # No alarms
    status = 2  # Bit 1 set (GPS valid)

    # Prepare location body with basic fields
    # Format: Alarm (4 bytes) + Status (4 bytes) + Latitude (4 bytes) + Longitude (4 bytes) + 
    # Altitude (2 bytes) + Speed (2 bytes) + Direction (2 bytes) + Time (6 bytes BCD)
    location_body = struct.pack(
        '>IIiiHHH6s',
        alarm, status, 
        int(latitude), int(longitude),
        altitude, speed, direction,
        datetime_to_bcd()
    )

    # Add pet-specific additional data fields if requested
    if include_pet_data:
        # Add battery level (0x30) - 1 byte value
        battery_level = random.randint(50, 100)
        location_body += bytes([0x30, 1, battery_level])

        # Add activity level (0x31) - 1 byte value
        activity_level = random.randint(0, 100)
        location_body += bytes([0x31, 1, activity_level])

        # Add health status flags (0x32) - 2 bytes
        # Bits indicating different health conditions
        health_flags = 0  # All healthy
        if random.random() < 0.1:  # 10% chance of warning
            health_flags |= 1  # Temperature warning
        if activity_level < 20 and random.random() < 0.5:
            health_flags |= 2  # Inactivity warning
        location_body += bytes([0x32, 2]) + struct.pack('>H', health_flags)

        # Add temperature data (0x33) - 2 bytes, signed
        # Temperature in 0.1°C units
        temperature = random.uniform(36.5, 39.5) * 10  # Normal dog temperature
        location_body += bytes([0x33, 2]) + struct.pack('>h', int(temperature))

    # Encode the full message
    return encode_jt808_message(0x0200, phone_number, location_body, seq_num)

def decode_response(data):
    """
    Decode a JT808 protocol response from the server

    Args:
        data: Raw bytes from server

    Returns:
        Dictionary with decoded response data or None on error
    """
    try:
        if not data:
            logger.warning("No data received")
            return None

        # For debugging
        hex_data = binascii.hexlify(data).decode('ascii')
        logger.debug(f"Received: {hex_data}")

        if data[0] != 0x7e:
            logger.warning("Missing start marker in response")
            return None

        if data[-1] != 0x7e:
            logger.warning("Missing end marker in response")
            return None

        # Remove escape sequences (reverse the 0x7d 0x01, 0x7d 0x02 escapes)
        unescaped_data = bytearray()
        i = 1  # Skip start marker
        while i < len(data) - 1:  # Skip end marker
            if data[i] == 0x7d:
                if i + 1 < len(data) - 1:
                    if data[i + 1] == 0x02:
                        unescaped_data.append(0x7e)
                        i += 2
                        continue
                    elif data[i + 1] == 0x01:
                        unescaped_data.append(0x7d)
                        i += 2
                        continue
                unescaped_data.append(data[i])
                i += 1
            else:
                unescaped_data.append(data[i])
                i += 1

        # Verify minimum length after unescaping
        if len(unescaped_data) < 12:  # Minimum size for header + checksum
            logger.warning(f"Message too short after unescaping: {len(unescaped_data)} bytes")
            return None

        # Extract header fields
        try:
            header_format = '>HH6sH'
            header_size = struct.calcsize(header_format)
            
            if len(unescaped_data) < header_size + 1:  # +1 for checksum
                logger.warning(f"Message too short for header: {len(unescaped_data)} bytes")
                return None
                
            header_data = struct.unpack(header_format, unescaped_data[:header_size])
            
            msg_id = header_data[0]
            msg_attributes = header_data[1]
            phone_number = header_data[2].decode('ascii', errors='ignore').strip('\x00')
            serial_number = header_data[3]
            
            # For general response (0x8001), decode body
            body = unescaped_data[header_size:-1]  # Exclude checksum
            body_dict = {}
            
            if msg_id == 0x8001:  # General response
                if len(body) >= 5:  # At least 2-byte serial + 2-byte msg_id + 1-byte result
                    resp_serial = struct.unpack('>H', body[0:2])[0]
                    resp_msg_id = struct.unpack('>H', body[2:4])[0]
                    result = body[4]
                    
                    body_dict = {
                        'response_serial_number': resp_serial,
                        'response_msg_id': resp_msg_id,
                        'result': result
                    }
                else:
                    body_dict = {'raw_hex': binascii.hexlify(body).decode('ascii')}
            else:
                body_dict = {'raw_hex': binascii.hexlify(body).decode('ascii')}
            
            return {
                'msg_id': msg_id,
                'msg_id_hex': f"0x{msg_id:04X}",
                'phone_number': phone_number,
                'serial_number': serial_number,
                'body': body_dict
            }
            
        except Exception as e:
            logger.error(f"Error parsing header/body: {e}")
            return {'error': str(e), 'raw_hex': binascii.hexlify(data).decode('ascii')}
            
    except Exception as e:
        logger.error(f"Error decoding response: {e}")
        return {'error': str(e), 'raw_hex': binascii.hexlify(data).decode('ascii') if data else 'No data'}

def run_test(host, port, device_id, test_count=5, delay=2, include_pet_data=True):
    """
    Run a test of pet-specific protocol extensions

    Args:
        host: Server host address
        port: Server port
        device_id: Device identifier
        test_count: Number of messages to send
        delay: Delay between messages in seconds
        include_pet_data: Whether to include pet-specific data fields
    """
    try:
        logger.info(f"Starting pet protocol test")
        logger.info(f"Connecting to {host}:{port}")
        logger.info(f"Device ID: {device_id}")
        logger.info(f"Pet data: {'Enabled' if include_pet_data else 'Disabled'}")
        
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        
        for i in range(test_count):
            # Generate sequence number
            seq_num = i + 1
            
            # Generate and send location message
            message = generate_location_message(device_id, seq_num, include_pet_data)
            logger.info(f"Sending location message {seq_num}/{test_count}")
            
            if not message:
                logger.error("Failed to generate message")
                continue
            
            # Show what we're sending with pet-specific data
            if include_pet_data:
                pet_info = []
                if i % 3 == 0:  # Vary the simulated pet status
                    pet_info.append("Normal temperature and activity")
                elif i % 3 == 1:
                    pet_info.append("Increased activity (exercise)")
                else:
                    pet_info.append("Rest period (lower activity)")
                
                logger.info(f"Pet data included: {', '.join(pet_info)}")
                
            sock.send(message)
            
            # Receive response
            try:
                sock.settimeout(5.0)  # Set timeout for receive
                response_data = sock.recv(1024)
                sock.settimeout(None)  # Reset timeout
                
                if response_data:
                    # Print raw hex for debugging
                    hex_data = binascii.hexlify(response_data).decode('ascii')
                    logger.debug(f"Raw response: {hex_data}")
                    
                    # Try to decode
                    response = decode_response(response_data)
                    if response:
                        if 'msg_id_hex' in response:
                            msg_id_hex = response['msg_id_hex']
                        else:
                            msg_id_hex = f"0x{response.get('msg_id', 0):04X}"
                            
                        body = response.get('body', {})
                        if isinstance(body, dict):
                            result = body.get('result', 'N/A')
                        else:
                            result = 'N/A'
                        logger.info(f"Received response: msg_id={msg_id_hex}, result={result}")
                        
                        # Log detailed response for debugging
                        logger.debug(f"Full response: {response}")
                    else:
                        logger.warning(f"Failed to decode response: {hex_data}")
                else:
                    logger.warning("No response received (empty data)")
            except socket.timeout:
                logger.warning("Socket timeout waiting for response")
            except Exception as e:
                logger.error(f"Error receiving/decoding response: {e}")
                
            # Wait before next message
            if i < test_count - 1:
                time.sleep(delay)
                
        # Close socket
        sock.close()
        logger.info("Test completed successfully")
        
    except ConnectionRefusedError:
        logger.error(f"Connection refused to {host}:{port}. Is the protocol server running?")
    except Exception as e:
        logger.error(f"Error during test: {e}")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='JT808 Pet Protocol Test Tool')
    parser.add_argument('--host', default=DEFAULT_SERVER_HOST,
                        help=f'Server host address (default: {DEFAULT_SERVER_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_SERVER_PORT,
                        help=f'Server port (default: {DEFAULT_SERVER_PORT})')
    parser.add_argument('--device-id', default=DEFAULT_DEVICE_ID,
                        help=f'Device ID (default: {DEFAULT_DEVICE_ID})')
    parser.add_argument('--count', type=int, default=5,
                        help='Number of messages to send (default: 5)')
    parser.add_argument('--delay', type=float, default=2.0,
                        help='Delay between messages in seconds (default: 2.0)')
    parser.add_argument('--no-pet-data', action='store_true',
                        help='Disable pet-specific additional data fields')
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()
    run_test(
        host=args.host,
        port=args.port,
        device_id=args.device_id,
        test_count=args.count,
        delay=args.delay,
        include_pet_data=not args.no_pet_data
    )

def compare_protocols():
    """
    Compare standard JT808 protocol with pet-enhanced version.
    This function generates and prints messages in both formats for comparison.
    """
    device_id = DEFAULT_DEVICE_ID
    seq_num = 1
    
    # Generate standard message
    standard_msg = generate_location_message(device_id, seq_num, include_pet_data=False)
    
    # Generate pet-enhanced message
    pet_msg = generate_location_message(device_id, seq_num, include_pet_data=True)
    
    # Compare sizes
    std_size = len(standard_msg)
    pet_size = len(pet_msg)
    size_diff = pet_size - std_size
    
    print("\n====== PROTOCOL COMPARISON ======")
    print(f"Standard JT808 message size: {std_size} bytes")
    print(f"Pet-enhanced JT808 message size: {pet_size} bytes")
    print(f"Difference: +{size_diff} bytes ({(size_diff/std_size*100):.1f}% larger)")
    
    # Show hexdump comparison (first 64 bytes for common part)
    print("\nStandard JT808 message (first 64 bytes):")
    standard_hex = binascii.hexlify(standard_msg[:64]).decode('ascii')
    formatted_hex = ' '.join(standard_hex[i:i+2] for i in range(0, len(standard_hex), 2))
    print(formatted_hex)
    
    print("\nPet-enhanced JT808 message (first 64 bytes):")
    pet_hex = binascii.hexlify(pet_msg[:64]).decode('ascii')
    formatted_hex = ' '.join(pet_hex[i:i+2] for i in range(0, len(pet_hex), 2))
    print(formatted_hex)
    
    # Show only the additional fields in the pet-enhanced version
    print("\nPet-specific fields only:")
    if pet_size > std_size:
        pet_specific = pet_msg[std_size-2:]  # Account for end marker and checksum
        pet_hex = binascii.hexlify(pet_specific).decode('ascii')
        formatted_hex = ' '.join(pet_hex[i:i+2] for i in range(0, len(pet_hex), 2))
        print(formatted_hex)
        
    print("\nPet-specific field meanings:")
    print("0x30 01 XX = Battery level (percentage)")
    print("0x31 01 XX = Pet activity level (percentage)")
    print("0x32 02 XX XX = Health status flags (2 bytes)")
    print("0x33 02 XX XX = Temperature (Celsius × 10, signed)")

if __name__ == "__main__":
    # Check if we should run the comparison
    if len(sys.argv) > 1 and sys.argv[1] == "--compare":
        compare_protocols()
    else:
        main()