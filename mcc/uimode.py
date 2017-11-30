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
from mcc.colors import C_NORM, C_TI, C_GOOD, C_ERR, C_WARN, C_STAT, C_HEAD2
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
    ui_print("\033[?25l")  # cursor off
    print("{}\n".format(fmt_table))
    sys.stdout.flush()
    # refresh_main values:
    #   None = loop main-cmd, True = refresh-list, False = exit-program
    refresh_main = None
    while refresh_main is None:
        cmd_name = get_user_cmd(node_dict)
        if callable(cmd_funct[cmd_name]):
            refresh_main = cmd_funct[cmd_name](cmd_name, node_dict)
        else:
            refresh_main = cmd_funct[cmd_name]
    if cmd_name != "connect" and refresh_main:
        ui_clear(len(node_dict) + 2)
    return refresh_main


def get_user_cmd(node_dict):
    """Get main command selection."""
    key_lu = {"q": ["quit", True], "r": ["run", True],
              "s": ["stop", True], "u": ["update", True],
              "c": ["connect", True], "d": ["details", True]}
    ui_cmd_bar()
    cmd_valid = False
    input_flush()
    with term.cbreak():
        while not cmd_valid:
            val = input_by_key()
            cmd_name, cmd_valid = key_lu.get(val.lower(), ["invalid", False])
            if not cmd_valid:
                ui_print(" - {0}Invalid Entry{1}".format(C_ERR, C_NORM))
                sleep(0.5)
                ui_cmd_bar()
    return cmd_name


def node_cmd(cmd_name, node_dict):
    """Process commands that target specific nodes."""
    sc = {"run": cmd_startstop, "stop": cmd_startstop,
          "connect": cmd_connect, "details": cmd_details}
    node_num = node_selection(cmd_name, len(node_dict))
    refresh_main = None
    if node_num != 0:
        (node_valid, node_info) = node_validate(node_dict, node_num, cmd_name)
        if node_valid:
            sub_cmd = sc[cmd_name]  # get sub-command
            refresh_main = sub_cmd(node_dict[node_num], cmd_name, node_info)
        else:  # invalid target
            ui_print_suffix(node_info, C_ERR)
            sleep(1.5)
    else:  # '0' entered - exit command but not program
        ui_print(" - Exit Command")
        sleep(0.5)
    return refresh_main


def node_selection(cmd_name, node_qty):
    """Determine Node via alternate input method."""
    cmd_disp = cmd_name.upper()
    cmd_title = ("\r{1}{0} NODE{2} - Enter {3}#{2}"
                 " ({4}0 = Exit Command{2}): ".
                 format(cmd_disp, C_TI, C_NORM, C_WARN, C_HEAD2))
    ui_cmd_title(cmd_title)
    selection_valid = False
    input_flush()
    with term.cbreak():
        while not selection_valid:
            node_num = input_by_key()
            try:
                node_num = int(node_num)
            except ValueError:
                node_num = 99999
            if node_num <= node_qty:
                selection_valid = True
            else:
                ui_print_suffix("Invalid Entry", C_ERR)
                sleep(0.5)
                ui_cmd_title(cmd_title)
    return node_num


def node_validate(node_dict, node_num, cmd_name):
    """Validate that command can be performed on target node."""
    # cmd: [required-state, action-to-displayed, error-statement]
    req_lu = {"run": ["stopped", "Already Running"],
              "stop": ["running", "Already Stopped"],
              "connect": ["running", "Can't Connect, Node Not Running"],
              "details": [node_dict[node_num].state, ""]}
    tm = {True: ("Node {1}{2}{0} ({5}{3}{0} on {1}{4}{0})".
                 format(C_NORM, C_WARN, node_num,
                        node_dict[node_num].name,
                        node_dict[node_num].cloud_disp, C_TI)),
          False: req_lu[cmd_name][1]}
    node_valid = bool(req_lu[cmd_name][0] == node_dict[node_num].state)
    node_info = tm[node_valid]
    return node_valid, node_info


def cmd_startstop(node, cmd_name, node_info):
    """Confirm command and execute it."""
    cmd_lu = {"run": ["ex_start_node", "wait_until_running", "RUNNING"],
              "stop": ["ex_stop_node", "", "STOPPING"]}
    # specific delay & message {provider: {command: [delay, message]}}
    cld_lu = {"azure": {"stop": [6, "Initiated"]},
              "aws": {"stop": [6, "Initiated"]}}
    conf_mess = ("\r{0}{1}{2} {3} - Confirm [y/N]: ".
                 format(C_STAT[cmd_name.upper()], cmd_name.upper(), C_NORM,
                        node_info))
    cmd_result = None
    if input_yn(conf_mess):
        exec_mess = ("\r{0}{1}{2} {3}:  ".
                     format(C_STAT[cmd_name.upper()], cmd_lu[cmd_name][2],
                            C_NORM, node_info))
        ui_erase_ln()
        ui_print(exec_mess)
        busy_obj = busy_disp_on()  # busy indicator ON
        node_drv = getattr(node, "driver")
        main_cmd = getattr(node_drv, cmd_lu[cmd_name][0])
        response = main_cmd(node)  # noqa
        cmd_wait = cmd_lu[cmd_name][1]
        if cmd_wait:
            seccmd = getattr(node_drv, cmd_wait)
            response = seccmd([node])  # noqa
        delay, cmd_end = cld_lu.get(node.cloud,
                                    {}).get(cmd_name, [0, "Successful"])
        sleep(delay)
        busy_disp_off(busy_obj)  # busy indicator OFF
        ui_print("\033[D")  # remove extra space
        cmd_result = True
        ui_print_suffix("{0} {1}".format(cmd_name.title(), cmd_end), C_GOOD)
        sleep(1.5)
    else:
        ui_print_suffix("Command Aborted")
        sleep(0.75)
    return cmd_result


