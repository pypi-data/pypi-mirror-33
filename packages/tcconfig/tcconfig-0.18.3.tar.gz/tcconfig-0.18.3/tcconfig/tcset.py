#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, print_function, unicode_literals

import errno
import ipaddress
import sys

import logbook
import msgfy
import pyparsing as pp
import six
import subprocrunner as spr
import typepy

from .__version__ import __version__
from ._argparse_wrapper import ArgparseWrapper
from ._capabilities import check_execution_authority
from ._common import initialize_cli, is_execute_tc_command, normalize_tc_value
from ._const import (
    IPV6_OPTION_ERROR_MSG_FORMAT, Network, ShapingAlgorithm, Tc, TcCommandOutput, TrafficDirection)
from ._converter import HumanReadableTime
from ._error import ModuleNotFoundError, NetworkInterfaceNotFoundError, ParameterError
from ._logger import logger, set_log_level
from ._shaping_rule_finder import TcShapingRuleFinder
from ._tc_script import write_tc_script
from .traffic_control import TrafficControl


def get_arg_parser():
    parser = ArgparseWrapper(__version__)

    group = parser.parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-d", "--device",
        help="network device name (e.g. eth0)")
    group.add_argument(
        "-f", "--config-file",
        help="setting traffic controls from a configuration file. output file of the tcshow.")

    group = parser.parser.add_mutually_exclusive_group()
    group.add_argument(
        "--overwrite", action="store_true", default=False,
        help="overwrite existing traffic shaping rules.")
    group.add_argument(
        "--change", dest="is_change_shaping_rule", action="store_true",
        default=False,
        help="""change existing traffic shaping rules to the new one. this option reduces
        the shaping rule switching side effect (such as traffic spike) compared to
        --overwrite option.
        note: the tcset command adds a shaping rule if there are no existing shaping rules.
        """)
    group.add_argument(
        "--add", dest="is_add_shaping_rule", action="store_true",
        default=False,
        help="add a traffic shaping rule in addition to existing rules.")

    group = parser.parser.add_argument_group("Traffic Control Parameters")
    group.add_argument(
        "--rate", "--bandwidth-rate", dest="bandwidth_rate",
        help="""network bandwidth rate [bit per second].
        valid units are either: K/M/G/Kbps/Mbps/Gbps
        e.g. --rate 10Mbps
        """)
    group.add_argument(
        "--delay", dest="network_latency",
        default=Tc.ValueRange.LatencyTime.MIN,
        help="""round trip network delay. the valid range is from {min_value:} to {max_value:}.
        valid time units are: {unit}. if no unit string found, considered milliseconds as
        the time unit. (default=%(default)s)
        """.format(
            min_value=Tc.ValueRange.LatencyTime.MIN,
            max_value=Tc.ValueRange.LatencyTime.MAX,
            unit="/".join(HumanReadableTime.get_valid_unit_list())))
    group.add_argument(
        "--delay-distro", dest="latency_distro_time",
        default=Tc.ValueRange.LatencyTime.MIN,
        help="""distribution of network latency becomes X +- Y (normal distribution).
        Here X is the value of --delay option and Y is the value of --delay-dist option).
        network latency distribution is uniform, without this option. valid time units are: {unit}.
        if no unit string found, considered milliseconds as the time unit.
        """.format(unit="/".join(HumanReadableTime.get_valid_unit_list())))
    group.add_argument(
        "--loss", dest="packet_loss_rate", type=float, default=0,
        help="""round trip packet loss rate [%%]. the valid range is from {:d}
        to {:d}. (default=%(default)s)
        """.format(
            TrafficControl.MIN_PACKET_LOSS_RATE,
            TrafficControl.MAX_PACKET_LOSS_RATE))
    group.add_argument(
        "--duplicate", dest="packet_duplicate_rate", type=float, default=0,
        help="""round trip packet duplicate rate [%%]. the valid range is
        from {:d} to {:d}. (default=%(default)s)
        """.format(
            TrafficControl.MIN_PACKET_DUPLICATE_RATE,
            TrafficControl.MAX_PACKET_DUPLICATE_RATE))
    group.add_argument(
        "--corrupt", dest="corruption_rate", type=float, default=0,
        help="""packet corruption rate [%%]. the valid range is from {:d} to {:d}.
        packet corruption means single bit error at a random offset in the packet.
        (default=%(default)s)
        """.format(
            TrafficControl.MIN_CORRUPTION_RATE,
            TrafficControl.MAX_CORRUPTION_RATE))
    group.add_argument(
        "--reordering", dest="reordering_rate", type=float, default=0,
        help="""packet reordering rate [%%]. the valid range is from {:d}
        to {:d}. (default=%(default)s)
        """.format(
            TrafficControl.MIN_REORDERING_RATE,
            TrafficControl.MAX_REORDERING_RATE))
    group.add_argument(
        "--shaping-algo", dest="shaping_algorithm",
        choices=[ShapingAlgorithm.HTB, ShapingAlgorithm.HTB],
        default=ShapingAlgorithm.HTB,
        help="shaping algorithm. defaults to %(default)s (recommended).")
    group.add_argument(
        "--iptables", dest="is_enable_iptables",
        action="store_true", default=False,
        help="use iptables to traffic control.")

    group = parser.add_routing_group()
    group.add_argument(
        "--exclude-dst-network",
        help="exclude a shaping rule for a specific destination IP-address/network.")
    group.add_argument(
        "--exclude-src-network",
        help="exclude a shaping rule for a specific source IP-address/network.")
    group.add_argument(
        "--exclude-dst-port",
        help="exclude a shaping rule for a specific destination port.")
    group.add_argument(
        "--exclude-src-port",
        help="exclude a shaping rule for a specific source port.")

    return parser.parser


