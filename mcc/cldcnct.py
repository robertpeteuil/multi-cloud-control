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
from builtins import range
from gevent.pool import Group
from gevent import monkey
import gevent
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.common.types import InvalidCredsError
from mcc.confdir import CONFIG_DIR
import sys
from requests.exceptions import SSLError
monkey.patch_all()


def collect_data(cred, providers):
    """Collect node data asyncronously using gevent lib."""
    cld_svc_map = {"aws": get_aws,
                   "azure": get_az,
                   "gcp": get_gcp}
    # turn on display-indicator to indicated working
    sys.stdout.write("\rAuthentication & Node Retrieval:  ")
    sys.stdout.flush()
    busy_obj = busy_disp_on()
    collec_fn = []
    for item in providers:
        collec_fn.append([cld_svc_map[item], cred])
    # fetch nodes
    node_list = []
    group = Group()
    node_list = group.map(get_conn_new, collec_fn)
    group.join()
    # turn off display-indicator that indicated working
    busy_disp_off(dobj=busy_obj)
    sys.stdout.write("\r                                                 \r")
    sys.stdout.write("\033[?25h")  # turn cusor back on
    sys.stdout.flush()
    return node_list


def get_conn_new(flist):
    """Call function for each provider."""
    cnodes = []
    cnodes = flist[0](flist[1])
    return cnodes


def busy_disp_on():
    """Turn ON busy_display to show working statues."""
    p = gevent.spawn(busy_display)
    return p


def busy_disp_off(dobj):
    """Turn OFF busy_display to show working statues."""
    dobj.kill(block=False)
    sys.stdout.write("\033[D \033[D")
    sys.stdout.flush()


def busy_display():
    """Display animation to show activity."""
    sys.stdout.write("\033[?25l")  # turn cursor off
    sys.stdout.flush()
    for x in range(999):
        symb = ['\\', '|', '/', '-']
        sys.stdout.write("\033[D{}".format(symb[x % 4]))
        sys.stdout.flush()
        gevent.sleep(0.1)


def ip_to_str(raw_ip):
    """Convert IP Address list to string or null."""
    if raw_ip:
        raw_ip = raw_ip[0]
    else:
        raw_ip = None
    return raw_ip


def get_aws(cred):
    """Establish connection to AWS service."""
    driver = get_driver(Provider.EC2)
    try:
        aws_obj = driver(cred['aws_access_key_id'],
                         cred['aws_secret_access_key'],
                         region=cred['aws_default_region'])
    except SSLError:
        print("\r SSL Error with AWS               ", end='')
        return []
    except InvalidCredsError:
        print("\r Error with AWS Credentials       ", end='')
        return []
    gevent.sleep(0)
    aws_nodes = []
    aws_nodes = aws_obj.list_nodes()
    # gevent.sleep(0)
    aws_nodes = adj_nodes_aws(aws_nodes)
    return aws_nodes


def adj_nodes_aws(aws_nodes):
    """Retreive details specific to AWS."""
    for node in aws_nodes:
        node.cloud = "aws"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['availability']
        node.size = node.extra['instance_type']
        node.type = node.extra['instance_lifecycle']
    return aws_nodes


def get_az(cred):
    """Establish connection to Azure service."""
    driver = get_driver(Provider.AZURE_ARM)
    try:
        az_obj = driver(tenant_id=cred['az_tenant_id'],
                        subscription_id=cred['az_sub_id'],
                        key=cred['az_app_id'],
                        secret=cred['az_app_sec'])
    except SSLError:
        print("\r SSL Error with Azure             ", end='')
        return []
    except InvalidCredsError:
        print("\r Error with Azure Credentials     ", end='')
        return []
    gevent.sleep(0)
    az_nodes = []
    az_nodes = az_obj.list_nodes()
    # gevent.sleep(0)
    az_nodes = adj_nodes_az(az_nodes)
    return az_nodes


def adj_nodes_az(az_nodes):
    """Retreive details specific to Azure."""
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


def get_gcp(cred):
    """Establish connection to GCP."""
    driver = get_driver(Provider.GCE)
    gcp_pem = CONFIG_DIR + cred['gcp_pem_file']
    try:
        gcp_obj = driver(cred['gcp_svc_acct_email'],
                         gcp_pem,
                         project=cred['gcp_proj_id'])
    except SSLError:
        print("\r SSL Error with GCP               ", end='')
        return []
    except InvalidCredsError:
        print("\r Error with GCP Credentials       ", end='')
        return []
    gevent.sleep(0)
    gcp_nodes = []
    gcp_nodes = gcp_obj.list_nodes(ex_use_disk_cache=True)
    # gevent.sleep(0)
    gcp_nodes = adj_nodes_gcp(gcp_nodes)
    return gcp_nodes


def adj_nodes_gcp(gcp_nodes):
    """Retreive details specific to GCP."""
    for node in gcp_nodes:
        node.cloud = "gcp"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['zone'].name
    return gcp_nodes
