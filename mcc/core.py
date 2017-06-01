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
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from mcc.colors import C_NORM, C_TI, C_STAT
from mcc.configdir import CONFIG_DIR
from pkg_resources import resource_filename
from prettytable import PrettyTable
import os
import shutil
import sys

__version__ = "0.0.10"


def main():
    nodes = []
    cld_svc_map = {"aws": collect_aws_nodes,
                   "azure": collect_az_nodes,
                   "gcp": collect_gcp_nodes}

    (providers, cred) = read_creds()

    for item in providers:
        nodes += cld_svc_map[item](cred)

    print_table(nodes)
    # print()
    # print_indx_table(nodes)


def read_creds():
    config_file = (u"{0}config.ini".format(CONFIG_DIR))
    check_config(config_file)
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    providers = [e.strip() for e in (config['info']['providers']).split(',')]
    cred = {}
    for item in providers:
        cred.update(dict(list(config[item].items())))
    return (providers, cred)


def check_config(config_file):
    if not os.path.isfile(config_file):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        filename = resource_filename("mcc", "config.ini")
        # filename = resource_filename(Requirement.parse("mcc"), "config.ini")
        shutil.copyfile(filename, config_file)
        print("Please add credential information to {}".format(config_file))
        sys.exit()


def collect_aws_nodes(cred):
    aws_nodes = []
    driver = get_driver(Provider.EC2)
    aws_obj = driver(cred['aws_access_key_id'],
                     cred['aws_secret_access_key'],
                     region=cred['aws_default_region'])
    aws_nodes = aws_obj.list_nodes()
    for node in aws_nodes:
        node.cloud = "AWS"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['availability']
        node.size = node.extra['instance_type']
        node.type = node.extra['instance_lifecycle']
    return aws_nodes


def collect_az_nodes(cred):
    az_nodes = []
    driver = get_driver(Provider.AZURE_ARM)
    az_obj = driver(tenant_id=cred['az_tenant_id'],
                    subscription_id=cred['az_sub_id'],
                    key=cred['az_app_id'],
                    secret=cred['az_app_sec'])
    az_nodes = az_obj.list_nodes()
    for node in az_nodes:
        node.cloud = "Azure"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['location']
        node.size = node.extra['properties']['hardwareProfile']['vmSize']
        group_raw = node.id
        unnsc, group_end = group_raw.split("resourceGroups/", 1)
        group, unnsc = group_end.split("/", 1)
        node.group = group
    return az_nodes


def collect_gcp_nodes(cred):
    gcp_nodes = []
    driver = get_driver(Provider.GCE)
    gcp_pem = CONFIG_DIR + cred['gcp_pem_file']
    gcp_obj = driver(cred['gcp_svc_acct_email'],
                     gcp_pem,
                     project=cred['gcp_proj_id'])
    gcp_nodes = gcp_obj.list_nodes()
    for node in gcp_nodes:
        node.cloud = "GCP"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['zone'].name
    return gcp_nodes


def ip_to_str(raw_ip):
    if raw_ip:
        raw_ip = raw_ip[0]
    else:
        raw_ip = None
    return raw_ip


def print_table(all_nodes):
    h_name = C_TI + "NAME"
    h_state = "STATE" + C_NORM
    nt = PrettyTable()
    nt.header = False
    nt.add_row([h_name, "CLOUD", "REGION", "SIZE", "PUBLIC IP", h_state])
    nt.padding_width = 2
    nt.border = False
    for node in all_nodes:
        state = C_STAT[node.state] + node.state + C_NORM
        if node.public_ips:
            n_ip = node.public_ips
        else:
            n_ip = "-"
        nt.add_row([node.name, node.cloud, node.zone, node.size,
                    n_ip, state])
    print(nt)


def print_indx_table(all_nodes):
    node_list = {}
    for i, j in enumerate(all_nodes):
        node_list[i] = j
    h_nm = C_TI + "NUM"
    h_state = "STATE" + C_NORM
    nt = PrettyTable()
    nt.header = False
    nt.add_row([h_nm, "NAME", "CLOUD", "REGION", "SIZE", "PUBLIC IP", h_state])
    nt.padding_width = 2
    nt.border = False
    for i, node in node_list.items():
        state = C_STAT[node.state] + node.state + C_NORM
        if node.public_ips:
            n_ip = node.public_ips
        else:
            n_ip = "-"
        nt.add_row([i + 1, node.name, node.cloud, node.zone, node.size,
                    n_ip, state])
    print(nt)


if __name__ == '__main__':
    main()
