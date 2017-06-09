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


def create_ui(fmt_table):
    """Create the base UI in command mode."""
    inst_max = 5  # max # of instances - need to pass here from main
    # print(term.enter_fullscreen())
    # print(term.move(5, 0))
    sys.stdout.write("\033[?25l")  # turn cursor off
    print(fmt_table)
    cmd_bar = "ENTER COMMAND -  (R)un   (S)top   (Q)uit:  "
    # sys.stdout.wrt("\n\n{0:<{width}}".format(cmd_bar, width=term.width - 2))
    # width = term.width - 2
    # sys.stdout.write("\n\n{0:<{1}}".format(cmd_bar, width))
    sys.stdout.write("\n\n{0}".format(cmd_bar))
    sys.stdout.flush()
    # print(term.move(term.height - 4, 0) + cmd_bar)

    with term.cbreak():
        val = ''
        while val.lower() != 'q':
            val = term.inkey(timeout=90)
            if not val:
                # timeout
                print("\nIt sure is quiet in here ...")
            elif val.lower() == 'r':
                cmd_run(inst_max)
                erase_ln()
            elif val.is_sequence:
                print("\nseq: {0}.".format((str(val), val.name, val.code)))
            elif val:
                print("\ngot {0}.".format(val))
    print('exiting')
    sys.stdout.write("\033[?25h")  # turn cusor back on
    sys.stdout.flush()
    # print(term.exit_fullscreen())


def erase_ln():
    sys.stdout.write("\033[A")
    blank_ln = " " * term.width
    sys.stdout.write(blank_ln)
    sys.stdout.write("\033[A")
    sys.stdout.flush()


def cmd_run(inst_max):
    """Execute Run Instance Command."""
    sys.stdout.write("\n'Run Instance' - Select Instance (0 Aborts):  ")
    sys.stdout.flush()
    with term.cbreak():
        inst_raw = ''
        inst_num = 999
        while inst_num != 0:
            inst_raw = term.inkey(timeout=90)
            try:
                inst_num = int(inst_raw)
            except:
                inst_num = 0
            if not inst_num:
                # timeout
                print("\nIt sure is quiet in here ...")
            elif inst_num < inst_max:
                print("\nRunnning Instance {}".format(inst_num))
                sleep(1)
                erase_ln()
                return
            else:
                print("\nInvalid Entry")
                sleep(0.5)
                erase_ln()
        print("Aborting")
        sleep(1)
        erase_ln()
        return
