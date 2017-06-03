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
from mcc.confdir import CONFIG_DIR
import mcc.dispout as disp
from multiprocessing import Pool
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool
import os
from pprint import pprint
import sys

__version__ = "0.0.18"
# cred = {}


def main():
    """Retreive and display instance data then process commands."""
    (nodes, conn_objs) = initialize()
    node_dict = conv_data(nodes)
    disp.indx_table(node_dict)

    pprint(conn_objs)
    # pprint(node_dict)


def list_only():
    """Retreive and display instance data then exit."""
    (nodes, conn_objs) = initialize()
    disp.list_table(nodes)


def initialize():
    """Read Config file and retrieve instance data."""
    (cred, providers) = read_config()
    (nodes, conn_objs) = collect_data(cred, providers)
    return (nodes, conn_objs)


def conv_data(nodes):
    """Convert node data from nested-list to dit."""
    node_dict = {}
    x = 1
    for item in nodes:
        for node in item:
            node_dict[x] = node
            x += 1
    return node_dict


def collect_data(cred, providers):
    """Orchestrate collection of node data from all providers with a pool."""
    cld_svc_map = {"aws": [aws_conn, aws_nodes],
                   "azure": [az_conn, az_nodes],
                   "gcp": [gcp_conn, gcp_nodes]}
    (procs, thrds) = pool_sizer()
    pool = Pool(procs)
    conn_r = {}
    for i, item in enumerate(providers):
        conn_r[item] = pool.apply_async(get_conn, [cld_svc_map[item][0], cred])
    conn_objs = {}
    for k, v in conn_r.items():
        conn_objs[k] = v.get()
    node_r = {}
    pool = ThreadPool(thrds)
    for i, item in enumerate(providers):
        node_r[i] = pool.apply_async(get_nodes, [cld_svc_map[item][1],
                                                 conn_objs[item]])
    pool.close()
    pool.join()
    del pool
    node_list = []
    for i in node_r:
        node_list.append(node_r[i].get())
    return (node_list, conn_objs)


def pool_sizer():
    """Determine number of processes to create based on CPU."""
    if cpu_count() > 2:
        procs = 3
        thrds = 9
    else:
        procs = cpu_count()
        thrds = 6
    return (procs, thrds)


def get_conn(funcnm, cred):
    """Call function and make connection."""
    conn_obj = []
    conn_obj = funcnm(cred)
    return conn_obj


def get_nodes(funcnm, c_obj):
    """Call function and retreive info."""
    rinfo = []
    rinfo = funcnm(c_obj)
    return rinfo


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


def aws_conn(cred):
    """Establish connection to AWS service."""
    driver = get_driver(Provider.EC2)
    aws_obj = driver(cred['aws_access_key_id'],
                     cred['aws_secret_access_key'],
                     region=cred['aws_default_region'])
    return aws_obj


def aws_nodes(c_obj):
    """Collect nodes from AWS and retreive details specific to AWS."""
    aws_nodes = []
    aws_nodes = c_obj.list_nodes()
    for node in aws_nodes:
        node.cloud = "aws"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['availability']
        node.size = node.extra['instance_type']
        node.type = node.extra['instance_lifecycle']
    return aws_nodes


def az_conn(cred):
    """Establish connection to Azure service."""
    driver = get_driver(Provider.AZURE_ARM)
    az_obj = driver(tenant_id=cred['az_tenant_id'],
                    subscription_id=cred['az_sub_id'],
                    key=cred['az_app_id'],
                    secret=cred['az_app_sec'])
    return az_obj


def az_nodes(c_obj):
    """Collect nodes from Azure and retreive details specific to Azure."""
    az_nodes = []
    az_nodes = c_obj.list_nodes()
    for node in az_nodes:
        node.cloud = "azure"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['location']
        node.size = node.extra['properties']['hardwareProfile']['vmSize']
        group_raw = node.id
        unnsc, group_end = group_raw.split("resourceGroups/", 1)
        group, unnsc = group_end.split("/", 1)
        node.group = group
    return az_nodes


def gcp_conn(cred):
    """Establish connection to Azure service."""
    driver = get_driver(Provider.GCE)
    gcp_pem = CONFIG_DIR + cred['gcp_pem_file']
    gcp_obj = driver(cred['gcp_svc_acct_email'],
                     gcp_pem,
                     project=cred['gcp_proj_id'])
    return gcp_obj


def gcp_nodes(c_obj):
    """Collect nodes from GCP and retreive details specific to GCP."""
    gcp_nodes = []
    gcp_nodes = c_obj.list_nodes()
    for node in gcp_nodes:
        node.cloud = "gcp"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['zone'].name
    return gcp_nodes


def ip_to_str(raw_ip):
    """Convert IP Address list to string or null."""
    if raw_ip:
        raw_ip = raw_ip[0]
    else:
        raw_ip = None
    return raw_ip


if __name__ == '__main__':
    main()
