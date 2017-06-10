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
from mcc.colors import C_NORM, C_TI, C_GOOD, C_ERR, MAGENTA, C_WARN, C_STAT

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


def create_ui(fmt_table, node_dict):
    """Create the base UI in command mode."""
    # print(term.enter_fullscreen())
    # print(term.move(5, 0))
    # sys.stdout.write("\033[?25l")  # turn cursor off
    uiprint("\033[?25l")  # turn cursor off
    print("{}\n".format(fmt_table))
    cmd_processor(node_dict)
    return


def uiprint(toprint):
    """Print provided text without charrage return."""
    sys.stdout.write(toprint)
    sys.stdout.flush()


def cmd_processor(node_dict):
    """Display Command Bar and run get-command fucntion."""
    while node_dict:
        cmd_bar = ("\rENTER COMMAND -   {2}(R){1}un Node   {3}"
                   "(S){1}top Node   {4}(Q){1}uit:  ".
                   format(C_TI, C_NORM, C_GOOD, C_ERR, MAGENTA))
        uiprint(cmd_bar)
        cmd_entry(node_dict)
        erase_ln()
    return


def cmd_entry(node_dict):
    """Get main command selection."""
    with term.cbreak():
        val = ''
        while val.lower() != 'q':
            val = term.inkey()
            # val = term.inkey(timeout=300)
            if val.lower() == 'r':
                uiprint("Run")
                sleep(0.75)
                cmd_target("run", node_dict)
                return
            if val.lower() == 's':
                uiprint("Stop")
                sleep(0.75)
                cmd_target("stop", node_dict)
                return
            elif val.is_sequence:
                uiprint("seq: {0}.".format((str(val), val.name, val.code)))
            # elif val:
            #     uiprint("got {0}.".format(val))
    uiprint("Quitting")
    uiprint("\033[?25h")  # turn cusor back on
    sys.exit()


def erase_ln():
    """Erase line above and position cursor on that line."""
    blank_ln = " " * term.width
    # ORIGINAL WORKING METHOD
    # uiprint("\033[A")
    # uiprint(blank_ln)

    # NEW METHOD - don't need to go up
    uiprint("\r{}".format(blank_ln))
    return


def disp_cmd_title(cmd_title):
    """Display Title and function statement for current command."""
    erase_ln()
    uiprint(cmd_title)


def cmd_target(cmdname, node_dict):
    """Determine Node and execute command."""
    cmd_display_lu = {"run": "RUNNING", "stop": "STOPPING"}
    cmdaction = cmd_display_lu.get(cmdname, "unknown")
    cmddisp = cmdname.upper()
    inst_max = len(node_dict)
    cmd_title = ("\r{1}{0} NODE{2} - Select {3}NODE #{2}"
                 " ({4}0 = Exit{2}):  ".
                 format(cmddisp, C_TI, C_NORM, C_WARN, MAGENTA))
    disp_cmd_title(cmd_title)
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
            if inst_num == 0:
                uiprint("Exiting {0}{2}{1} COMMAND".
                        format(C_WARN, C_NORM, cmddisp))
                sleep(1)
                return
            if inst_num < inst_max:
                erase_ln()
                uiprint("\r{2}{0} NODE{3}: {4}{1}{3}".
                        format(cmdaction, inst_num,
                               C_STAT[cmdaction.lower()], C_NORM, C_WARN))
                sleep(3)
                return
            else:
                uiprint("{0}Invalid Entry{1}".format(C_ERR, C_NORM))
                sleep(1)
                disp_cmd_title(cmd_title)
                # Alternate method:
                #   go up & only erase-line to right edge
                #   instead of calling erase_ln & re-printing title
