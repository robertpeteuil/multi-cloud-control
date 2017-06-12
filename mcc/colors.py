"""Determine color capability, define color vars and theme.

License:

    MCC - Unified CLI Utility for AWS, Azure and GCP Instance Control.
    Copyright (C) 2017  Robert Peteuil

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

URL:       https://github.com/robertpeteuil/multi-cloud-control
Author:    Robert Peteuil

"""
import sys

try:
    import colorama
    colorama.init(strip=(not sys.stdout.isatty()))
    GREEN, YELLOW, RED = (colorama.Fore.GREEN, colorama.Fore.YELLOW,
                          colorama.Fore.RED)
    BLUE, CYAN, WHITE = (colorama.Fore.BLUE, colorama.Fore.CYAN,
                         colorama.Fore.WHITE)
    MAGENTA = colorama.Fore.MAGENTA
    BRIGHT, RESET = colorama.Style.BRIGHT, colorama.Fore.RESET
except ImportError:  # pragma: no cover
    # No colorama, fallback to no-color mode
    GREEN = YELLOW = RED = BLUE = CYAN = WHITE = MAGENTA = BRIGHT = RESET = ''


C_NORM = RESET
C_HEAD = GREEN
C_HEAD2 = BLUE
C_TI = CYAN
C_TI2 = YELLOW
C_GOOD = GREEN
C_WARN = YELLOW
C_ERR = RED
"""Functionally titled vars as a psuedo color theme.

It's intended that modules will import and use these functionaly-named
vars instead of the color named vars.

This simplifies changing colors in the module using them.  To change
a color, the corresponding functional var only needs to be changed to a
different color here.  If direct color names are used, changes
require replacing all occurences of the color var being changed.
"""


C_STAT = {"running": C_GOOD, "starting": C_GOOD, "rebooting": C_WARN,
          "pending": C_WARN, "suspended": C_WARN, "paused": C_WARN,
          "stopping": C_WARN, "stopped": C_NORM, "error": C_ERR,
          "unknown": C_WARN, "reconfiguring": C_WARN, "terminated": C_NORM,
          "START": C_GOOD, "STOP": C_ERR}
"""Color dictionary for instance status colors.

Any value encountered in the AWS data must be listed or a KeyError is
thrown in the function printing the color.
"""
