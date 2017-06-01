Unified CLI Utility for AWS, Azure and GCP Instance Control
===========================================================

MCC: Command-Line Instance Control for Top 3 Enterprise Cloud Providers
-----------------------------------------------------------------------

The Multi-Cloud-Control utility, mcc, is currently in alpha and allows
listing basic information from instances on AWS, Azure and GCP in one report
with one simple command: **mcc**.

Planned future enhancements:
- start and stop instances
- connect to instances via ssh
- image / snapshot instances
- change instance configuration (disk, network, HW)

Installation
------------

This utility can be installed with **pip**:

.. code:: shell

  pip install mcc

Configuration
-------------

The first time the utility is executed, it:

- creates its configuration directory **{HOME}/.cloud**
- copies a sample config.ini file into that directory
- Informs the user to edit and their credential information to that file
- while editing the config.ini file

  - be careful not to change the names of the keys - the titles left of the '=' symbol
  - comment lines (those beginning with #) may be deleted

**config.ini sections**

.. code::

  [info]
  # example - connect to all three providers
  providers = aws,azure,gcp

  # the "providers" key specifies which cloud providers to work with
  # the list can contain any subset or combination of "aws", "azure" and "gcp"
  # each provider listed must have a corresponding section of the same name
  #   the corresponding section contains the security credentials for that provider


**[aws] section** - specifies your AWS security credentials and our default datacenter region. `Information on AWS Credentials <http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-set-up.html>`_


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


**[gcp] section** - specifies your Google Compute Service Account, the name of your private key (use a JSON formatted key), and your Project ID.  `Information on Setting up Service Account Authentication <https://cloud.google.com/compute/docs/access/create-enable-service-accounts-for-instances>`_


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
