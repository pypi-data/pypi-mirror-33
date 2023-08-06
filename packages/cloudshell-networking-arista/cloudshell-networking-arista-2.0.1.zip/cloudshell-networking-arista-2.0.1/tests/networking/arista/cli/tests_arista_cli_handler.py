from unittest import TestCase

from cloudshell.cli.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from mock import MagicMock, patch

from cloudshell.networking.arista.cli.arista_cli_handler import \
    AristaCliHandler
from cloudshell.networking.arista.cli.arista_command_modes import \
    AristaConfigCommandMode, AristaDefaultCommandMode, AristaEnableCommandMode
from cloudshell.networking.arista.sessions.console_ssh_session \
    import ConsoleSSHSession
from cloudshell.networking.arista.sessions.console_telnet_session \
    import ConsoleTelnetSession


class TestAristaSystemActions(TestCase):
    def setUp(self):
        AristaConfigCommandMode.ENTER_CONFIG_RETRY_TIMEOUT = 0.5

        self.api = MagicMock()
        self.api.DecryptPassword().Value.return_value = "password"

    def get_cli_handler(self, connection_type='SSH'):
        resource_config = MagicMock()
        resource_config.cli_connection_type = connection_type
        return AristaCliHandler(CLI(), resource_config, MagicMock(), self.api)

    def test_default_mode(self):
        cli_handler = self.get_cli_handler()
        self.assertIsInstance(cli_handler.default_mode,
                              AristaDefaultCommandMode)

    def test_enable_mode(self):
        cli_handler = self.get_cli_handler()
        self.assertIsInstance(cli_handler.enable_mode,
                              AristaEnableCommandMode)

    def test_config_mode(self):
        cli_handler = self.get_cli_handler()
        self.assertIsInstance(cli_handler.config_mode,
                              AristaConfigCommandMode)

    def test_get_ssh_session(self):
        cli_handler = self.get_cli_handler(connection_type='SSH')
        self.assertIsInstance(cli_handler._new_sessions(), SSHSession)

    def test_get_telnet_session(self):
        cli_handler = self.get_cli_handler(connection_type='TELNET')
        self.assertIsInstance(cli_handler._new_sessions(), TelnetSession)

    def test_get_console_sessions(self):
        cli_handler = self.get_cli_handler(connection_type='console')
        sessions = cli_handler._new_sessions()
        console_ssh, console_telnet, console_telnet2 = sessions

        self.assertIsInstance(console_ssh, ConsoleSSHSession)
        self.assertIsInstance(console_telnet, ConsoleTelnetSession)
        self.assertIsInstance(console_telnet2, ConsoleTelnetSession)

    def test_get_sessions_by_default(self):
        cli_handler = self.get_cli_handler(connection_type='')
        sessions = cli_handler._new_sessions()
        ssh, telnet, console_ssh, console_telnet, console_telnet2 = sessions

        self.assertIsInstance(ssh, SSHSession)
        self.assertIsInstance(telnet, TelnetSession)
        self.assertIsInstance(console_ssh, ConsoleSSHSession)
        self.assertIsInstance(console_telnet, ConsoleTelnetSession)
        self.assertIsInstance(console_telnet2, ConsoleTelnetSession)

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    def test_enter_config_mode_with_lock(self, recv_mock, cb_mock, paramiko_mock):
        cli_handler = self.get_cli_handler()
        recv_mock.side_effect = ["Boogie#", "Boogie#", "Boogie#", "Boogie#", "Boogie#",
                                 "Boogie#configuration Locked", "Boogie(config)#",
                                 "Boogie(config)#", "Boogie(config)#",
                                 "Boogie(config)#", "Boogie#", "Boogie#", "Boogie#"]

        with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
            session.send_command("")

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    def test_enter_config_mode_with_multiple_retries(self, recv_mock, cb_mock, paramiko_mock):
        cli_handler = self.get_cli_handler()
        locked_message = """Boogie#
        configuration Locked
        Boogie#"""
        recv_mock.side_effect = ["Boogie#", "Boogie#", "Boogie#", "Boogie#", "Boogie#",
                                 locked_message, locked_message,
                                 locked_message, locked_message,
                                 "Boogie(config)#", "Boogie(config)#",
                                 "Boogie(config)#", "Boogie#", "Boogie#", "Boogie#"]

        with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
            session.send_command("")

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    def test_enter_config_mode_regular(self, recv_mock, cb_mock, paramiko_mock):
        cli_handler = self.get_cli_handler()
        recv_mock.side_effect = ["Boogie#", "Boogie#", "Boogie#", "Boogie#", "Boogie#",
                                 "Boogie(config)#", "Boogie(config)#",
                                 "Boogie#", "Boogie#", "Boogie#"]

        with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
            session.send_command("")

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    def test_enter_config_mode_fail(self, recv_mock, cb_mock, paramiko_mock):
        cli_handler = self.get_cli_handler()
        error_message = "Failed to create new session for type SSH, see logs for details"
        locked_message = """Boogie#
        configuration Locked
        Boogie#"""
        recv_mock.side_effect = ["Boogie#", "Boogie#", "Boogie#", "Boogie#", "Boogie#",
                                 locked_message, locked_message,
                                 locked_message, locked_message,
                                 locked_message, locked_message,
                                 locked_message, locked_message]

        try:
            with cli_handler.get_cli_service(cli_handler.enable_mode) as session:
                session.send_command("")
        except Exception as e:
            self.assertTrue(error_message in e.args)
