# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, print_function

from subprocrunner import SubprocessRunner
from tcconfig._const import Tc
from tcconfig._converter import Humanreadable, HumanReadableTime
from typepy import RealNumber


DEADLINE_TIME = 3  # [sec]
ASSERT_MARGIN = 0.5


def is_invalid_param(
        rate, delay, packet_loss, packet_duplicate, corrupt, reordering):
    param_value_list = [
        packet_loss,
        packet_duplicate,
        corrupt,
        reordering,
    ]

    print(param_value_list)

    is_invalid = all([
        not RealNumber(param_value).is_type() or param_value <= 0
        for param_value in param_value_list
    ] + [HumanReadableTime(delay) <= HumanReadableTime("0ms")])

    try:
        Humanreadable(rate, kilo_size=1000).to_bit()
    except (TypeError, ValueError):
        pass
    else:
        is_invalid = False

    return is_invalid


def execute_tcdel(device):
    return SubprocessRunner(
        "{:s} --device {} --all".format(Tc.Command.TCDEL, device), dry_run=False).run()