def verify_netem_module():
    import re

    runner = spr.SubprocessRunner("lsmod")

    try:
        if runner.run() != 0:
            raise OSError(runner.returncode, "failed to execute lsmod")
    except spr.CommandError as e:
        # reach here when the kmod package not installed.
        # this kind of environments could exist such as slim containers.
        logger.debug(msgfy.to_debug_message(e))
    else:
        if re.search(r"\bsch_netem\b", runner.stdout) is None:
            raise ModuleNotFoundError("sch_netem module not found")


class TcConfigLoader(object):
    def __init__(self, logger):
        self.__logger = logger
        self.__config_table = None
        self.is_overwrite = False

    def load_tcconfig(self, config_file_path):
        import json
        from voluptuous import Schema, Required, Any, ALLOW_EXTRA

        schema = Schema({
            Required(six.text_type): {
                Any(*TrafficDirection.LIST): {
                    six.text_type: {
                        six.text_type: Any(six.text_type, int, float)
                    },
                }
            },
        }, extra=ALLOW_EXTRA)

        with open(config_file_path) as fp:
            self.__config_table = json.load(fp)

        schema(self.__config_table)
        self.__logger.debug("tc config file: {:s}".format(
            json.dumps(self.__config_table, indent=4)))

    def get_tcconfig_command_list(self):
        command_list = []

        for device, device_table in six.iteritems(self.__config_table):
            device_option = "--device={:s}".format(device)

            if self.is_overwrite:
                command_list.append("{:s} {:s}".format(
                    Tc.Command.TCDEL, device_option))

            for direction, direction_table in six.iteritems(device_table):
                is_first_set = True

                for tc_filter, filter_table in six.iteritems(direction_table):
                    self.__logger.debug("is_first_set={}, filter='{}', table={}".format(
                        is_first_set, tc_filter, filter_table))

                    if not filter_table:
                        continue

                    option_list = [
                        device_option,
                        "--direction={:s}".format(direction),
                    ]
                    for key, value in six.iteritems(filter_table):
                        arg_item = "--{:s}={}".format(key, value)

                        parse_result = get_arg_parser().parse_known_args(
                            ["--device", "dummy", arg_item])
                        if parse_result[1]:
                            self.__logger.debug("unknown parameter: key={}, value={}".format(
                                key, value))
                            continue

                        option_list.append(arg_item)

                    try:
                        dst_network = self.__parse_tc_filter_network(tc_filter)
                        if dst_network not in (Network.Ipv4.ANYWHERE, Network.Ipv6.ANYWHERE):
                            option_list.append("--dst-network={:s}".format(dst_network))
                    except pp.ParseException:
                        pass

                    try:
                        src_port = self.__parse_tc_filter_src_port(tc_filter)
                        option_list.append("--src-port={}".format(src_port))
                    except pp.ParseException:
                        pass

                    try:
                        dst_port = self.__parse_tc_filter_dst_port(tc_filter)
                        option_list.append("--dst-port={}".format(dst_port))
                    except pp.ParseException:
                        pass

                    if not is_first_set:
                        option_list.append("--add")

                    is_first_set = False

                    command_list.append(" ".join([Tc.Command.TCSET] + option_list))

        return command_list

    @staticmethod
    def __parse_tc_filter_network(text):
        network_pattern = (
            pp.SkipTo("{:s}=".format(Tc.Param.DST_NETWORK), include=True) +
            pp.Word(pp.alphanums + "." + "/"))

        return network_pattern.parseString(text)[-1]

    @staticmethod
    def __parse_tc_filter_src_port(text):
        port_pattern = (
            pp.SkipTo("{:s}=".format(Tc.Param.SRC_PORT), include=True) +
            pp.Word(pp.nums))

        return port_pattern.parseString(text)[-1]

    @staticmethod
    def __parse_tc_filter_dst_port(text):
        port_pattern = (
            pp.SkipTo("{:s}=".format(Tc.Param.DST_PORT), include=True) +
            pp.Word(pp.nums))

        return port_pattern.parseString(text)[-1]


