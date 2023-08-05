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

import os
import sys
import shutil
from install_scripts.distros import Distros
from install_scripts.helper import process_call


def build_cpuminer_multi(distro: Distros, destination: str):
    """
    Builds cpuminer-multi and moves it to the location specified
    :param distro: The distribution for which to build cpuminer-multi
    :param destination: The destination to which to
                        save the built cpuminer-multi to
    :return: None
    """

    if distro == Distros.ARCH:
        distro.value["install"]([
            "git", "make", "gcc", "make", "autpoconf", "automake",
            "autogen", "curl", "jansson", "openssl"
        ])

    else:
        print("Building cpuminer-multi not supported on this distro")
        sys.exit(1)

    if os.path.isdir("cpuminer-multi"):
        shutil.rmtree("cpuminer-multi")

    process_call(["git", "clone",
                  "https://github.com/tpruvot/cpuminer-multi.git"])
    os.chdir("cpuminer-multi")
    process_call(["./build.sh"])
    os.chdir("..")
    os.rename("cpuminer-multi", destination)
