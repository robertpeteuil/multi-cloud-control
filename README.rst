Unified CLI Utility for AWS, Azure and GCP Instance Control
===========================================================

MCC: Command-Line Instance Control for Top 3 Enterprise Cloud Providers
-----------------------------------------------------------------------

Multi-Cloud-Control is currently in alpha and runs in two modes:

- **mcc** - Text UI that lists all instances from AWS, Azure and GCP in formatted table

  - Accepts Commands to Start Nodes, Stop Nodes or Quit
  - Additional commands planned include: connect via ssh, image/snapshot nodes, and change nore configuration (hardware, disks, network)

- **mccl** - Display list of instances from all providers as table and exit

Support Systems
---------------

Python 2.7, 3.3, 3.4, 3.5

Platforms:

- Linux
- macOS (OS X)

Pre-Reqs
--------

This utility uses some Python libraries which may require compilation during the installation process.

RedHat / CentOS Based Systems

.. code:: shell

  sudo yum install gcc libffi-devel python-devel openssl-devel

Debian / Ubuntu Based Systems:

.. code:: shell

  sudo apt-get install gcc libssl-dev libffi-dev python-dev
  sudo apt-get install python3-dev  #  if using python3.x

Installation
------------

This utility can be installed with **pip**:

.. code:: shell

  sudo pip install mcc

Configuration
-------------

The first time the utility is executed:

- It creates the config directory **{HOME}/.cloud**
- It copies the sample config.ini file to the config dir
- Tells the user to add their credential information to config.ini

Notes while editing the config.ini file:

- be careful not to change the names of the keys (titles left of the '=' symbol)
- comment lines may be deleted (those beginning with #)

**config.ini sections**

.. code::

  [info]
  # example - connect to all three providers
  providers = aws,azure,gcp

  # the "providers" key specifies which cloud providers to work with
  # it may contain any subset or combination of "aws", "azure" and "gcp"
  # each provider listed must have a corresponding section of the same name
  #   the corresponding section contains the security credentials for that provider


**[aws] section** - specifies your AWS security credentials and default datacenter region. `Information on AWS Credentials <http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-set-up.html>`_


.. code::

  [aws]
  aws_access_key_id = EXCEWDYSWRP7VZOW4VAW
  aws_secret_access_key = CHVsdhV+YgBEjJuZsJNstLGgRY43kZggNHQEh/JK
  aws_default_region = us-west-1


**[azure] section** - specifies your Azure Tenant-ID, Subscription-ID, Application-ID and Application-Secret.  `Creating an Azure Service Principal <https://azure.microsoft.com/en-us/documentation/articles/resource-group-authenticate-service-principal>`_


.. code::

  [azure]
  az_tenant_id = a3b7de99-6c36-e71f-e7d7-c5a1eefd9c01
  az_sub_id = 2ac1b147-fdca-947c-4907-3f302a667100
  az_app_id = ee16ad1d-d266-bffa-031c-008ab40d971e
  az_app_sec = 22918C9e1cCC7665a+b3e4052f942630aE979CF68/v=


**[gcp] section** - specifies your Google Compute Service Account, the name of your access key (use JSON formatted key), and your Project ID.  `Information on Setting up Service Account Authentication <https://cloud.google.com/compute/docs/access/create-enable-service-accounts-for-instances>`_


.. code::

  [gcp]
  gcp_svc_acct_email = 37646997249-compute@developer.gserviceaccount.com
  gcp_pem_file = SampleProject-72fcfdb29717.json
  gcp_proj_id = sampleproject-634368

  # list the filename of the JSON key in this file
  # copy the file itself to the config directory: {HOME}/.cloud


Supported Platforms & Python Versions
-------------------------------------

Python 2.7, 3.3, 3.4, 3.5, 3.6

Platforms:

- Linux
- macOS (OS X)

Windows support is planned in the future
