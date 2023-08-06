from unittest import TestCase

from cloudshell.cli.cli_service import CliService
from mock import MagicMock, create_autospec

from cloudshell.networking.arista.command_actions.enable_disable_snmp_actions \
    import EnableDisableSnmpActions


def return_cmd(cmd, **kwargs):
    return cmd


class TestAristaSystemActions(TestCase):
    def set_up(self, response):
        cli_service = create_autospec(CliService)
        if callable(response):
            cli_service.send_command = response
        else:
            cli_service.send_command.return_value = response
        return EnableDisableSnmpActions(cli_service=cli_service,
                                        logger=MagicMock())

    def test_get_current_snmp_communities(self):
        # Setup
        expected_result = "snmp-server community public ro"
        enable_disable_actions = self.set_up(expected_result)

        # Assert
        self.assertTrue(
            enable_disable_actions.is_configured(snmp_community='public'))

    def test_get_current_enable_snmp_read_only(self):
        # Setup
        community = "public"
        expected_result = "snmp-server community public ro"
        enable_disable_actions = self.set_up(return_cmd)

        # Act
        result = enable_disable_actions.enable_snmp(community)

        # Assert
        self.assertTrue(result)
        self.assertEqual(result, expected_result)

    def test_get_current_disable_snmp(self):
        # Setup
        community = "public"
        expected_result = "no snmp-server community public"
        enable_disable_actions = self.set_up(return_cmd)

        # Act
        result = enable_disable_actions.disable_snmp(community)

        # Assert
        self.assertTrue(result)
        self.assertEqual(result, expected_result)
