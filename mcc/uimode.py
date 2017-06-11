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
# from builtins import input
from blessed import Terminal
import sys
from termios import tcflush, TCIFLUSH
# import os
from time import sleep
from mcc.colors import C_NORM, C_TI, C_GOOD, C_ERR, MAGENTA, C_WARN

term = Terminal()


def create_ui(fmt_table, node_dict):
    """Create the base UI in command mode."""
    uiprint("\033[?25l")  # turn cursor off
    print("{}\n".format(fmt_table))
    tar_valid = False
    cmd_todo = get_cmd(node_dict)
    while cmd_todo != "quit":
        inst_num = tar_selection(cmd_todo, len(node_dict))
        if inst_num != 0:
            tar_valid = tar_validate(node_dict, inst_num, cmd_todo)
            if tar_valid:
                uiprint(" - valid target")
                sleep(1.5)
            else:
                uiprint(" - bad target node")
                sleep(1.5)
        else:
            uiprint(" - Exit Command")
            sleep(0.5)
        cmd_todo = get_cmd(node_dict)
    uiprint("Quitting")
    uiprint("\033[?25h")  # turn cursor on
    sys.exit()


# def create_ui_old(fmt_table, node_dict):
#     """Create the base UI in command mode."""
#     uiprint("\033[?25l")  # turn cursor off
#     print("{}\n".format(fmt_table))
#     get_cmd(node_dict)
#     return


def uiprint(toprint):
    """Print text without charrage return."""
    sys.stdout.write(toprint)
    sys.stdout.flush()


def disp_cmd_title(cmd_title):
    """Display Title and function statement for current command."""
    disp_erase_ln()
    uiprint(cmd_title)


def disp_cmd_bar():
    """Display Command Bar."""
    cmd_bar = ("\rSELECT COMMAND -   {2}(R){1}un Node   {3}"
               "(S){1}top Node   {4}(Q){1}uit:  ".
               format(C_TI, C_NORM, C_GOOD, C_ERR, MAGENTA))
    disp_erase_ln()
    uiprint(cmd_bar)


def disp_erase_ln():
    """Erase line above and position cursor on that line."""
    blank_ln = " " * term.width
    # uiprint("\033[A")   # go up one line
    uiprint("\r{}".format(blank_ln))
    return


# def get_cmd(node_dict):
#     """Display Command Bar and run get-command fucntion."""
#     while node_dict:
#         cmd_bar = ("\rENTER COMMAND -   {2}(R){1}un Node   {3}"
#                    "(S){1}top Node   {4}(Q){1}uit:  ".
#                    format(C_TI, C_NORM, C_GOOD, C_ERR, MAGENTA))
#         uiprint(cmd_bar)
#         cmd_entry(node_dict)
#         disp_erase_ln()
#     return


def get_cmd(node_dict):
    """Get main command selection."""
    disp_cmd_bar()
    cmd_valid = False
    # cmd_todo = ""
    # val = ''
    # while val.lower() != 'q':
    while not cmd_valid:
        with term.cbreak():
            tcflush(sys.stdin, TCIFLUSH)
            val = term.inkey()
        if val.lower() == 'q':
            cmd_todo = "quit"
            cmd_valid = True
            # break
            # uiprint("Quitting")
            # uiprint("\033[?25h")  # turn cusor back on
            # sys.exit()
        elif val.lower() == 'r':
            cmd_todo = "run"
            cmd_valid = True
            uiprint("Run")
            sleep(0.5)
            # break
            # tar_selection("run", node_dict)
            # disp_cmd_bar()
        elif val.lower() == 's':
            cmd_todo = "stop"
            cmd_valid = True
            uiprint("Stop")
            sleep(0.5)
            # break
            # tar_selection("stop", node_dict)
            # # cmd_target("stop", node_dict)
            # disp_cmd_bar()
        # elif val.is_sequence:
        #     uiprint("seq: {0}.".format((str(val), val.name, val.code)))
        else:
            uiprint("{0}Invalid Entry{1}".format(C_ERR, C_NORM))
            sleep(0.5)
            disp_cmd_bar()
    return cmd_todo