def cmd_connect(node, cmd_name, node_info):
    """Connect to node."""
    # FUTURE: call function to check for custom connection-info
    conn_info = "Defaults"
    conf_mess = ("\r{0}{1} TO{2} {3} using {5}{4}{2} - Confirm [y/N]: ".
                 format(C_STAT[cmd_name.upper()], cmd_name.upper(), C_NORM,
                        node_info, conn_info, C_HEAD2))
    cmd_result = None
    if input_yn(conf_mess):
        exec_mess = ("\r{0}CONNECTING TO{1} {2} using {4}{3}{1}: ".
                     format(C_STAT[cmd_name.upper()], C_NORM, node_info,
                            conn_info, C_HEAD2))
        ui_erase_ln()
        ui_print(exec_mess)
        (ssh_user, ssh_key) = ssh_get_info(node)
        if ssh_user:
            ssh_cmd = "ssh {0}{1}@{2}".format(ssh_key, ssh_user,
                                              node.public_ips)
        else:
            ssh_cmd = "ssh {0}{1}".format(ssh_key, node.public_ips)
        print("\n")
        ui_print("\033[?25h")  # cursor on
        subprocess.call(ssh_cmd, shell=True)
        ui_print("\033[?25l")  # cursor off
        print()
        cmd_result = True
    else:
        ui_print_suffix("Command Aborted")
        sleep(0.75)
    return cmd_result


def cmd_details(node, cmd_name, node_info):
    """Display Node details."""
    ui_print_suffix("Command Aborted")
    return None


def ssh_get_info(node):
    """Determine ssh-user and ssh-key for node."""
    ssh_key = ""
    if node.cloud == "aws":
        raw_key = node.extra['key_name']
        ssh_key = "-i {0}{1}.pem ".format(CONFIG_DIR, raw_key)
        ssh_user = ssh_calc_aws(node)
    elif node.cloud == "azure":
        ssh_user = node.extra['properties']['osProfile']['adminUsername']
    else:
        items = node.extra['metadata'].get('items', [{}])
        keyname = items['key' == 'ssh-keys'].get('value', "")
        pos = keyname.find(":")
        ssh_user = keyname[0:pos]
    return ssh_user, ssh_key


def ssh_calc_aws(node):
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


def ui_print(to_print):
    """Print text without carriage return."""
    sys.stdout.write(to_print)
    sys.stdout.flush()


def ui_print_suffix(to_print, clr=C_WARN):
    """Print Colored Suffix Message after command."""
    ui_print(" - {1}{0}{2}".format(to_print, clr, C_NORM))


def ui_cmd_title(cmd_title):
    """Display Title and function statement for current command."""
    ui_erase_ln()
    ui_print(cmd_title)


def ui_cmd_bar():
    """Display Command Bar."""
    cmd_bar = ("\rSELECT COMMAND -  {2}(R){1}un   {0}(C){1}onnect   "
               "{3}(S){1}top   {0}(U){1}pdate"
               "   {0}(Q){1}uit: ".
               format(C_TI, C_NORM, C_GOOD, C_ERR))
    # FUTURE - TO BE USED WHEN DETAILS IMPLEMENTED
    # cmd_bar = ("\rSELECT COMMAND -  {2}(R){1}un   {0}(C){1}onnect   "
    #            "{3}(S){1}top   {0}(D){1}etails   {0}(U){1}pdate Info"
    #            "   {4}(Q){1}uit: ".
    #            format(C_TI, C_NORM, C_GOOD, C_ERR, C_HEAD2))
    ui_erase_ln()
    ui_print(cmd_bar)


def ui_del_char(check_len):
    """Move Left and delete one character."""
    if check_len:
        ui_print("\033[D \033[D")


def ui_clear(num_lines):
    """Clear previous display info from screen in prep for new data."""
    ui_erase_ln()
    for i in range(num_lines, 0, -1):
        ui_print("\033[A")
        ui_erase_ln()


def ui_erase_ln():
    """Erase line above and position cursor on that line."""
    blank_ln = " " * (term.width - 1)
    ui_print("\r{0}".format(blank_ln))


def input_flush():
    """Flush the input buffer on posix and windows."""
    try:
        import sys, termios  # noqa
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except ImportError:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()


def input_by_key():
    """Get user input using term.inkey to prevent /n printing at end."""
    usr_inp = ''
    input_valid = True
    input_flush()
    with term.cbreak():
        while input_valid:
            ui_print("\033[?25h")  # cursor on
            key_raw = term.inkey()
            if key_raw.name == "KEY_ENTER":
                input_valid = False
                ui_print("\033[?25l")  # cursor off
                break
            if key_raw.name == 'KEY_DELETE':
                ui_del_char(len(usr_inp))
                usr_inp = usr_inp[:-1]
            if not key_raw.is_sequence:
                usr_inp += key_raw
                ui_print(key_raw)
    if not usr_inp:
        ui_print("\033[D")
    return usr_inp


def input_yn(conf_mess):
    """Print Confirmation Message and Get Y/N response from user."""
    ui_erase_ln()
    ui_print(conf_mess)
    with term.cbreak():
        input_flush()
        val = input_by_key()
    return bool(val.lower() == 'y')
