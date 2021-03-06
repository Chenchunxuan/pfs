from time import time as sys_time
from os import path

from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry, StateField


class AntennaDeployReadTask:

    def __init__(self, state_field_registry: StateFieldRegistry):
        self.state_field_registry: StateFieldRegistry = state_field_registry

    def execute(self):
        """
        Checks if antenna has been deployed
        :return: (None)
        """
        self.state_field_registry.update(StateField.ANTENNA_DEPLOYED, path.exists("/root/antenna_deployed"))
