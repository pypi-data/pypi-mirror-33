from cloudshell.cli.session.ssh_session import SSHSession


class ConsoleSSHSession(SSHSession):
    SESSION_TYPE = 'CONSOLE_SSH'
