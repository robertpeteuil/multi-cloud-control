"""Process User Interface and execute commands..

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
from __future__ import absolute_import, print_function
from blessed import Terminal
import sys
from time import sleep
from mcc.colors import C_NORM, C_TI, C_GOOD, C_ERR, MAGENTA, C_WARN

term = Terminal()


def main(fmt_table, inst_max):
    """Create an control UI."""
    # this is the sample flow
    create_ui(fmt_table)  # print table and cmd_bar
    ui_cmd = ""
    while ui_cmd != 'quit':
        ui_cmd = get_ui_cmd()  # get user specified function
        ui_inst = 999
        while ui_inst != 0:
            ui_inst = get_ui_instance(inst_max)
            run_selected_cmd(ui_inst)


def create_ui(fmt_table, inst_max):
    """Create the base UI in command mode."""
    # print(term.enter_fullscreen())
    # print(term.move(5, 0))
    # sys.stdout.write("\033[?25l")  # turn cursor off
    print("\033[?25l", end="")  # turn cursor off
    print(fmt_table)
    print("\n\n")
    cmd_processor(fmt_table, inst_max)
    return


def uiprint(toprint):
    """Print provided text without charrage return."""
    sys.stdout.write(toprint)
    sys.stdout.flush()


def cmd_processor(fmt_table, inst_max):
    """Display Command Bar and run get-command fucntion."""
    while inst_max:
        erase_ln()
        cmd_bar = ("\r{0}ENTER COMMAND{1}\t{2}(R){1}un\t{3}"
                   "(S){1}top\t{4}(Q){1}uit:  ".
                   format(C_TI, C_NORM, C_GOOD, C_ERR, MAGENTA))
        # print("{}".format(cmd_bar), end='')
        uiprint(cmd_bar)
        # sys.stdout.flush()
        cmd_entry(inst_max)
        # sys.stdout.write("\n\n{0}".format(cmd_bar))
    return


def cmd_entry(inst_max):
    """Get main command selection."""
    with term.cbreak():
        val = ''
        while val.lower() != 'q':
            val = term.inkey()
            # val = term.inkey(timeout=300)
            # if not val:
            #     # timeout
            #     print("\nIt sure is quiet in here ...")
            if val.lower() == 'r':
                cmd_target("Run", inst_max)
                return
            elif val.is_sequence:
                uiprint("seq: {0}.".format((str(val), val.name, val.code)))
            elif val:
                uiprint("got {0}.".format(val))
    # erase_ln()
    print('exiting')
    uiprint("\033[?25h")  # turn cusor back on
    # sys.stdout.write("\033[?25h")  # turn cusor back on
    # sys.stdout.flush()
    sys.exit()


def erase_ln():
    """Erase line above and position cursor on that line."""
    uiprint("\033[A")
    # sys.stdout.write("\033[A")
    blank_ln = " " * term.width
    uiprint(blank_ln)
    # sys.stdout.write(blank_ln)
    # sys.stdout.write("\033[A")
    # sys.stdout.flush()
    return


def disp_cmd_title(cmd_title):
    """Display Title and function statement for current command."""
    uiprint(cmd_title)


def cmd_target(cmdname, inst_max):
    """Determine Instance and execute command."""
    erase_ln()
    cmd_title = ("\r'{1}{0}{2} Instance' - Select {3}Instance #{2} (0"
                 " Aborts):  ".format(cmdname, C_TI, C_NORM, C_WARN))
    disp_cmd_title(cmd_title)
    # sys.stdout.flush()
    with term.cbreak():
        inst_raw = ''
        inst_num = 999
        while inst_num != 0:
            inst_raw = term.inkey()
            # inst_raw = term.inkey(timeout=90)
            try:
                inst_num = int(inst_raw)
            except:
                inst_num = 999
            # if not inst_num:
            #     # timeout
            #     print("\nIt sure is quiet in here ...")
            if inst_num < inst_max:
                erase_ln()
                uiprint("\rRunnning Instance {}".format(inst_num))
                sleep(3)
                erase_ln()
                return
            else:
                uiprint("Invalid Entry")
                sleep(0.5)
                # no to go up, erase to right edge
                #  instead of calling erase_ln
                erase_ln()
                disp_cmd_title(cmd_title)
        uiprint("Aborting")
        sleep(1)
        erase_ln()
        return
