"""LICENSE
Copyright 2017 Hermann Krumrey <hermann@krumreyh.com>

This file is part of install-scripts.

install-scripts is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

install-scripts is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with install-scripts.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import sys
from install_scripts.distros import Distros
from install_scripts.arch import install_essentials
from install_scripts.auth import install_fingerprint_auth
from install_scripts.customization import install_themes
from install_scripts.cryptomining import build_cpuminer_multi
from install_scripts.hosts import block_reddit
from install_scripts.bashrc import base, add_nas_bashrc_lines


MACHINE_CONFIGS = {
    "x250": [
        # (install_essentials, (True,)),
        (install_fingerprint_auth, (Distros.ARCH,)),
        (install_themes, (Distros.ARCH,)),
        (block_reddit, ()),
        (base, (Distros.ARCH,)),
        (add_nas_bashrc_lines, (False,))
    ],
    "hermann-desktop": [
        (install_essentials, (True,)),
        (install_themes, (Distros.ARCH,)),
        (block_reddit, ()),
        (base, (Distros.ARCH,)),
        (add_nas_bashrc_lines, (True,))
    ],
    "freenas": [
        (base, (Distros.FREENAS,)),
    ],
    "ubuntu-server": [
        (base, (Distros.UBUNTU,)),
    ],
    "namibsun": [
        (base, (Distros.UBUNTU,)),
    ]
}


APPLICATION_CONFIGS = {
    "cpuminer-multi": [
        (build_cpuminer_multi, ())
    ]
}


def execute_config(entry: str):
    """
    Executes a configuration
    :param entry: The entry in the configuration to execute
    :return: None
    """

    if entry in MACHINE_CONFIGS:
        config = MACHINE_CONFIGS
    elif entry in APPLICATION_CONFIGS:
        config = APPLICATION_CONFIGS
    else:
        print("Invalid config entry")
        sys.exit(1)

    commands = config[entry]
    for command in commands:
        print(command)
        command[0](*command[1])
