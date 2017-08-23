"""Display Functions for mcc utility.

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
from mcc.colors import C_NORM, C_TI, C_STAT, C_WARN
from prettytable import PrettyTable


def indx_table(node_dict, tbl_mode=False):
    """Print Table for dict=formatted list conditionally include numbers."""
    nt = PrettyTable()
    nt.header = False
    nt.padding_width = 2
    nt.border = False
    clr_num = C_TI + "NUM"
    clr_name = C_TI + "NAME"
    clr_state = "STATE" + C_NORM
    t_lu = {True: [clr_num, "NAME", "REGION", "CLOUD",
                   "SIZE", "PUBLIC IP", clr_state],
            False: [clr_name, "REGION", "CLOUD", "SIZE",
                    "PUBLIC IP", clr_state]}
    nt.add_row(t_lu[tbl_mode])
    for i, node in node_dict.items():
        state = C_STAT[node.state] + node.state + C_NORM
        inum = C_WARN + str(i) + C_NORM
        if node.public_ips:
            n_ip = node.public_ips
        else:
            n_ip = "-"
        r_lu = {True: [inum, node.name, node.zone, node.cloud,
                       node.size, n_ip, state],
                False: [node.name, node.zone, node.cloud,
                        node.size, n_ip, state]}
        nt.add_row(r_lu[tbl_mode])
    if not tbl_mode:
        print(nt)
    else:
        idx_tbl = nt.get_string()
        return idx_tbl
