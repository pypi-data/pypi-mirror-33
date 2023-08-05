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


def install_themes(distro: Distros):
    """
    Install numix themes
    :param distro: The distro for which to install
    :return: None
    """

    if distro == Distros.ARCH:
        distro.value["install"](["numix-icon-theme-git", "arc-gtk-theme"])
    else:
        print("This distro is not supported")
        sys.exit(1)

    print("Manual configuration:")
    print("Set Window Borders to Arc-Darker")
    print("Set Icons to Numix")
    print("Set Controls to Arc-Dark")
    print("Set Desktop to Arc-Dark")
