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
import os
import sys
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
# from pprint import pprint

__version__ = "0.0.14"
cred = {}


def main():
    """Retreive and display instance data then process commands."""
    providers = read_config()

    nodes = collect_data(providers)

    disp.print_list_table(nodes)

    # pprint(nodes)

    # FLAT LIST TABLES (old)
    # disp.print_table(nodes)
    # table with indexed dict
    # disp.print_indx_table(nodes)


def collect_data(providers):
    """Orchestrate collection of node data from all providers with a pool."""
    cld_svc_map = {"aws": collect_aws_nodes,
                   "azure": collect_az_nodes,
                   "gcp": collect_gcp_nodes}
    services = []
    for item in providers:
        services.append(cld_svc_map[item])
    # pool = Pool()
    pool = Pool(4)
    result = {}
    nodes = []
    for i, item in enumerate(services):
        result[i] = pool.apply_async(item, [cred])
    for i in result:
        nodes.append(result[i].get(timeout=9))
    # nodes = pool.map(get_nodes, services)
    pool.close()
    pool.join()
    del pool
    return nodes


def get_nodes(funcnm):
    """Call appropriate function for provider and retreive nodes."""
    pool = ThreadPool(6)
    results = []
    results.append(pool.apply_async(funcnm, [cred]))
    pool.close()
    pool.join()
    # nodes = funcnm(cred)
    return results
    # return nodes


def read_config():
    """Read config file and gather credentials."""
    global cred
    config_file = (u"{0}config.ini".format(CONFIG_DIR))
    if not os.path.isfile(config_file):
        make_config(config_file)
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    providers = [e.strip() for e in (config['info']['providers']).split(',')]
    for item in providers:
        cred.update(dict(list(config[item].items())))
    return providers


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


def collect_aws_nodes(cred):
    """Collect nodes from AWS and retreive details specific to AWS."""
    aws_nodes = []
    driver = get_driver(Provider.EC2)
    aws_obj = driver(cred['aws_access_key_id'],
                     cred['aws_secret_access_key'],
                     region=cred['aws_default_region'])
    aws_nodes = aws_obj.list_nodes()
    for node in aws_nodes:
        node.cloud = "aws"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['availability']
        node.size = node.extra['instance_type']
        node.type = node.extra['instance_lifecycle']
    return aws_nodes


def collect_az_nodes(cred):
    """Collect nodes from Azure and retreive details specific to Azure."""
    az_nodes = []
    driver = get_driver(Provider.AZURE_ARM)
    az_obj = driver(tenant_id=cred['az_tenant_id'],
                    subscription_id=cred['az_sub_id'],
                    key=cred['az_app_id'],
                    secret=cred['az_app_sec'])
    az_nodes = az_obj.list_nodes()
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


def collect_gcp_nodes(cred):
    """Collect nodes from GCP and retreive details specific to GCP."""
    gcp_nodes = []
    driver = get_driver(Provider.GCE)
    gcp_pem = CONFIG_DIR + cred['gcp_pem_file']
    gcp_obj = driver(cred['gcp_svc_acct_email'],
                     gcp_pem,
                     project=cred['gcp_proj_id'])
    gcp_nodes = gcp_obj.list_nodes()
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
