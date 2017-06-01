"""Calculate the dir contianing configuation information."""

import os
from os.path import expanduser

home_dir = expanduser("~")
os_spec = {"nt": "\\"}
fs_sep = os_spec.get(os.name, "/")
CONFIG_DIR = (u"{0}{1}.cloud{1}".format(home_dir, fs_sep))