def set_tc_from_file(logger, config_file_path, is_overwrite):
    return_code = 0

    loader = TcConfigLoader(logger)
    loader.is_overwrite = is_overwrite

    try:
        loader.load_tcconfig(config_file_path)
    except IOError as e:
        logger.error(msgfy.to_error_message(e))
        return errno.EIO

    for tcconfig_command in loader.get_tcconfig_command_list():
        return_code |= spr.SubprocessRunner(tcconfig_command).run()

    return return_code


def main():
    options = get_arg_parser().parse_args()

    initialize_cli(options)

    if is_execute_tc_command(options.tc_command_output):
        check_execution_authority("tc")

        if options.direction == TrafficDirection.INCOMING:
            check_execution_authority("ip")
    else:
        spr.SubprocessRunner.default_is_dry_run = True

    try:
        verify_netem_module()
    except ModuleNotFoundError as e:
        logger.debug(e)

    if typepy.is_not_null_string(options.config_file):
        return set_tc_from_file(logger, options.config_file, options.overwrite)

    spr.SubprocessRunner.clear_history()

    tc = TrafficControl(
        options.device,
        direction=options.direction,
        bandwidth_rate=options.bandwidth_rate,
        latency_time=options.network_latency,
        latency_distro_time=options.latency_distro_time,
        packet_loss_rate=options.packet_loss_rate,
        packet_duplicate_rate=options.packet_duplicate_rate,
        corruption_rate=options.corruption_rate,
        reordering_rate=options.reordering_rate,
        dst_network=options.dst_network,
        exclude_dst_network=options.exclude_dst_network,
        src_network=options.src_network,
        exclude_src_network=options.exclude_src_network,
        src_port=options.src_port,
        exclude_src_port=options.exclude_src_port,
        dst_port=options.dst_port,
        exclude_dst_port=options.exclude_dst_port,
        is_ipv6=options.is_ipv6,
        is_change_shaping_rule=options.is_change_shaping_rule,
        is_add_shaping_rule=options.is_add_shaping_rule,
        is_enable_iptables=options.is_enable_iptables,
        shaping_algorithm=options.shaping_algorithm,
        tc_command_output=options.tc_command_output,
    )

    try:
        tc.validate()
    except NetworkInterfaceNotFoundError as e:
        logger.error(e)
        return errno.EINVAL
    except ipaddress.AddressValueError as e:
        logger.error(IPV6_OPTION_ERROR_MSG_FORMAT.format(e))
        return errno.EINVAL
    except ParameterError as e:
        logger.error(msgfy.to_error_message(e))
        return errno.EINVAL

    normalize_tc_value(tc)

    if options.overwrite:
        if options.log_level == logbook.INFO:
            set_log_level(logbook.ERROR)

        try:
            tc.delete_all_tc()
        except NetworkInterfaceNotFoundError:
            pass

        set_log_level(options.log_level)

    if (options.is_add_shaping_rule and
            TcShapingRuleFinder(logger=logger, tc=tc).is_exist_rule()):
        logger.error("\n".join([
            "adding a shaping rule failed. a shaping rule for the same network/port "
            "already exist. try to execute with:",
            "  (a) --overwrite option if you want to overwrite the existing rules.",
            "  (b) --change option if you want to change the existing rule parameter.",
        ]))
        return errno.EINVAL

    try:
        return_code = tc.set_tc()
    except NetworkInterfaceNotFoundError as e:
        logger.error(e)
        return errno.EINVAL

    command_history = "\n".join(tc.get_command_history())

    if options.tc_command_output == TcCommandOutput.STDOUT:
        print(command_history)
        return 0

    if options.tc_command_output == TcCommandOutput.SCRIPT:
        write_tc_script(Tc.Command.TCSET, command_history, filename_suffix=options.device)
        return 0

    logger.debug("command history\n{}".format(command_history))

    return return_code


if __name__ == '__main__':
    sys.exit(main())
