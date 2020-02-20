from MainControlLoop.lib.StateFieldRegistry import StateFieldRegistry
from MainControlLoop.lib.drivers.APRS import APRS

from MainControlLoop.tasks.APRS.read_task import APRSReadTask


class APRSReadTest:
    def test_read(self):
        """
        Test APRS read task
        :return: None
        """
        aprs = APRS()
        aprs.functional()
        state_field_registry = StateFieldRegistry()
        aprs_read_task = APRSReadTask(aprs, state_field_registry)
        message = ""
        while message != "-1":
            if input("Send something now. Send or type '-1' (no quotes) to stop. Press enter to continue") == "-1":
                return
            aprs_read_task.execute()
            if state_field_registry.critical_failure():
                print("Critical failure received in SFR")
                print(state_field_registry.registry)
                print(state_field_registry.hardware_faults)
            else:
                print("Received", aprs_read_task.last_message)
                message = aprs_read_task.last_message
