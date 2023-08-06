from cloudshell.devices.runners.autoload_runner import AutoloadRunner

from cloudshell.networking.arista.flows.arista_autoload_flow import AristaAutoloadFlow


class AristaAutoloadRunner(AutoloadRunner):
    def __init__(self, logger, resource_config, snmp_handler):
        super(AristaAutoloadRunner, self).__init__(resource_config)
        self._logger = logger
        self.snmp_handler = snmp_handler

    @property
    def autoload_flow(self):
        return AristaAutoloadFlow(self.snmp_handler, self._logger)
