from unittest import TestCase

from mock import MagicMock

from cloudshell.networking.arista.flows.arista_disable_snmp_flow import AristaDisableSnmpFlow
from cloudshell.networking.arista.flows.arista_enable_snmp_flow import AristaEnableSnmpFlow
from cloudshell.networking.arista.snmp.arista_snmp_handler import AristaSnmpHandler


class TestAristaSnmpHandler(TestCase):
    def setUp(self):
        self.snmp_handler = AristaSnmpHandler(
            MagicMock(), MagicMock(), MagicMock(), MagicMock())

    def test_get_enable_flow(self):
        self.assertIsInstance(self.snmp_handler._create_enable_flow(),
                              AristaEnableSnmpFlow)

    def test_get_disable_flow(self):
        self.assertIsInstance(self.snmp_handler._create_disable_flow(),
                              AristaDisableSnmpFlow)
