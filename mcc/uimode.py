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
from builtins import range
from blessed import Terminal
import sys
from mcc.cldcnct import busy_disp_on, busy_disp_off
from time import sleep
from mcc.colors import C_NORM, C_TI, C_GOOD, C_ERR, MAGENTA, C_WARN, C_STAT
from gevent import monkey

monkey.patch_all()
term = Terminal()


def ui_main(fmt_table, node_dict):
    """Create the base UI in command mode."""
    uiprint("\033[?25l")  # turn cursor off
    print("{}\n".format(fmt_table))
    sys.stdout.flush()
    tar_valid = False
    cmd_todo = get_cmd(node_dict)
    while cmd_todo != "quit":
        inst_num = tar_selection(cmd_todo, len(node_dict))
        if inst_num != 0:
            (tar_valid, tar_mess) = tar_validate(node_dict, inst_num, cmd_todo)
            if tar_valid:
                cmd_result = cmd_exec(node_dict[inst_num], cmd_todo, tar_mess)
                uiprint("- {}".format(cmd_result))
                sleep(1)
                if cmd_result != "Command Aborted":
                    # datalines = len(node_dict) + 2
                    disp_clear(len(node_dict))
                    return True
            else:
                uiprint(tar_mess)
                sleep(2)
        else:
            uiprint(" - Exit")
            sleep(0.2)
        cmd_todo = get_cmd(node_dict)
    uiprint("\033[?25h")  # turn cursor on
    return False


def get_cmd(node_dict):
    """Get main command selection."""
    key_cmd_lu = {"q": ["quit", True], "r": ["run", True],
                  "s": ["stop", True]}
    disp_cmd_bar()
    cmd_valid = False
    while not cmd_valid:
        with term.cbreak():
            flush_input()
            val = input_by_key()
        cmd_todo, cmd_valid = key_cmd_lu.get(val.lower(), ["invalid", False])
        if not cmd_valid:
            uiprint(" - {0}Invalid Entry{1}".format(C_ERR, C_NORM))
            sleep(0.5)
            disp_cmd_bar()
    return cmd_todo


def tar_selection(cmdname, inst_max):
    """Determine Node via alternate input method."""
    cmddisp = cmdname.upper()
    cmd_title = ("\r{1}{0} NODE{2} - Enter {3}Node #{2}"
                 " ({4}0 = Exit Command{2}):  ".
                 format(cmddisp, C_TI, C_NORM, C_WARN, MAGENTA))
    disp_cmd_title(cmd_title)
    inst_valid = False
    with term.cbreak():
        while not inst_valid:
            inst_num = input_by_key()
            try:
                inst_num = int(inst_num)
            except ValueError:
                inst_num = 99999
            if inst_num <= inst_max:
                inst_valid = True
            else:
                uiprint(" - {0}Invalid Entry{1}".format(C_ERR, C_NORM))
                sleep(0.5)
                disp_cmd_title(cmd_title)
    return inst_num


def tar_validate(node_dict, inst_num, cmdname):
    """Validate that command can be performed on target node."""
    # cmd: [required-state, action-to-be-performed, already state]
    req_lu = {"run": ["stopped", "START", "running"],
              "stop": ["running", "STOP", "stopped"]}
    # req_lu = {"run": ["stopped", "starting", "running"],
    #           "stop": ["running", "stopping", "stopped"]}
    if req_lu[cmdname][0] == node_dict[inst_num].state:
        tar_valid = True
        tar_mess = ("{0}{2}{1} Node {3}{4}{1} ({5} on {6})".
                    format(C_STAT[req_lu[cmdname][1]], C_NORM,
                           req_lu[cmdname][1], C_WARN, inst_num,
                           node_dict[inst_num].name,
                           node_dict[inst_num].cloud))
        # tar_mess = ("{0}{2}{1} Node {3}{4}{1} '{5}'".
        #             format(C_STAT[req_lu[cmdname][1]], C_NORM,
        #                    req_lu[cmdname][1].title(), C_WARN, inst_num,
        #                    node_dict[inst_num].name))
    else:
        tar_valid = False
        tar_mess = (" - Node Already {2} - {0}Aborting{1}".
                    format(C_ERR, C_NORM, req_lu[cmdname][2].title()))
    return (tar_valid, tar_mess)


def cmd_exec(tar_node, cmdname, tar_mess):
    """Confirm command and execute it."""
    cmd_lu = {"run": ["ex_start_node", "wait_until_running", "Successfull"],
              "stop": ["ex_stop_node", "", "Initiated"]}
    conf_mess = ("\r{0} - Continue? [y/N] ".
                 format(tar_mess))
    if input_yn(conf_mess):
        exec_mess = "\rEXECUTING COMMAND - {0}  ".format(tar_mess)
        disp_erase_ln()
        uiprint(exec_mess)
        busy_obj = busy_disp_on()  # turn on busy indicator
        cmd_one = cmd_lu[cmdname][0]
        cmd_two = cmd_lu[cmdname][1]
        cmdpre = getattr(tar_node, "driver")
        maincmd = getattr(cmdpre, cmd_one)
        response = maincmd(tar_node)  # noqa
        if cmd_two:
            cmdpre = getattr(tar_node, "driver")
            seccmd = getattr(cmdpre, cmd_two)
            response = seccmd([tar_node])  # noqa
        cmd_result = "{0} {1}".format(cmdname.title(),
                                      cmd_lu[cmdname][2])
        if cmdname == "stop" and tar_node.cloud == "azure":
            sleep(3)
        busy_disp_off(busy_obj)  # turn off busy indicator
    else:
        cmd_result = "Command Aborted"
    return cmd_result


def input_yn(conf_mess):
    """Print Confirmation Message and Get Y/N response from user."""
    disp_erase_ln()
    uiprint(conf_mess)
    with term.cbreak():
        flush_input()
        val = input_by_key()
        sleep(0.5)
    return bool(val.lower() == 'y')


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


def disp_clear(numlines):
    """Clear previous display info from screen in prep for new data."""
    numlines += 2
    disp_erase_ln()
    for i in range(numlines, 0, -1):
        uiprint("\033[A")
        disp_erase_ln()


def disp_erase_ln():
    """Erase line above and position cursor on that line."""
    blank_ln = " " * (term.width - 1)
    uiprint("\r{0}".format(blank_ln))
    return


def flush_input():
    """Flush the input buffer on posix and windows."""
    try:
        import sys, termios  # noqa
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except ImportError:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()


def input_by_key():
    """Get user input using inkey to prevent /n printing at end."""
    usr_inp = ''
    input_valid = True
    flush_input()
    with term.cbreak():
        while input_valid:
            uiprint("\033[?25h")  # turn cursor on
            key_raw = term.inkey()
            if key_raw.name == "KEY_ENTER":
                input_valid = False
                uiprint("\033[?25l")  # turn cursor off
                break
            if key_raw.name == 'KEY_DELETE':
                usr_inp = usr_inp[:-1]
                uiprint("\033[D \033[D")
            if not key_raw.is_sequence:
                usr_inp += key_raw
                uiprint(key_raw)
    return usr_inp
