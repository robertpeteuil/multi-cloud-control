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
from mcc.confdir import CONFIG_DIR
import sys
from mcc.cldcnct import busy_disp_on, busy_disp_off
from time import sleep
from mcc.colors import C_NORM, C_TI, C_GOOD, C_ERR, MAGENTA, C_WARN, C_STAT
from gevent import monkey
from gevent import subprocess

monkey.patch_all()
term = Terminal()


def ui_main(fmt_table, node_dict):
    """Create the base UI in command mode."""
    cmd_funct = {"quit": False,
                 "run": node_cmd,
                 "stop": node_cmd,
                 "connect": node_cmd,
                 "details": node_cmd,
                 "update": True}
    uiprint("\033[?25l")  # cursor off
    print("{}\n".format(fmt_table))
    sys.stdout.flush()
    # refresh_main values:
    #   None = loop main-cmd, True = refresh-list, False = exit-program
    refresh_main = None
    while refresh_main is None:
        cmd_todo = get_cmd(node_dict)
        if callable(cmd_funct[cmd_todo]):
            refresh_main = cmd_funct[cmd_todo](cmd_todo, node_dict)
        else:
            refresh_main = cmd_funct[cmd_todo]
    if refresh_main:
        disp_clear(len(node_dict) + 2)
    # else:
    #     uiprint("\033[?25h")  # cursor on
    return refresh_main


def get_cmd(node_dict):
    """Get main command selection."""
    key_lu = {"q": ["quit", True], "r": ["run", True],
              "s": ["stop", True], "u": ["update", True],
              "c": ["connect", True], "d": ["details", True]}
    disp_cmd_bar()
    cmd_valid = False
    flush_input()
    with term.cbreak():
        while not cmd_valid:
            val = input_by_key()
            cmd_todo, cmd_valid = key_lu.get(val.lower(), ["invalid", False])
            if not cmd_valid:
                uiprint(" - {0}Invalid Entry{1}".format(C_ERR, C_NORM))
                sleep(0.5)
                disp_cmd_bar()
    return cmd_todo


def node_cmd(cmd_todo, node_dict):
    """Process commands that target specific nodes."""
    sc = {"run": cmd_startstop, "stop": cmd_startstop,
          "connect": cmd_conn, "details": cmd_details}
    node_qty = len(node_dict)
    inst_num = tar_selection(cmd_todo, node_qty)
    refresh_main = None
    if inst_num != 0:
        (tar_valid, tar_mess) = tar_validate(node_dict, inst_num, cmd_todo)
        if tar_valid:
            subcmd = sc[cmd_todo]  # get dynamic sub-command
            refresh_main = subcmd(node_dict[inst_num], cmd_todo,
                                  tar_mess, node_qty)
            # cmd_result = subcmd(node_dict[inst_num], cmd_todo,
            #                     tar_mess, node_qty)
            # if cmd_result == "Connect Successful":
            #     print(term.clear)  # clear screen after ssh session
            #     print(term.move_y(node_qty + 2))
            #     refresh_main = True
            # else:
            #     if cmd_result == "Command Aborted":
            #         c_result = C_WARN
            #     else:
            #         refresh_main = True
            #         c_result = C_GOOD
            #     uiprint_suffix(cmd_result, c_result)
            #     sleep(1)
        else:  # invalid target
            uiprint_suffix(tar_mess, C_ERR)
            sleep(1.5)
    else:  # 0 - exit command but not program
        uiprint(" - Exit Command")
        sleep(0.5)
    return refresh_main


def tar_selection(cmdname, inst_max):
    """Determine Node via alternate input method."""
    cmddisp = cmdname.upper()
    cmd_title = ("\r{1}{0} NODE{2} - Enter {3}#{2}"
                 " ({4}0 = Exit Command{2}): ".
                 format(cmddisp, C_TI, C_NORM, C_WARN, MAGENTA))
    disp_cmd_title(cmd_title)
    inst_valid = False
    flush_input()
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
                uiprint_suffix("Invalid Entry", C_ERR)
                sleep(0.5)
                disp_cmd_title(cmd_title)
    return inst_num


