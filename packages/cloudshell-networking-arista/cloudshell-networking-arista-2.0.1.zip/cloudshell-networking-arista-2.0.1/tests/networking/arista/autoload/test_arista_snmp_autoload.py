from unittest import TestCase

from cloudshell.snmp.quali_snmp import QualiSnmp
from mock import MagicMock, create_autospec

from cloudshell.networking.arista.autoload.arista_snmp_autoload import AristaSNMPAutoload


def _get_property(dct):
    def wrapped(*args):
        return dct.get(args)
    return wrapped


class TestAristaSnmpAutoload(TestCase):
    def setUp(self):
        self.supported_os = ['EOS']
        self.snmp_service = create_autospec(QualiSnmp)
        shell_name = 'AristaEosSwitchShell2G'
        shell_type = 'CS_Switch'
        resource_name = MagicMock()
        logger = MagicMock()

        self.autoload = AristaSNMPAutoload(
            self.snmp_service, shell_name, shell_type, resource_name, logger)

    def test_not_supported_os(self):
        self.snmp_service.get_property.side_effect = _get_property({
            ('SNMPv2-MIB', 'sysDescr', '0'): 'Cisco Networks IOS',
        })

        self.assertRaises(Exception, self.autoload.discover, self.supported_os)

    def test_is_valid_device_os(self):
        self.snmp_service.get_property.side_effect = _get_property({
            ('SNMPv2-MIB', 'sysDescr', '0'):
                'Arista Networks EOS version 4.20.1F running on an Arista Networks vEOS',
        })

        self.assertTrue(self.autoload._is_valid_device_os(self.supported_os))

    def test_discover(self):
        properties = {
            ('SNMPv2-MIB', 'sysDescr', '0'):
                'Arista Networks EOS version 4.20.1F running on an Arista Networks vEOS',
            ('SNMPv2-MIB', 'sysContact', '0'): '',
            ('SNMPv2-MIB', 'sysName', '0'): '',
            ('SNMPv2-MIB', 'sysLocation', '0'): '',
            ('SNMPv2-MIB', 'sysObjectID', '0'): 'ARISTA-SMI-MIB::aristaProducts.2759',
        }
        self.snmp_service.get_property.side_effect = properties.get
        # self.snmp_service.get_table.side_effect = _get_table({
        #
        # })

        self.autoload.discover(self.supported_os)
