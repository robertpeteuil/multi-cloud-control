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
from collections import OrderedDict
from mcc.confdir import CONFIG_DIR
import mcc.tables as table
import mcc.cldcnct as cld
import mcc.uimode as ui
import os
import sys

__version__ = "0.0.33"


def main():
    """Retreive and display instance data then process commands."""
    (cred, providers) = config_read()
    cmd_mode = True
    while cmd_mode:
        nodes = cld.collect_data(cred, providers)
        node_dict = make_node_dict(nodes)
        idx_tbl = table.indx_table(node_dict, True)
        cmd_mode = ui.ui_main(idx_tbl, node_dict)
    print("\033[?25h")


def list_only():
    """Retreive and display instance data then exit."""
    (cred, providers) = config_read()
    nodes = cld.collect_data(cred, providers)
    table.list_table(nodes)


def make_node_dict(full_list):
    """Convert node data from nested-list to dict."""
    node_dict = {}
    x = 1
    for item in full_list:
        for node in item:
            node_dict[x] = node
            x += 1
    return node_dict


def config_read():
    """Read config info from config file."""
    config_file = (u"{0}config.ini".format(CONFIG_DIR))
    if not os.path.isfile(config_file):
        config_make(config_file)
    config = configparser.ConfigParser(allow_no_value=True)
    try:
        config.read(config_file, encoding='utf-8')
    except IOError:
        print("Error reading config file: {}".format(config_file))
        sys.exit()
    # Read and de-duplicate provider-list
    providers = config_prov(config)
    # Read credentials for each provider specified
    (cred, to_remove) = config_cred(config, providers)
    # remove unsupported and credentialess providers
    for item in to_remove:
        providers.remove(item)
    return (cred, providers)


def config_prov(config):
    """Read providers from configfile and de-duplicate it."""
    try:
        providers = [e.strip() for e in (config['info']
                                         ['providers']).split(',')]
    except KeyError as e:
        print("Error reading config item: {}".format(e))
        sys.exit()
    providers = list(OrderedDict.fromkeys(providers))
    return providers


def config_cred(config, providers):
    """Read credentials from configfile."""
    expected = ['aws', 'azure', 'gcp']
    cred = {}
    to_remove = []
    for item in providers:
        if item in expected:
            try:
                cred.update(dict(list(config[item].items())))
            except KeyError as e:
                print("No credentials section in config file for {} -"
                      " provider will be skipped.".format(e))
                to_remove.append(item)
        else:
            print("Unsupported provider: '{}' listed in config - ignoring"
                  .format(item))
            to_remove.append(item)
    return (cred, to_remove)


def config_make(config_file):
    """Create config.ini on first use, make dir and copy sample."""
    from pkg_resources import resource_filename
    import shutil
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    filename = resource_filename("mcc", "config.ini")
    try:
        shutil.copyfile(filename, config_file)
    except IOError:
        print("Error copying sample config file: {}".format(config_file))
        sys.exit()
    print("Please add credential information to {}".format(config_file))
    sys.exit()


if __name__ == '__main__':
    main()