def tar_validate(node_dict, inst_num, cmdname):
    """Validate that command can be performed on target node."""
    # cmd: [required-state, action-to-displayed, error-statement]
    req_lu = {"run": ["stopped", "Already Running"],
              "stop": ["running", "Already Stopped"],
              "connect": ["running", "Can't Connect, Node Not Running"],
              "details": [node_dict[inst_num].state, ""]}
    tm = {True: ("Node {1}{2}{0} ({5}{3}{0} on {1}{4}{0})".
                 format(C_NORM, C_WARN, inst_num,
                        node_dict[inst_num].name,
                        node_dict[inst_num].cloud_disp, C_TI)),
          False: req_lu[cmdname][1]}
    tar_valid = bool(req_lu[cmdname][0] == node_dict[inst_num].state)
    tar_mess = tm[tar_valid]
    return (tar_valid, tar_mess)


def cmd_startstop(tar_node, cmdname, tar_mess, node_qty):
    """Confirm command and execute it."""
    cmd_lu = {"run": ["ex_start_node", "wait_until_running", "RUNNING"],
              "stop": ["ex_stop_node", "", "STOPPING"]}
    # specific delay & message {provider: {command: [delay, message]}}
    cld_lu = {"azure": {"stop": [5, "Initiated"]}}
    conf_mess = ("\r{0}{1}{2} {3} - Confirm [y/N]: ".
                 format(C_STAT[cmdname.upper()], cmdname.upper(), C_NORM,
                        tar_mess))
    cmd_result = None
    if input_yn(conf_mess):
        exec_mess = ("\r{0}{1}{2} {3}:  ".
                     format(C_STAT[cmdname.upper()], cmd_lu[cmdname][2],
                            C_NORM, tar_mess))
        disp_erase_ln()
        uiprint(exec_mess)
        busy_obj = busy_disp_on()  # busy indicator ON
        cmdpre = getattr(tar_node, "driver")
        maincmd = getattr(cmdpre, cmd_lu[cmdname][0])
        response = maincmd(tar_node)  # noqa
        cmd_wait = cmd_lu[cmdname][1]
        if cmd_wait:
            seccmd = getattr(cmdpre, cmd_wait)
            response = seccmd([tar_node])  # noqa
        delay, cmd_end = cld_lu.get(tar_node.cloud,
                                    {}).get(cmdname, [0, "Successful"])
        # result_msg = "{0} {1}".format(cmdname.title(), cmd_end)
        # uiprint_suffix(result_msg, C_GOOD)
        sleep(delay)
        busy_disp_off(busy_obj)  # busy indicator OFF
        uiprint("\033[D")  # remove extra space
        cmd_result = True
        uiprint_suffix("{0} {1}".format(cmdname.title(), cmd_end), C_GOOD)
    else:
        uiprint_suffix("Command Aborted")
        # result_msg = "Command Aborted"
        # result_clr = C_WARN
    # uiprint_suffix(result_msg, result_clr)
    sleep(1)
    return cmd_result


def cmd_conn(tar_node, cmdname, tar_mess, node_qty):
    """Connect to node."""
    # FUTURE: call function to check for custom connection-info
    conn_info = "Defaults"
    conf_mess = ("\r{0}{1} TO{2} {3} using {4}{5}{2} - Confirm [y/N]: ".
                 format(C_STAT[cmdname.upper()], cmdname.upper(), C_NORM,
                        tar_mess, C_TI, conn_info))
    cmd_result = None
    if input_yn(conf_mess):
        exec_mess = ("\r{0}CONNECTING TO{1} {2} using {3}{4}{1}:  ".
                     format(C_STAT[cmdname.upper()], C_NORM, tar_mess,
                            C_TI, conn_info))
        disp_erase_ln()
        uiprint(exec_mess)
        (ssh_user, ssh_key) = get_sshinfo(tar_node)
        if ssh_user:
            ssh_cmd = "ssh {0}{1}@{2}".format(ssh_key, ssh_user,
                                              tar_node.public_ips)
        else:
            ssh_cmd = "ssh {0}{1}".format(ssh_key, tar_node.public_ips)
        print("\n")
        uiprint("\033[?25h")  # cursor on
        # retval = subprocess.call(ssh_cmd, shell=True)
        subprocess.call(ssh_cmd, shell=True)
        uiprint("\033[?25l")  # cursor off
        # print(retval)
        # sleep(2)
        # result_msg = "Connect Successful"
        uiprint("\033[D")  # remove extra space
        cmd_result = True
        uiprint_suffix("Connect Successful", C_GOOD)
        print(term.clear)  # clear screen after ssh session
        print(term.move_y(node_qty + 2))
        # if retval:
        #     uiprint("\033[A\033[A\033[A")
        #     disp_erase_ln()
        #     uiprint("\nFailed wit SSH Command: {}".format(ssh_cmd))
        #     sleep(10)
        #     result_msg = "Connect Failed"
        # else:
        #     result_msg = "Connect Successful"
    else:
        # result_msg = "Command Aborted"
        uiprint_suffix("Command Aborted")
        sleep(1)
    return cmd_result


