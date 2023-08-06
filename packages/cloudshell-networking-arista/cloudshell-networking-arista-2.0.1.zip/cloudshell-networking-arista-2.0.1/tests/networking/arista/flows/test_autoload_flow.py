from unittest import TestCase

from mock import MagicMock, create_autospec, patch

from cloudshell.networking.arista.flows.arista_autoload_flow import AristaAutoloadFlow
from cloudshell.networking.arista.snmp.arista_snmp_handler import AristaSnmpHandler


@patch('cloudshell.networking.arista.flows.arista_autoload_flow.AristaSNMPAutoload')
class TestAristaLoadFirmwareFlow(TestCase):
    def test_execute_flow(self, autoload_mock):
        snmp_handler = create_autospec(AristaSnmpHandler)
        logger = MagicMock()
        autoload_flow = AristaAutoloadFlow(snmp_handler, logger)
        snmp_service = snmp_handler.get_snmp_service.return_value.__enter__.return_value
        supported_os = MagicMock()
        shell_name = MagicMock()
        shell_type = MagicMock()
        resource_name = MagicMock()

        autoload_flow.execute_flow(supported_os, shell_name, shell_type, resource_name)

        autoload_mock.assert_called_once_with(
            snmp_service, shell_name, shell_type, resource_name, logger
        )
        autoload_mock.return_value.discover.assert_called_once_with(supported_os)
