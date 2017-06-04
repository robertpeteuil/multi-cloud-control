"""Unified CLI Utility for AWS, Azure and GCP Instance Control.

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
import configparser
from mcc.confdir import CONFIG_DIR
import mcc.tables as table
import mcc.conncloud as conn
import os
# from pprint import pprint
import sys

__version__ = "0.0.20"


def main():
    """Retreive and display instance data then process commands."""
    (nodes, conn_objs) = initialize()
    node_dict = make_node_dict(nodes)
    table.indx_table(node_dict)
    # idx_tbl = table.indx_table(node_dict)

    # print(idx_tbl)
    # pprint(conn_objs)
    # pprint(node_dict)


def list_only():
    """Retreive and display instance data then exit."""
    (nodes, conn_objs) = initialize()
    table.list_table(nodes)


def initialize():
    """Read Config file and retrieve instance data."""
    (cred, providers) = read_config()
    (nodes, conn_objs) = conn.begin_collect(cred, providers)
    return (nodes, conn_objs)


def make_node_dict(nodes):
    """Convert node data from nested-list to dict."""
    node_dict = {}
    x = 1
    for item in nodes:
        for node in item:
            node_dict[x] = node
            x += 1
    return node_dict


def read_config():
    """Read config file and gather credentials."""
    cred = {}
    config_file = (u"{0}config.ini".format(CONFIG_DIR))
    if not os.path.isfile(config_file):
        make_config(config_file)
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(config_file, encoding='utf-8')
    providers = [e.strip() for e in (config['info']['providers']).split(',')]
    for item in providers:
        cred.update(dict(list(config[item].items())))
    return (cred, providers)


def make_config(config_file):
    """Create config.ini on first use, make dir and copy sample."""
    from pkg_resources import resource_filename
    import shutil
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    filename = resource_filename("mcc", "config.ini")
    shutil.copyfile(filename, config_file)
    print("Please add credential information to {}".format(config_file))
    sys.exit()


if __name__ == '__main__':
    main()
