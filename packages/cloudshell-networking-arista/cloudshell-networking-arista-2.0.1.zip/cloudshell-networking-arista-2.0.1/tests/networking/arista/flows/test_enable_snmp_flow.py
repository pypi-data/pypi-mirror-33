from unittest import TestCase

from cloudshell.snmp.snmp_parameters import SNMPV2WriteParameters, SNMPV2ReadParameters,\
    SNMPV3Parameters
from mock import MagicMock, create_autospec

from cloudshell.networking.arista.cli.arista_cli_handler import AristaCliHandler
from cloudshell.networking.arista.flows.arista_enable_snmp_flow import AristaEnableSnmpFlow


class TestAristaEnableSNMPFlow(TestCase):
    IP = "localhost"
    SNMP_WRITE_COMMUNITY = "private"
    SNMP_READ_COMMUNITY = "public"
    SNMP_USER = "admin"
    SNMP_PASSWORD = "P@ssw0rD"
    SNMP_PRIVATE_KEY = "PrivKey"

    def setUp(self):
        cli = create_autospec(AristaCliHandler)
        cli_service = MagicMock()
        logger = MagicMock()
        self.session = MagicMock()

        cli.get_cli_service.return_value = cli_service
        cli_service.__enter__.return_value = self.session
        self.session.enter_mode.return_value = self.session
        self.session.__enter__.return_value = self.session

        self.enable_flow = AristaEnableSnmpFlow(cli, logger)

    def test_enable_snmp_read_v2(self):
        self.session.send_command.side_effect = [
            'disabled',
            'enabling community',
            'Community name: {}'.format(self.SNMP_READ_COMMUNITY),
        ]

        snmp_v2_read_parameters = SNMPV2ReadParameters(
            self.IP, self.SNMP_READ_COMMUNITY)

        self.enable_flow.execute_flow(snmp_v2_read_parameters)
        self.assertEqual(self.session.send_command.call_count, 3)

    def test_enable_snmp_write_v2(self):
        self.session.send_command.side_effect = [
            'disabled',
            'enabling community',
            'Community name: {}'.format(self.SNMP_WRITE_COMMUNITY),
        ]

        snmp_v2_write_parameters = SNMPV2WriteParameters(
            self.IP, self.SNMP_WRITE_COMMUNITY)

        self.enable_flow.execute_flow(snmp_v2_write_parameters)
        self.assertEqual(self.session.send_command.call_count, 3)

    def test_enable_snmp_v3(self):
        snmp_v3_parameters = SNMPV3Parameters(
            self.IP, self.SNMP_USER, self.SNMP_PASSWORD, self.SNMP_PRIVATE_KEY)

        self.assertRaises(Exception, self.enable_flow.execute_flow, snmp_v3_parameters)
        self.session.send_command.assert_not_called()

    def test_empty_snmp_community(self):
        snmp_parameters = MagicMock()
        snmp_parameters.snmp_community = None

        self.assertRaises(Exception, self.enable_flow.execute_flow, snmp_parameters)

    def test_already_enabled_snmp(self):
        self.session.send_command.side_effect = [
            'Community name: {}'.format(self.SNMP_READ_COMMUNITY),
            'Community name: {}'.format(self.SNMP_READ_COMMUNITY),
        ]

        snmp_v2_read_parameters = SNMPV2ReadParameters(
            self.IP, self.SNMP_READ_COMMUNITY)

        self.enable_flow.execute_flow(snmp_v2_read_parameters)
        self.assertEqual(self.session.send_command.call_count, 2)

    def test_not_enabled_snmp_community(self):
        self.session.send_command.side_effect = [
            'disabled',
            'does not enabling community',
            'disabled',
        ]

        snmp_v2_read_parameters = SNMPV2ReadParameters(
            self.IP, self.SNMP_READ_COMMUNITY)

        self.assertRaises(
            Exception, self.enable_flow.execute_flow, snmp_v2_read_parameters)
        self.assertEqual(self.session.send_command.call_count, 3)
