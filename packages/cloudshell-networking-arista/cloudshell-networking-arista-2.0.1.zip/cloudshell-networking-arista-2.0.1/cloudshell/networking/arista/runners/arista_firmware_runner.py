from cloudshell.devices.runners.firmware_runner import FirmwareRunner

from cloudshell.networking.arista.flows.arista_load_firmware_flow import AristaLoadFirmwareFlow


class AristaFirmwareRunner(FirmwareRunner):
    @property
    def load_firmware_flow(self):
        return AristaLoadFirmwareFlow(self.cli_handler, self._logger)