# def cmd_target(cmdname, node_dict):
#     """Determine Node and execute command."""
#     # cmd_display_lu = {"run": "RUNNING", "stop": "STOPPING"}
#     # cmdaction = cmd_display_lu.get(cmdname, "unknown")
#     cmddisp = cmdname.upper()
#     inst_max = len(node_dict)
#     cmd_title = ("\r{1}{0} NODE{2} - Select {3}NODE #{2}"
#                  " ({4}0 = Exit Command{2}):  ".
#                  format(cmddisp, C_TI, C_NORM, C_WARN, MAGENTA))
#     disp_cmd_title(cmd_title)
#
#     inst_raw = ''
#     inst_num = 999
#     while inst_num != 0:
#         with term.cbreak():
#             inst_raw = term.inkey()
#         try:
#             inst_num = int(inst_raw)
#         except ValueError:
#             inst_num = 999
#         if inst_num == 0:
#             # uiprint("Exiting {0}{2}{1} COMMAND".
#             #         format(C_WARN, C_NORM, cmddisp))
#             # uiprint("Returning to Main")
#             uiprint("Exit Command")
#             sleep(0.5)
#             return
#         elif inst_num < inst_max:
#             uiprint(str(inst_num))
#             sleep(0.25)
#             tar_validate(node_dict, inst_num, cmdname)
#             # uiprint(" - {1}{0} NODE{2}".
#             #         format(cmdaction, C_STAT[cmdaction.lower()], C_NORM))
#             # sleep(2.5)
#             return
#         else:
#             uiprint("{0}Invalid Entry{1}".format(C_ERR, C_NORM))
#             sleep(0.5)
#             disp_cmd_title(cmd_title)
#             # Alternate method:
#             #   go up & only erase-line to right edge
#             #   instead of calling disp_erase_ln & re-printing title


def input_by_key():
    """Get user input using inkey to prevent /n printing at end."""
    # key_raw = ''
    inst_num = ''
    input_valid = True
    with term.cbreak():
        while input_valid:
            tcflush(sys.stdin, TCIFLUSH)
            key_raw = term.inkey()
            if key_raw.name == "KEY_ENTER":
                input_valid = False
                break
            if key_raw.name == 'KEY_DELETE':
                inst_num = inst_num[:-1]
                uiprint("\033[D \033[D")
            if not key_raw.is_sequence:
                inst_num += key_raw
                uiprint(key_raw)
        try:
            inst_num = int(inst_num)
        except ValueError:
            inst_num = 99999
    return inst_num


def tar_selection(cmdname, inst_max):
    """Determine Node via alternate input method."""
    cmddisp = cmdname.upper()
    cmd_title = ("\r{1}{0} NODE{2} - Enter {3}NODE #{2} and 'enter'"
                 " ({4}0 = Exit Command{2}):  ".
                 format(cmddisp, C_TI, C_NORM, C_WARN, MAGENTA))
    disp_cmd_title(cmd_title)
    inst_valid = False
    with term.cbreak():
        while not inst_valid:
            inst_num = input_by_key()
            # if inst_num == 0:
            #     uiprint(" - Exit Command")
            #     sleep(0.5)
            #     return
            if inst_num <= inst_max:
                inst_valid = True
                # tar_validate(node_dict, inst_num, cmdname)
                # return
            else:
                uiprint(" - {0}Invalid Entry{1}".format(C_ERR, C_NORM))
                sleep(0.5)
                disp_cmd_title(cmd_title)
    return inst_num


def tar_validate(node_dict, inst_num, cmdname):
    """Validate that command can be performed on target node."""
    req_state_lu = {"run": ["stopped", "running"],
                    "stop": ["running", "stopped"]}
    # req_state = req_state_lu[cmdname][0]
    # tar_state = node_dict[inst_num].state
    if req_state_lu[cmdname][0] == node_dict[inst_num].state:
        tar_valid = True
        uiprint(" - {} node".format(req_state_lu[cmdname][1]))
        sleep(0.5)
    else:
        tar_valid = False
        uiprint(" - node already {}".format(req_state_lu[cmdname][1]))
        sleep(0.5)
    return tar_valid
