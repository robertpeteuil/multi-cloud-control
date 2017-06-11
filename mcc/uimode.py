"""Process User Interface and execute commands.

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
# import os
from time import sleep
from mcc.colors import C_NORM, C_TI, C_GOOD, C_ERR, MAGENTA, C_WARN, C_STAT

term = Terminal()


def create_ui(fmt_table, node_dict):
    """Create the base UI in command mode."""
    uiprint("\033[?25l")  # turn cursor off
    print("{}\n".format(fmt_table))
    tar_valid = False
    cmd_todo = get_cmd(node_dict)
    while cmd_todo != "quit":
        uiprint(cmd_todo.title())
        sleep(0.5)
        inst_num = tar_selection(cmd_todo, len(node_dict))
        if inst_num != 0:
            (tar_valid, val_mess) = tar_validate(node_dict, inst_num, cmd_todo)
            if tar_valid:
                uiprint(val_mess)
                sleep(2)
            else:
                uiprint(val_mess)
                sleep(2)
        else:
            uiprint(" - Exit Command")
            sleep(0.5)
        cmd_todo = get_cmd(node_dict)
    uiprint("Quitting")
    uiprint("\033[?25h")  # turn cursor on
    sys.exit()


def get_cmd(node_dict):
    """Get main command selection."""
    key_cmd_lu = {"q": ["quit", True], "r": ["run", True],
                  "s": ["stop", True]}
    disp_cmd_bar()
    cmd_valid = False
    while not cmd_valid:
        with term.cbreak():
            flush_input()
            val = term.inkey()
        cmd_todo, cmd_valid = key_cmd_lu.get(val.lower(), ["invalid", False])
        if not cmd_valid:
            uiprint("{0}Invalid Entry{1}".format(C_ERR, C_NORM))
            sleep(0.5)
            disp_cmd_bar()
    return cmd_todo


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
            if inst_num <= inst_max:
                inst_valid = True
            else:
                uiprint(" - {0}Invalid Entry{1}".format(C_ERR, C_NORM))
                sleep(0.5)
                disp_cmd_title(cmd_title)
    return inst_num


def tar_validate(node_dict, inst_num, cmdname):
    """Validate that command can be performed on target node."""
    req_lu = {"run": ["stopped", "starting", "running"],
              "stop": ["running", "stopping", "stopped"]}
    if req_lu[cmdname][0] == node_dict[inst_num].state:
        tar_valid = True
        val_mess = (" - {0}{2}{1} Node".
                    format(C_STAT[req_lu[cmdname][1]], C_NORM,
                           req_lu[cmdname][1].title()))
    else:
        tar_valid = False
        val_mess = (" - {0}Aborting {1}{2} - Node Already {3}".
                    format(C_ERR, cmdname.title(), C_NORM,
                           req_lu[cmdname][2].title()))
    return (tar_valid, val_mess)


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


def flush_input():
    """Flush the input buffer on posix and windows."""
    try:
        import sys, termios  # noqa
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    except ImportError:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()


def input_by_key():
    """Get user input using inkey to prevent /n printing at end."""
    inst_num = ''
    input_valid = True
    with term.cbreak():
        while input_valid:
            flush_input()
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
