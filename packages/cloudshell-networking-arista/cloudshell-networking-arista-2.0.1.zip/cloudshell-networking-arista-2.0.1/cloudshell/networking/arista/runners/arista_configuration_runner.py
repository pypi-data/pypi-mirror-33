from cloudshell.devices.runners.configuration_runner import ConfigurationRunner

from cloudshell.networking.arista.flows.arista_restore_flow import AristaRestoreFlow
from cloudshell.networking.arista.flows.arista_save_flow import AristaSaveFlow


class AristaConfigurationRunner(ConfigurationRunner):
    @property
    def restore_flow(self):
        return AristaRestoreFlow(self.cli_handler, self._logger)

    @property
    def save_flow(self):
        return AristaSaveFlow(self.cli_handler, self._logger)

    @property
    def file_system(self):
        return "flash:"
