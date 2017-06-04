"""Connect Authenticate and get node objects from AWS, Azure and GCP.

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
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from mcc.confdir import CONFIG_DIR
from multiprocessing import Process
from multiprocessing import Pool
from multiprocessing import cpu_count
import sys
import os


def begin_collect(cred, providers):
    """Check the host machine and determine collection function to use."""
    if os.uname()[4].startswith("arm"):
        collfunc = collect_data
    elif cpu_count() == 1:
        collfunc = collect_data
    else:
        collfunc = collect_data_mt
    (node_list, conn_objs) = collfunc(cred, providers)
    return (node_list, conn_objs)


def collect_data(cred, providers):
    """Orchestrate collection of node data from all providers with a pool."""
    cld_svc_map = {"aws": [aws_conn, aws_nodes],
                   "azure": [az_conn, az_nodes],
                   "gcp": [gcp_conn, gcp_nodes]}
    conn_objs = []
    for item in providers:
        conn_objs.append(cld_svc_map[item][0](cred))
    node_list = []
    for i, object in enumerate(conn_objs):
        node_list.append(cld_svc_map[providers[i]][1](object))
    return (node_list, conn_objs)


def collect_data_mt(cred, providers):
    """Orchestrate collection of node data from all providers with a pool."""
    cld_svc_map = {"aws": [aws_conn, aws_nodes],
                   "azure": [az_conn, az_nodes],
                   "gcp": [gcp_conn, gcp_nodes]}
    # turn on display-indicator to indicated working
    busy_obj = busy_disp_on()
    pool = Pool(pool_sizer(), maxtasksperchild=1)
    conns = {}
    for item in providers:
        # c = pool.apply_async(get_conn, [cld_svc_map[item][0], cred])
        c = pool.apply_async(cld_svc_map[item][0], [cred])
        conns[item] = c
    # Gather connection-objects as they become available, then
    #   immediately start sync process with each object to get nodes from it
    count = len(providers)
    conn_objs = {}
    node_r = {}
    while count > 0:
        for k, v in conns.items():
            if v.ready():
                conn_objs[k] = v.get()
                # node_r[k] = pool.apply_async(get_nodes, [cld_svc_map[k][1],
                #                                          conn_objs[k]])
                node_r[k] = pool.apply_async(cld_svc_map[k][1],
                                             [conn_objs[k]])
                del conns[k]
                count -= 1
    # Read node-result objects as they become available, then
    #   combine them into a nested list sorted by provider in the order
    #   they are listed in providers (from config.ini)
    node_list = results_to_node_list(providers, node_r)
    # cleanup multiprocessing pool
    pool.close()
    pool.join()
    del pool
    # turn off display-indicator that indicated working
    busy_disp_off(dobj=busy_obj)
    return (node_list, conn_objs)


def pool_sizer():
    """Determine number of processes to create based on CPU."""
    cc = cpu_count()
    ctp = {16: 12, 8: 6, 4: 3, 2: 2, 1: 1}
    procs = ctp.get(cc, cc - 1)
    return procs


def busy_disp_on():
    """Turn ON busy_display to show working statues."""
    p = Process(target=busy_display, name='delay-indicator')
    p.start()
    return p


def busy_disp_off(dobj):
    """Turn OFF busy_display to show working statues."""
    dobj.terminate()
    sys.stdout.write("\033[A\n")
    sys.stdout.write("\033[?25h")  # turn cusor back on
    sys.stdout.flush()


def busy_display():
    """Display animation while loading."""
    from time import sleep
    sys.stdout.write("\033[?25l")  # turn cursor off
    sys.stdout.flush()
    for x in range(100):
        symb = ['\\', '|', '/', '-']
        sys.stdout.write('\rAuthentication & Node Retrieval: %s'
                         % (symb[x % 4]))
        sys.stdout.flush()
        sleep(0.1)


def results_to_node_list(providers, node_r):
    """Convert async result objs to node_list."""
    node_list = []
    node_dict = {}
    count = len(providers)
    # process node results as they become available into dict
    while count > 0:
        for k, v in node_r.items():
            if node_r[k].ready():
                # node_list.append(node_r[k].get())
                node_dict[k] = node_r[k].get()
                del node_r[k]
                count -= 1
    # create list from dict in the "provider" order
    for item in providers:
        node_list.append(node_dict[item])
    return node_list


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
