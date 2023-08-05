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


from typing import List
from install_scripts.helper import process_call


def install_packages(packages: List[str]):
    """
    Installs packages on ubuntu linux
    :param packages: The packages to install
    :return: None
    """
    process_call(["sudo", "apt", "update"])

    for package in packages:
        process_call(["sudo", "apt", "install", package, "-y"])


def install_essentials(desktop: bool = False):
    """
    Installs essential packages
    :param desktop: Specifies if this is for a desktop system or not
    :return: None
    """
    packages = ["git", "curl", "wget", "htop"]
    if desktop:
        packages += []

    install_packages(packages)
