"""Determine color capability, define color vars and theme."""

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


C_STAT = {"running": C_GOOD, "start": C_GOOD, "ssh": C_NORM,
          "pending": C_WARN, "starting": C_WARN, "stopping": C_WARN,
          "stopped": C_NORM, "stop": C_NORM, "shutting-down": C_NORM,
          "terminated": C_ERR}
"""Color dictionary for instance status colors.

Any value encountered in the AWS data must be listed or a KeyError is
thrown in the function printing the color.
"""
