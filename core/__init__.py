import importlib
import logging
import os
import time
import yaml

from enum import Enum
from functools import partial
from threading import Timer

from core.threadhandler import ThreadHandler

from submodules.antenna_deploy import AntennaDeployer


class Mode(Enum):
    NORMAL = 0
    LOW_POWER = 1
    EMERGENCY = 2


class Power(Enum):
    STARTUP = 8.2
    NORMAL = 7.6
    EMERGENCY = 0


class Core:

    def __init__(self):
        if os.path.exists('config/config_custom.yml'):
            with open('config/config_custom.yml') as f:
                self.config = yaml.load(f)
        else:
            with open('config/config_default.yml') as f:
                self.config = yaml.load(f)

        self.logger = logging.getLogger("core")
        self.state = Mode.LOW_POWER

        while True:
            time.sleep(1)

    def get_config(self):
        """Returns the configuration data from config_*.yml as a list"""
        return self.config

    def get_state(self):
        return self.state

    def enter_normal_mode(self, reason: str = '') -> None:
        """
        Enter normal power mode.
        :param reason: Reason for entering normal mode.
        """
        self.logger.warning(
            f"Entering normal mode{'  Reason: ' if reason else ''}{reason}")
        self.state = Mode.NORMAL

    def enter_low_power_mode(self, reason: str = '') -> None:
        """
        Enter low power mode.
        :param reason: Reason for entering low power mode.
        """
        self.logger.warning(
            f"Entering low_power mode{'  Reason: ' if reason else ''}{reason}")
        self.state = Mode.LOW_POWER

    def enter_emergency_mode(self, reason: str = '') -> None:
        """
        Enter emergency power mode.
        :param reason: Reason for entering emergency power mode.
        """
        self.logger.warning(
            f"Entering emergency mode{'  Reason: ' if reason else ''}{reason}")
        self.state = Mode.EMERGENCY

    def power_watchdog(self):
        while True:
            if eps.get_battery_bus_volts() >= Power.NORMAL.value and state != Mode.NORMAL:
                self.enter_normal_mode(
                    f'Battery level at sufficient state: {eps.get_battery_bus_volts()}')
            elif eps.get_battery_bus_volts() < Power.NORMAL.value and state != Mode.LOW_POWER:
                self.enter_low_power_mode(
                    f'Battery level at critical state: {eps.get_battery_bus_volts()}')


def start():
    # Monitor Power Level
    power_monitoring_thread = ThreadHandler(target=partial(power_watchdog),
                                            name="monitoring_power", parent_logger=logger)
    power_monitoring_thread.start()

    while True:
        time.sleep(1)
