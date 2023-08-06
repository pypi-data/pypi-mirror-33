from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters

from cloudshell.networking.arista.cli.arista_cli_handler import AristaCliHandler
from cloudshell.networking.arista.command_actions.enable_disable_snmp_actions \
    import EnableDisableSnmpActions


class AristaEnableSnmpFlow(EnableSnmpFlow):
    def __init__(self, cli_handler, logger):
        """
        Enable snmp flow
        :param AristaCliHandler cli_handler:
        :param logger:
        :return:
        """
        super(AristaEnableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler

    def execute_flow(self, snmp_parameters):
        if hasattr(snmp_parameters, "snmp_community") and not snmp_parameters.snmp_community:
            message = 'SNMP community cannot be empty'
            self._logger.error(message)
            raise Exception(self.__class__.__name__, message)

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as session:
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                snmp_actions = EnableDisableSnmpActions(config_session, self._logger)
                if isinstance(snmp_parameters, SNMPV3Parameters):
                    raise Exception(self.__class__.__name__, 'Do not support SNMP V3')
                else:
                    if not snmp_actions.is_configured(snmp_parameters.snmp_community):
                        snmp_actions.enable_snmp(snmp_parameters.snmp_community)
                    else:
                        self._logger.debug("SNMP Community '{}' already configured".format(
                            snmp_parameters.snmp_community))

                self._logger.info("Start verification of SNMP config")
                if not snmp_actions.is_configured(snmp_parameters.snmp_community):
                    raise Exception(self.__class__.__name__, "Failed to create SNMP community." +
                                    " Please check Logs for details")
