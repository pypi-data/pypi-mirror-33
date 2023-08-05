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
from subprocess import Popen
from install_scripts.distros import Distros
from install_scripts.helper import process_call


def install_fingerprint_auth(distro: Distros):
    """
    Installs fprintd and sets up fingerprint authentification
    :param distro: The distro for which to install fprintd
    :return: None
    """

    if distro == Distros.ARCH:

        # Currently, there's a bug with the newest fprintd causing
        # the program to crash while enrolling the fingerprints
        # distro.value["install"](["fprintd"])

        # Use older versions instead
        fprintd = "https://archive.archlinux.org/packages/f/fprintd/" \
                  "fprintd-0.7.0-1-x86_64.pkg.tar.xz"
        libfprint = "https://archive.archlinux.org/packages/l/libfprint/" \
                    "libfprint-0.7.0-1-x86_64.pkg.tar.xz"
        process_call(["wget", fprintd])
        process_call(["wget", libfprint])
        process_call(["sudo", "pacman", "-U", "--noconfirm",
                      fprintd.rsplit("/", 1)[1],
                      libfprint.rsplit("/", 1)[1]])
        os.remove(fprintd.rsplit("/", 1)[1])
        os.remove(libfprint.rsplit("/", 1)[1])

    else:
        print("This distro is not supported")
        sys.exit(1)

    print("Enrolling Fingers:")
    print("Right Index Finger:")
    Popen(["fprintd-enroll"]).wait()
    print("Right Middle Finger:")
    Popen(["fprintd-enroll", "-f", "right-middle-finger"]).wait()
    Popen("sudo sed -i '2iauth      sufficient pam_fprintd.so' /etc/pam.d/*",
          shell=True).wait()
