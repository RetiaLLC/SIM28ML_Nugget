## By Skickar 2024
## Parses NMEA messages from a SIM28ML GPS Module
## Also displays them on the screen of USB Nugget

import board
import busio
import time
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_displayio_sh1106 import SH1106

# Initialize I2C and display
displayio.release_displays()
i2c = busio.I2C(scl=board.SCL, sda=board.SDA)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
WIDTH = 130
HEIGHT = 64
display = SH1106(display_bus, width=WIDTH, height=HEIGHT)

# Initialize UART communication
uart = busio.UART(board.IO8, board.IO6, baudrate=9600)

def read_line(uart):
    line = bytearray()
    while True:
        char = uart.read(1)
        if char:
            line += char
            if char == b'\n':
                break
    return bytes(line)

# GPS parsing functions
def parse_gpgga(sentence):
    fields = sentence.split(',')
    time_utc = fields[1]
    latitude = fields[2]
    longitude = fields[4]
    fix_status = fields[6]
    num_satellites = fields[7]
    # Add more detailed parsing as needed
    return f"Time: {time_utc}, Latitude: {latitude}, Longitude: {longitude}, Satellites: {num_satellites}"

def parse_gpgsv(sentence):
    fields = sentence.split(',')
    total_messages = fields[1]
    message_number = fields[2]
    satellites_in_view = fields[3]
    satellites_info = ''
    for i in range(4, len(fields)-3, 4):
        satellite_id = fields[i]
        elevation = fields[i+1]
        azimuth = fields[i+2]
        snr = fields[i+3]
        satellites_info += f"Satellite ID: {satellite_id}, Elevation: {elevation}, Azimuth: {azimuth}, SNR: {snr}; "
    return f"Satellites in View: {satellites_in_view}, Details: [{satellites_info}]"


def parse_gpgsa(sentence):
    fields = sentence.split(',')
    mode = fields[1]
    fix_type = fields[2]
    satellites = [field for field in fields[3:15] if field != '']
    pdop = fields[15]
    hdop = fields[16]
    vdop = fields[17].split('*')[0]  # Remove checksum part if present
    return f"Mode: {mode}, Fix Type: {fix_type}, Satellites: {satellites}, PDOP: {pdop}, HDOP: {hdop}, VDOP: {vdop}"


def parse_gprmc(sentence):
    fields = sentence.split(',')
    time_utc = fields[1]
    status = fields[2]
    latitude = fields[3]
    longitude = fields[5]
    speed_over_ground = fields[7]
    course_over_ground = fields[8]
    return f"Time: {time_utc}, Status: {status}, Latitude: {latitude}, Longitude: {longitude}, Speed: {speed_over_ground}, Course: {course_over_ground}"

def parse_gpGLL(sentence):
    fields = sentence.split(',')
    latitude = fields[1]
    latitude_dir = fields[2]
    longitude = fields[3]
    longitude_dir = fields[4]
    time_utc = fields[5]
    status = fields[6]  # A=Active, V=Void (inactive)
    return f"Latitude: {latitude} {latitude_dir}, Longitude: {longitude} {longitude_dir}, Time: {time_utc}, Status: {status}"


def parse_gpvtg(sentence):
    fields = sentence.split(',')
    course_over_ground = fields[1]
    speed_over_ground_knots = fields[5]
    speed_over_ground_kmh = fields[7]
    return f"Course: {course_over_ground}, Speed: {speed_over_ground_knots} Knots, {speed_over_ground_kmh} Km/h"

def parse_gps_data(data):
    try:
        sentence = data.decode('utf-8').strip()
        if sentence.startswith('$GPGGA'):
            return parse_gpgga(sentence)
        elif sentence.startswith('$GPRMC'):
            return parse_gprmc(sentence)
        elif sentence.startswith('$GPVTG'):
            return parse_gpvtg(sentence)
        elif sentence.startswith('$GPGSV'):
            return parse_gpgsv(sentence)
        elif sentence.startswith('$GPGSA'):
            return parse_gpgsa(sentence)
        elif sentence.startswith('$GPGLL'):
            return parse_gpGLL(sentence)
        # Add elif blocks for other sentence types as needed
        else:
            pass #return 'Unsupported sentence type'
    except Exception as e:
        return f"Error decoding data: {e}"

# Main loop to read and display GPS data
while True:
    data = read_line(uart)
    if data:
        gps_info = parse_gps_data(data)
        print(gps_info)

    time.sleep(1)
