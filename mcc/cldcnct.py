"""Authenticate and get node objects from user-specified cloud providers.

License:

    MCC - Command-Line Instance Control for AWS, Azure and GCP.
    Copyright (C) 2017-2018  Robert Peteuil

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
monkey.patch_all()

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.common.types import InvalidCredsError
from libcloud.common.exceptions import BaseHTTPError
from requests.exceptions import SSLError
from mcc.confdir import CONFIG_DIR
import sys



def get_conns(cred, providers):
    """Collect node data asynchronously using gevent lib."""
    cld_svc_map = {"aws": conn_aws,
                   "azure": conn_az,
                   "gcp": conn_gcp}
    sys.stdout.write("\rEstablishing Connections:  ")
    sys.stdout.flush()
    busy_obj = busy_disp_on()
    conn_fn = [[cld_svc_map[x.rstrip('1234567890')], cred[x], x]
               for x in providers]
    cgroup = Group()
    conn_res = []
    conn_res = cgroup.map(get_conn, conn_fn)
    cgroup.join()
    conn_objs = {}
    for item in conn_res:
        conn_objs.update(item)
    busy_disp_off(dobj=busy_obj)
    sys.stdout.write("\r                                                 \r")
    sys.stdout.write("\033[?25h")  # cursor back on
    sys.stdout.flush()
    return conn_objs


def get_data(conn_objs, providers):
    """Refresh node data using existing connection-objects."""
    cld_svc_map = {"aws": nodes_aws,
                   "azure": nodes_az,
                   "gcp": nodes_gcp}
    sys.stdout.write("\rCollecting Info:  ")
    sys.stdout.flush()
    busy_obj = busy_disp_on()
    collec_fn = [[cld_svc_map[x.rstrip('1234567890')], conn_objs[x]]
                 for x in providers]
    ngroup = Group()
    node_list = []
    node_list = ngroup.map(get_nodes, collec_fn)
    ngroup.join()
    busy_disp_off(dobj=busy_obj)
    sys.stdout.write("\r                                                 \r")
    sys.stdout.write("\033[?25h")  # cursor back on
    sys.stdout.flush()
    return node_list


def get_conn(flist):
    """Call function for each provider."""
    cnodes = []
    cnodes = flist[0](flist[1], flist[2])
    return cnodes


def get_nodes(flist):
    """Call node collection function for each provider."""
    cnodes = []
    cnodes = flist[0](flist[1])
    return cnodes


def busy_disp_on():
    """Turn ON busy_display to show working statues."""
    p = gevent.spawn(busy_display)
    return p


def busy_disp_off(dobj):
    """Turn OFF busy_display to indicate completion."""
    dobj.kill(block=False)
    sys.stdout.write("\033[D \033[D")
    sys.stdout.flush()


def busy_display():
    """Display animation to show activity."""
    sys.stdout.write("\033[?25l")  # cursor off
    sys.stdout.flush()
    for x in range(1800):
        symb = ['\\', '|', '/', '-']
        sys.stdout.write("\033[D{}".format(symb[x % 4]))
        sys.stdout.flush()
        gevent.sleep(0.1)


def ip_to_str(raw_ip):
    """Convert IP Address list to string or null."""
    if raw_ip:
        return raw_ip[0]
    else:
        return None


def conn_aws(cred, crid):
    """Establish connection to AWS service."""
    driver = get_driver(Provider.EC2)
    try:
        aws_obj = driver(cred['aws_access_key_id'],
                         cred['aws_secret_access_key'],
                         region=cred['aws_default_region'])
    except SSLError as e:
        abort_err("\r SSL Error with AWS: {}".format(e))
    except InvalidCredsError as e:
        abort_err("\r Error with AWS Credentials: {}".format(e))
    return {crid: aws_obj}


def nodes_aws(c_obj):
    """Get node objects from AWS."""
    aws_nodes = []
    try:
        aws_nodes = c_obj.list_nodes()
    except BaseHTTPError as e:
        abort_err("\r HTTP Error with AWS: {}".format(e))
    aws_nodes = adj_nodes_aws(aws_nodes)
    return aws_nodes


def adj_nodes_aws(aws_nodes):
    """Adjust details specific to AWS."""
    for node in aws_nodes:
        node.cloud = "aws"
        node.cloud_disp = "AWS"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['availability']
        node.size = node.extra['instance_type']
        node.type = node.extra['instance_lifecycle']
    return aws_nodes


def conn_az(cred, crid):
    """Establish connection to Azure service."""
    driver = get_driver(Provider.AZURE_ARM)
    try:
        az_obj = driver(tenant_id=cred['az_tenant_id'],
                        subscription_id=cred['az_sub_id'],
                        key=cred['az_app_id'],
                        secret=cred['az_app_sec'])
    except SSLError as e:
        abort_err("\r SSL Error with Azure: {}".format(e))
    except InvalidCredsError as e:
        abort_err("\r Error with Azure Credentials: {}".format(e))
    return {crid: az_obj}


def nodes_az(c_obj):
    """Get node objects from Azure."""
    az_nodes = []
    try:
        az_nodes = c_obj.list_nodes()
    except BaseHTTPError as e:
        abort_err("\r HTTP Error with Azure: {}".format(e))
    az_nodes = adj_nodes_az(az_nodes)
    return az_nodes


def adj_nodes_az(az_nodes):
    """Adjust details specific to Azure."""
    for node in az_nodes:
        node.cloud = "azure"
        node.cloud_disp = "Azure"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['location']
        node.size = node.extra['properties']['hardwareProfile']['vmSize']
        group_raw = node.id
        unnsc, group_end = group_raw.split("resourceGroups/", 1)
        group, unnsc = group_end.split("/", 1)
        node.group = group
    return az_nodes


def conn_gcp(cred, crid):
    """Establish connection to GCP."""
    gcp_auth_type = cred.get('gcp_auth_type', "S")
    if gcp_auth_type == "A":  # Application Auth
        gcp_crd_ia = CONFIG_DIR + ".gcp_libcloud_a_auth." + cred['gcp_proj_id']
        gcp_crd = {'user_id': cred['gcp_client_id'],
                   'key': cred['gcp_client_sec'],
                   'project': cred['gcp_proj_id'],
                   'auth_type': "IA",
                   'credential_file': gcp_crd_ia}
    else:  # Service Account Auth
        gcp_pem = CONFIG_DIR + cred['gcp_pem_file']
        gcp_crd_sa = CONFIG_DIR + ".gcp_libcloud_s_auth." + cred['gcp_proj_id']
        gcp_crd = {'user_id': cred['gcp_svc_acct_email'],
                   'key': gcp_pem,
                   'project': cred['gcp_proj_id'],
                   'credential_file': gcp_crd_sa}
    driver = get_driver(Provider.GCE)
    try:
        gcp_obj = driver(**gcp_crd)
    except SSLError as e:
        abort_err("\r SSL Error with GCP: {}".format(e))
    except (InvalidCredsError, ValueError) as e:
        abort_err("\r Error with GCP Credentials: {}".format(e))
    return {crid: gcp_obj}


def nodes_gcp(c_obj):
    """Get node objects from GCP."""
    gcp_nodes = []
    try:
        gcp_nodes = c_obj.list_nodes(ex_use_disk_cache=True)
    except BaseHTTPError as e:
        abort_err("\r HTTP Error with GCP: {}".format(e))
    gcp_nodes = adj_nodes_gcp(gcp_nodes)
    return gcp_nodes


def adj_nodes_gcp(gcp_nodes):
    """Adjust details specific to GCP."""
    for node in gcp_nodes:
        node.cloud = "gcp"
        node.cloud_disp = "GCP"
        node.private_ips = ip_to_str(node.private_ips)
        node.public_ips = ip_to_str(node.public_ips)
        node.zone = node.extra['zone'].name
    return gcp_nodes


def abort_err(messg):
    """Print Error Message and Exit."""
    print(messg)
    print("\033[?25h")
    sys.exit()
