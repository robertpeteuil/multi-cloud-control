Multi Cloud Control of AWS, Azure, GCP & AliCloud Instances
===========================================================

Unified Instance control across Enterprise Cloud Providers
----------------------------------------------------------

|PyPi release| |lang|
---------------------

Multi-Cloud-Control provides a single solution for controlling cloud VMs/Instances across AWS, Azure, GCP and Alibaba Cloud.  It displays a combined list of VM-instances across providers, and allows starting, stopping and making connections.  It's extremely useful for shell users who work in multi-cloud environments.

This utility can be executed with two different commands:

- ``mccl`` - runs in "List Mode", which displays a unified list of instances and their state across providers
- ``mcc`` - runs in "Command Mode", which displays a unified instance list and allows for command execution

``mccl``
--------

- ``mccl`` Displays a unified list of VM/instances and their parameters across providers

  - useful when quick access to information is needed; it displays a list of instances and their state and exits

**List Mode screenshot**


.. image:: https://user-images.githubusercontent.com/1554603/33449863-4b1e182a-d5c7-11e7-958e-a1fac2ec1ee5.png


``mcc``
-------

- ``mcc`` Displays a unified list of VM-Instances across providers and enables command execution

  - Designed for use when control of VM/instance is needed
  - After listing instances and command options, the authenticated connection to the provider is maintained, and it awaits user command selection
  - Supports commands for starting, stopping and connecting (via ssh)
  - Future commands may include: creating/deleting instances, changing configuration (hardware, disks, network), managing imaging/snapshots, managing disk/storage, add/remove to groups/clusters


**Command Mode screenshot**


.. image:: https://user-images.githubusercontent.com/1554603/33449859-47c4677e-d5c7-11e7-8974-9212c31e785f.png


Supported Python versions & Platforms
-------------------------------------

Python 2.7, 3.4, 3.5, 3.6, 3.7

Platforms:

- Linux
- macOS (OS X)
- Windows 10 - Linux Shells

Installation
------------

This utility can be installed with **pip**, **brew** or downloading the repo and running ``python setup.py install``.

Installing with Brew
--------------------

On macOS, this utility can be installed with `brew <https://brew.sh/>`_.  This simplifies the installation process and automatically installs the necessary Python libraries in a seperate virtual environment.

It can be installed via **brew** with the command:

.. code:: shell

  brew install robpco/tap/mcc

Installing with Pip
-------------------

This utility can be installed with **pip**:

.. code:: shell

  pip install --user mcc

Pip Installation Pre-Reqs
-------------------------

When installing with **pip**, the libraries used for secure authentication may require compilation during the installation process on some systems.  In order to successfully compile these dependencies, the following packages must be installed before installation:

**Installing Pre-Reqs on Debian / Ubuntu Based Systems:**

.. code:: shell

  sudo apt-get install gcc python-dev libssl-dev libffi-dev -y

**Installing Pre-Reqs on RedHat / CentOS Based Systems:**

.. code:: shell

  sudo yum install gcc python-devel openssl-devel libffi-devel -y

Configuration
-------------

The first time the utility is executed it performs the following tasks:

- Creates a config directory for ``mcc`` located at **$HOME/.cloud**
- Copies a sample configuration file, ``config.ini``, to the new dir
- Displays a message instructing the user to edit ``config.ini``

The `Wiki Configuration Page <https://github.com/robertpeteuil/multi-cloud-control/wiki/Configuration>`_ describes how to configure cloud provider accounts and add credentials to the ``config.ini`` file.

.. |PyPi release| image:: https://img.shields.io/pypi/v/mcc.svg
   :target: https://pypi.python.org/pypi/mcc

.. |lang| image:: https://img.shields.io/badge/language-python-3572A5.svg
   :target: https://github.com/robertpeteuil/multi-cloud-control

.. |Dependency| image:: https://gemnasium.com/badges/github.com/robertpeteuil/multi-cloud-control.svg
   :target: https://gemnasium.com/github.com/robertpeteuil/multi-cloud-control
