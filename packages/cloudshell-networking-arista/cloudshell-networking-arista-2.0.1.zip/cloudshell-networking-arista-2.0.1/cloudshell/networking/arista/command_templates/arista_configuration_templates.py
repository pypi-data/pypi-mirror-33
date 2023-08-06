from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

BOOT_SYSTEM_FILE = CommandTemplate("boot system flash:{firmware_file_name}")
SHOW_BOOT = CommandTemplate("show boot")

ACTION_MAP = OrderedDict()
ERROR_MAP = OrderedDict([(r'[Ee]rror:', 'Command error')])

SHOW_SNMP_COMMUNITY = CommandTemplate('show snmp community', action_map=ACTION_MAP, error_map=ERROR_MAP)
ENABLE_SNMP = CommandTemplate('snmp-server community {snmp_community} ro', action_map=ACTION_MAP, error_map=ERROR_MAP)
DISABLE_SNMP = CommandTemplate('no snmp-server community {snmp_community}', action_map=ACTION_MAP, error_map=ERROR_MAP)

