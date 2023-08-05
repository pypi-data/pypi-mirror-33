import argparse
import os
import sys
from typing import Tuple

from docker_ascii_map import __version__


# This code is taken from Django
def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True


def get_input_parameters() -> Tuple[bool]:
    parser = argparse.ArgumentParser(description='Display the docker host contents on a visual map.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-c', '--color', action='store_const', const='color', help='Use color in map display')
    parser.add_argument('-m', '--mono', action='store_const', const='mono', help='Render the map in monochrome')
    parser.add_argument('-f', '--follow', action='store_const', const='follow',
                        help='Follow status changes continuously')

    args = parser.parse_args()
    color_mode = supports_color()

    if args.color:
        color_mode = True

    if args.mono:
        color_mode = False

    return color_mode, args.follow is not None