def get_sshinfo(node):
    """Determine ssh-user and ssh-key for node."""
    ssh_key = ""
    if node.cloud == "aws":
        raw_key = node.extra['key_name']
        ssh_key = "-i {0}{1}.pem ".format(CONFIG_DIR, raw_key)
        ssh_user = calc_awsssh(node)
    elif node.cloud == "azure":
        ssh_user = node.extra['properties']['osProfile']['adminUsername']
    else:
        items = node.extra['metadata'].get('items', [{}])
        keyname = items['key' == 'ssh-keys'].get('value', "")
        pos = keyname.find(":")
        ssh_user = keyname[0:pos]
    return (ssh_user, ssh_key)


def calc_awsssh(node):
    """Calculate default ssh-user based on image-if of AWS instance."""
    userlu = {"ubunt": "ubuntu", "debia": "admin", "fedor": "root",
              "cento": "centos", "openb": "root"}
    image_name = node.driver.get_image(node.extra['image_id']).name
    if not image_name:
        image_name = node.name
    usertemp = ['name'] + [value for key, value in list(userlu.items())
                           if key in image_name.lower()]
    usertemp = dict(zip(usertemp[::2], usertemp[1::2]))
    username = usertemp.get('name', 'ec2-user')
    return username


def cmd_details(tar_node, cmdname, tar_mess, node_qty):
    """Display Node details."""
    uiprint_suffix("Command Aborted")
    return None


def input_yn(conf_mess):
    """Print Confirmation Message and Get Y/N response from user."""
    disp_erase_ln()
    uiprint(conf_mess)
    with term.cbreak():
        flush_input()
        val = input_by_key()
    return bool(val.lower() == 'y')


def uiprint(toprint):
    """Print text without charrage return."""
    sys.stdout.write(toprint)
    sys.stdout.flush()


def uiprint_suffix(toprint, clr=C_WARN):
    """Print Colored Suffix Message after command."""
    uiprint(" - {1}{0}{2}".format(toprint, clr, C_NORM))


def disp_cmd_title(cmd_title):
    """Display Title and function statement for current command."""
    disp_erase_ln()
    uiprint(cmd_title)


def disp_cmd_bar():
    """Display Command Bar."""
    cmd_bar = ("\rSELECT COMMAND -  {2}(R){1}un   {0}(C){1}onnect   "
               "{3}(S){1}top   {0}(U){1}pdate Info"
               "   {4}(Q){1}uit: ".
               format(C_TI, C_NORM, C_GOOD, C_ERR, MAGENTA))
    # FUTURE - TO BE USED WHEN DETAILS IMPLEMENTED
    # cmd_bar = ("\rSELECT COMMAND -  {2}(R){1}un   {0}(C){1}onnect   "
    #            "{3}(S){1}top   {0}(D){1}etails   {0}(U){1}pdate Info"
    #            "   {4}(Q){1}uit: ".
    #            format(C_TI, C_NORM, C_GOOD, C_ERR, MAGENTA))
    disp_erase_ln()
    uiprint(cmd_bar)


def disp_clear(numlines):
    """Clear previous display info from screen in prep for new data."""
    disp_erase_ln()
    for i in range(numlines, 0, -1):
        uiprint("\033[A")
        disp_erase_ln()


def disp_erase_ln():
    """Erase line above and position cursor on that line."""
    blank_ln = " " * (term.width - 1)
    uiprint("\r{0}".format(blank_ln))


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
            uiprint("\033[?25h")  # cursor on
            key_raw = term.inkey()
            if key_raw.name == "KEY_ENTER":
                input_valid = False
                uiprint("\033[?25l")  # cursor off
                break
            if key_raw.name == 'KEY_DELETE':
                del_one_char(len(usr_inp))
                usr_inp = usr_inp[:-1]
            if not key_raw.is_sequence:
                usr_inp += key_raw
                uiprint(key_raw)
    if not usr_inp:
        uiprint("\033[D")
    return usr_inp


def del_one_char(check_len):
    """Move Left and delete one character."""
    if check_len:
        uiprint("\033[D \033[D")
