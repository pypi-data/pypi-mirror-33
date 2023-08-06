from cloudshell.networking.arista.flows.arista_disable_snmp_flow import AristaDisableSnmpFlow
from cloudshell.networking.arista.flows.arista_enable_snmp_flow import AristaEnableSnmpFlow
from cloudshell.devices.snmp_handler import SnmpHandler


class AristaSnmpHandler(SnmpHandler):
    def __init__(self, resource_config, logger, api, cli_handler):
        super(AristaSnmpHandler, self).__init__(resource_config, logger, api)
        self.cli_handler = cli_handler

    def _create_enable_flow(self):
        return AristaEnableSnmpFlow(self.cli_handler, self._logger)

    def _create_disable_flow(self):
        return AristaDisableSnmpFlow(self.cli_handler, self._logger)
