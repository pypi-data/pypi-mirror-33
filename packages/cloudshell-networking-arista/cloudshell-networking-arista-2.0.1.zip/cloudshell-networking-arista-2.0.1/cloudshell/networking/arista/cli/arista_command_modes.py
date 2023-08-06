import re
import time

from cloudshell.cli.command_mode import CommandMode


class AristaDefaultCommandMode(CommandMode):
    PROMPT = r'>\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''

    def __init__(self, resource_config, api):
        """
        Initialize Default command mode, only for cases when session started not in enable mode

        :param resource_config:
        """

        self.resource_config = resource_config
        self._api = api

        CommandMode.__init__(
            self,
            AristaDefaultCommandMode.PROMPT,
            AristaDefaultCommandMode.ENTER_COMMAND,
            AristaDefaultCommandMode.EXIT_COMMAND,
        )


class AristaEnableCommandMode(CommandMode):
    PROMPT = r'(?:(?!\)).)#\s*$'
    ENTER_COMMAND = 'enable'
    EXIT_COMMAND = ''

    def __init__(self, resource_config, api):
        """
        Initialize Enable command mode - default command mode for Arista Shells

        :param resource_config:
        """

        self.resource_config = resource_config
        self._api = api
        self._enable_password = None

        CommandMode.__init__(
            self,
            AristaEnableCommandMode.PROMPT,
            AristaEnableCommandMode.ENTER_COMMAND,
            AristaEnableCommandMode.EXIT_COMMAND,
            enter_action_map=self.enter_action_map(),
        )

    @property
    def enable_password(self):
        if not self._enable_password:
            password = self.resource_config.enable_password
            self._enable_password = self._api.DecryptPassword(password).Value
        return self._enable_password

    def enter_action_map(self):
        return {
            "[Pp]assword":
                lambda session, logger: session.send_line(self.enable_password, logger)
        }


class AristaConfigCommandMode(CommandMode):
    MAX_ENTER_CONFIG_MODE_RETRIES = 5
    ENTER_CONFIG_RETRY_TIMEOUT = 5
    PROMPT = r'\(config.*\)#\s*$'
    ENTER_COMMAND = 'configure terminal'
    EXIT_COMMAND = 'end'

    def __init__(self, resource_config, api):
        """
        Initialize Config command mode

        :param resource_config:
        """
        self.resource_config = resource_config
        self._api = api

        CommandMode.__init__(
            self,
            AristaConfigCommandMode.PROMPT,
            AristaConfigCommandMode.ENTER_COMMAND,
            AristaConfigCommandMode.EXIT_COMMAND,
            enter_action_map=self.enter_action_map(),

        )

    def enter_action_map(self):
        return {r"{}.*$".format(AristaEnableCommandMode.PROMPT): self._check_config_mode}

    def _check_config_mode(self, session, logger):
        error_message = "Failed to enter config mode, please check logs, for details"
        conf_prompt = AristaConfigCommandMode.PROMPT
        enable_prompt = AristaEnableCommandMode.PROMPT

        retry = 0
        output = session.hardware_expect("", "{0}|{1}".format(conf_prompt, enable_prompt), logger)
        while not re.search(conf_prompt, output) and retry < self.MAX_ENTER_CONFIG_MODE_RETRIES:
            output = session.hardware_expect(
                AristaConfigCommandMode.ENTER_COMMAND,
                "{0}|{1}".format(enable_prompt, conf_prompt),
                logger)
            time.sleep(self.ENTER_CONFIG_RETRY_TIMEOUT)
            retry += 1

        if not re.search(conf_prompt, output):
            raise Exception(error_message)


CommandMode.RELATIONS_DICT = {
    AristaDefaultCommandMode: {
        AristaEnableCommandMode: {
            AristaConfigCommandMode: {}
        }
    }
}
