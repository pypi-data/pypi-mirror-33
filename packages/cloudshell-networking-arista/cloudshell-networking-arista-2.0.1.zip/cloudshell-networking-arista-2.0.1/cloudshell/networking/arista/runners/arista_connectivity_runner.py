from cloudshell.devices.runners.connectivity_runner import ConnectivityRunner

from cloudshell.networking.arista.flows.arista_add_vlan_flow import AristaAddVlanFlow
from cloudshell.networking.arista.flows.arista_remove_vlan_flow import AristaRemoveVlanFlow


class AristaConnectivityRunner(ConnectivityRunner):
    @property
    def add_vlan_flow(self):
        return AristaAddVlanFlow(self.cli_handler, self._logger)

    @property
    def remove_vlan_flow(self):
        return AristaRemoveVlanFlow(self.cli_handler, self._logger)
