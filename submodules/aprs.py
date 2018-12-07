import logging
import time
from functools import partial

import serial

from core import config
from . import command_ingest
from . import eps
from .command_ingest import command
from core.threadhandler import ThreadHandler

# Placeholder values for `telemetry.py`
total_received_ph = 100
success_checksum_ph = 60
fail_checksum_ph = 40
sent_messages_ph = 50

# Initialize global variables
logger = logging.getLogger("APRS")
send_buffer = []
last_telem_time = time.time()
last_message_time = time.time()

bperiod = 60
ser = None  # Initialize serial


@command("aprs_echo", str)
def enqueue(msg: str) -> None:
    """
    Put a packet in the APRS queue.  The APRS queue exists
    only to make sure that we don't send and receive at the
    same time.
    :param msg: Message to send into the APRS queue.
    """
    global send_buffer
    msg = msg + "\r\n"
    send_buffer += [msg]


def send_loop():
    """
    Send all messages in the APRS queue.
    """
    global send_buffer
    while True:
        while len(send_buffer) > 0:  # While there are still messages left in the queue
            # Wait until `message_spacing` seconds after the last received message
            while time.time() - last_message_time < config['aprs']['message_spacing']:
                time.sleep(1)

            ser.write(send_buffer[0].encode("utf-8"))  # Send the message

            send_buffer = send_buffer[1:]  # Remove message from queue
            time.sleep(1)

        time.sleep(1)


def telemetry_watchdog():
    """
    Watches for "hardware beacon" sent out by APRS. Ensures that the radio is still alive.
    """
    while True:
        time.sleep(config['aprs']['telem_timeout'])
        if time.time() - last_telem_time > config['aprs']['telem_timeout']:
            logger.error("APRS IS DEAD - RESTART APRS")
            eps.pin_off('aprs')
            time.sleep(3)
            eps.pin_on('aprs')
            time.sleep(3)
        else:
            logger.debug("Watchdog pass APRS")


def listen():
    """
    Read messages from serial. If a command is received, send it to `command_ingest`
    """
    global last_message_time, last_telem_time
    while True:
        line = ser.readline()  # Read in a full message from serial

        # Update last message time
        last_message_time = time.time()
        if line[0:2] == 'T#':  # Telemetry Packet: APRS special case
            last_telem_time = time.time()
            logger.debug('APRS Telemetry heartbeat received')
            continue  # Don't parse telemetry packets

        # Dispatch command
        parsed = parse_aprs_packet(line)
        command_ingest.dispatch(parsed)


def parse_aprs_packet(packet: str) -> str:
    """
    Given a raw radio packet, strip the APRS junk off of it and make it into pure data.
    :param packet: Input data packet to process.
    :return: The pure data with all APRS wrappers removed.
    """
    raw_packet = str(packet)
    logger.debug("From APRS: " + raw_packet)
    header_index = raw_packet.find(':')
    if header_index == -1:
        logger.error("Incomplete APRS header!")
        return ""  # TODO: make sure this is what we want to do.
    header = raw_packet[:header_index]
    logger.debug("header: " + header)
    data = raw_packet[header_index + 1:]

    if len(data) == 0:
        logger.warning("Empty packet body!")
        # return ""

    logger.debug("Body: " + data)
    return data
    # command_ingest.dispatch(data)


def on_startup():
    global ser

    # Opens the serial port for all methods to use with 19200 baud
    ser = serial.Serial(config['aprs']['serial_port'], 19200)

    # Create all the background threads
    t1 = ThreadHandler(target=partial(listen), name="aprs-listen", parent_logger=logger)
    t2 = ThreadHandler(target=partial(send_loop), name="aprs-send_loop", parent_logger=logger)
    t3 = ThreadHandler(target=partial(telemetry_watchdog), name="aprs-telemetry_watchdog", parent_logger=logger)

    # Start the background threads
    t1.start()
    t2.start()
    t3.start()

    # Turn the power on.  TODO: Power check before turn-on.
    eps.pin_on('aprs')


# TODO: Update these methods. Currently only holds placeholder methods.
def enter_normal_mode():
    global bperiod
    bperiod = 60


def enter_low_power_mode():
    global bperiod
    bperiod = 120


def enter_emergency_mode():
    pass
