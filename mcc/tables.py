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


def list_table(all_nodes):
    """Print Table for NEW nested-list all_nodes."""
    h_name = C_TI + "NAME"
    h_state = "STATE" + C_NORM
    nt = PrettyTable()
    nt.header = False
    nt.add_row([h_name, "REGION", "CLOUD", "SIZE", "PUBLIC IP", h_state])
    nt.padding_width = 2
    nt.border = False
    for item in all_nodes:
        for node in item:
            state = C_STAT[node.state] + node.state + C_NORM
            if node.public_ips:
                n_ip = node.public_ips
            else:
                n_ip = "-"
            nt.add_row([node.name, node.zone, node.cloud, node.size,
                        n_ip, state])
    print(nt)


def indx_table(node_dict, strmode=False):
    """Print Table for NEW dict=formatted list."""
    h_nm = C_TI + "NUM"
    h_state = "STATE" + C_NORM
    nt = PrettyTable()
    nt.header = False
    nt.add_row([h_nm, "NAME", "REGION", "CLOUD", "SIZE", "PUBLIC IP", h_state])
    nt.padding_width = 2
    nt.border = False
    for i, node in node_dict.items():
        state = C_STAT[node.state] + node.state + C_NORM
        inum = C_WARN + str(i) + C_NORM
        if node.public_ips:
            n_ip = node.public_ips
        else:
            n_ip = "-"
        nt.add_row([inum, node.name, node.zone, node.cloud, node.size,
                    n_ip, state])
    if not strmode:
        print(nt)
    else:
        idx_tbl = nt.get_string()
        return idx_tbl
